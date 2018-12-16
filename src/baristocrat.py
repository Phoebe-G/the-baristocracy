import subprocess
from Xlib import display
from Xlib.ext import randr
from io import TextIOWrapper
import os, tempfile
import select
from time import sleep
import shutil
import errno
import posix
#import ptvsd

#ptvsd.enable_attach("testing", address = ('localhost', 3000))
#ptvsd.wait_for_attach()

monitors = []

def get_monitors():
    """ Checks xrandr for connected outputs, finds their position and dimensions,
        queries bspwm for list of available desktops. """

    _display = display.Display()
    _s = _display.screen()
    _w = _s.root.create_window(0, 0, 1, 1, 1, _s.root_depth)
    _resources = randr.get_screen_resources(_w)._data

    def monitor_info(crtc):
        _crt = _display.xrandr_get_crtc_info(crtc, _resources["config_timestamp"])._data
        if len(_crt["outputs"]) == 1:
            _info = _display.xrandr_get_output_info(
                _crt["outputs"][0],
                _resources["config_timestamp"]
                )._data

            _desktops = subprocess.run(
                ["/usr/bin/bspc", "query", "-D", "-m", _info["name"]],
                universal_newlines=True, stdout=subprocess.PIPE
                ).stdout.strip()

            _current = subprocess.run(
                ["/usr/bin/bspc", "query", "-D", "-m", _info["name"], "-d", ".focused"],
                universal_newlines=True, stdout=subprocess.PIPE
                ).stdout.strip()

            _bspc_id = subprocess.run(
                ["/usr/bin/bspc", "query", "-M", "-m", _info["name"]],
                universal_newlines=True, stdout=subprocess.PIPE
                ).stdout.strip()

            return {
                "name": _info["name"],
                "monitor_id": _bspc_id,
                "x": _crt["x"],
                "width": _crt["width"],
                "desktops": list(filter(None, _desktops.split("\n"))),
                "current": _current
            }
        return None

    return list(filter(None, list(map(monitor_info, _resources["crtcs"]))))

def desktop_event_parser():
    """ returns an event parser that translates bspc subscribe event messages
        into dicts with the values mapped to their bspc-documented names.
        - events with unhandled types return None """

    def parse_desktop_event(evt):
        """ event-to-dict mapper """
        tokens = evt.split()

        print("Event: {}".format(evt))
        events = {
            "desktop_focus": {
                "event": tokens[0]      if 0 < len(tokens) else None,
                "monitor_id": tokens[1] if 2 < len(tokens) else None,
                "desktop_id": tokens[2] if 2 < len(tokens) else None
            },
            "desktop_add": {
                "event": tokens[0]          if 0 < len(tokens) else None,
                "desktop_id": tokens[2]     if 2 < len(tokens) else None,
                "desktop_name":  tokens[3]  if 3 < len(tokens) else None,
                "monitor_id": tokens[1]     if 1 < len(tokens) else None
            },
            "desktop_remove": {
                "event": tokens[0]          if 0 < len(tokens) else None,
                "monitor_id": tokens[1]     if 1 < len(tokens) else None,
                "desktop_id":  tokens[2]  if 2 < len(tokens) else None
            },
            "desktop_transfer": {
                "event": tokens[0] if 0 < len(tokens) else None,
                "source_monitor": tokens[1] if 1 < len(tokens) else None,
                "desktop_id": tokens[2] if 2 < len(tokens) else None,
                "target_monitor": tokens[3] if 3 < len(tokens) else None
            }
        }

        return events.get(tokens[0], None)

    return parse_desktop_event

def updateMonitor(monitor):
    if monitor is not None and monitor["bar_proc"].poll() is None:
        if "bar_proc" in monitor and monitor["bar_proc"].poll() is None:
            with open(monitor["input_pipe"], "w") as f:
                f.write("{} {}\n".format(str(len(monitor["desktops"])),
                                            str(monitor["desktops"].index(monitor["current"]) + 1)
                                        ))
                f.close()

def desktop_event_handler(monitors):
    """ returns a handler object that can process various parsed bspc desktop events """

    def unhandled_event(evt):
        """ stub for parsed but unhandled events """
        print("Unhandled bspc desktop event {}".format(evt.event))

    def focus_event(evt):
        """ bspc desktop_focus event handler
            - checks whether the focus event implies a desktop change on one of the screens.
            - updates our internal screen mapping to reflect new current desktop """

        monitor = next((monitor for
                        monitor in monitors
                        if monitor["monitor_id"] == evt["monitor_id"]
                       ), None)

        if monitor["current"] != evt["desktop_id"]:
            monitor["current"] = evt["desktop_id"]
            updateMonitor(monitor)

    def desktop_add_event(evt):
        monitor = next((monitor for
                        monitor in monitors
                        if monitor["monitor_id"] == evt["monitor_id"]
                       ), None)
        print("Add a desktop: {}".format(evt))
        print("To monitor: {}".format(monitor))
        monitor["desktops"].append(evt["desktop_id"])
        updateMonitor(monitor)

    def desktop_remove_event(evt):
        monitor = next((monitor for
                        monitor in monitors
                        if monitor["monitor_id"] == evt["monitor_id"]
                       ), None)

        monitor["desktops"].remove(evt["desktop_id"])

        if(monitor["current"] == evt["desktop_id"]):
            currentMonitors = get_monitors()

            m = next((m for
                        m in currentMonitors
                        if m["monitor_id"] == monitor["monitor_id"]
                        ), None)

            if m:
                monitor["current"] = subprocess.run(
                                    ["/usr/bin/bspc", "query", "-D", "-m", monitor["name"], "-d", ".focused"],
                                    universal_newlines=True, stdout=subprocess.PIPE
                                    ).stdout.strip()
                updateMonitor(monitor)

    def desktop_transfer_event(evt):
        desktop_remove_event({
            "event": None,
            "monitor_id": evt["source_monitor"],
            "desktop_id": evt["desktop_id"]
        })

        desktop_add_event({
            "event": None,
            "desktop_id": evt["desktop_id"],
            "desktop_name": None,
            "monitor_id": evt["target_monitor"]
        })

    def handle_desktop_event(evt):
        """ event-to-func mapper """
        if evt is None:
            return
        events = {
            "desktop_focus": focus_event,
            "desktop_add": desktop_add_event,
            "desktop_remove": desktop_remove_event,
            "desktop_transfer": desktop_transfer_event
        }
        print("event: {}".format(evt))
        events.get(evt["event"], unhandled_event)(evt)

    return handle_desktop_event

def startMonitorBars(tmpdir, monitors):
    for monitor in monitors:
        monitor["input_pipe"] = os.path.join(tmpdir, "barscript-{}-in".format(monitor["name"]))
        monitor["bar_proc"] = subprocess.Popen(["../bin/barscript",
                                           monitor["name"],
                                           str(monitor["width"]),
                                           str(monitor["x"]),
                                           str(len(monitor["desktops"])),
                                           str(monitor["desktops"]
                                               .index(monitor["current"]) + 1),
                                           str(monitor["input_pipe"])
                                          ], universal_newlines=True)

def startWMListener(monitors):
    desktop_event = subprocess.Popen(["/usr/bin/bspc", "subscribe", "desktop"], bufsize=1, universal_newlines=True, stdout=subprocess.PIPE)
    desktop_event_poll = select.poll()
    desktop_event_poll.register(desktop_event.stdout, select.POLLIN)

    print("listening for bscp desktop events")
    parse_event = desktop_event_parser()
    handle_event = desktop_event_handler(monitors)

    while desktop_event.poll() is None:
        poll_result = desktop_event_poll.poll(0)

        if poll_result:
            _evt = parse_event(desktop_event.stdout.readline().strip())
            handle_event(_evt)

        for monitor in monitors:
            if monitor["bar_proc"].poll() is not None:
                desktop_event.kill()
                break

        sleep(0.025)


def start():
    """ Opens a bar script on each monitor and starts listening to bspc for desktop events. """
    monitors = get_monitors()

    tmpdir = tempfile.mkdtemp()
    inputFile = tempfile.NamedTemporaryFile(mode="w+b", buffering=-1, prefix="baristocrat-", suffix="-in")

    startMonitorBars(tmpdir, monitors)

    startWMListener(monitors)

    for monitor in monitors:
        monitor["bar_proc"].kill()
        #os.remove(monitor["input_pipe"])

    #os.rmdir(tmpdir)
    #shutil.rmtree(tmpdir)

if __name__ == '__main__':
    start()
