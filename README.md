(warning this readme may contain occasional reckless use of hyperbole, cynicism and satire, [read at your own risk](https://en.wikipedia.org/wiki/The_Death_of_the_Author).)

# The Baristocracy

( **(WIP)** set of userspace scripts intended for desktop linux use, current (known & assumed) reqs: bash, python 3 + libs, xorg, **bspwm**(+bspc), **ocelot-dzen**, terminus font + possibly several more userland tools for providing notifications (when enabled.. which they aren't right now) etc. And to be absolutely transparent I have only used this on a first gen X1 Yoga.)

## What it is

A "bartending"* script intended to manage many of the duties required to maintain a consistent UI/UX on bspwm running on convertible / dockable devices like the X1 Yoga and any other quirky setups that requires a bit more hand holding than the usual static (or pain in the arse) configurations available to most WM users.

My intention when first writing these scripts was to build something I could iterate on quickly with the intention of eventually shoring things up and living with this thing for a long time. I wanted to keep the memory and CPU footprint as low as possible - if something is chewing up your battery life I don't want it to be baristocrat, it better be a naively written plugin at worst, dig? I found a lot of bar scripts were hungry by default, polling all the things every time and in lockstep with whatever speed you want your clock to update. I decided it was time to start learning more about how scripts work, how process management works, how to write polite bash scripts etc.

Of course.. this has always been just like, my dirty little secret, until now, so I've cut corners everywhere. Eg I've been content to just re-launch stuff by hand etc so at the time of writing, right-clicking on a bar will crash baristocrat and I have to restart it. And I do, multiple times a day. Because I haven't fixed a litany of issues with even this early incarnation of the code.

Still, it's got some things going for it-

- baristocrat.py is the bar managing program, it detects the number of monitors and their geometry to draw a dzen bar at the top of each one
- if any part of the application crashes, the whole thing cleans up after itself leaving no orphaned processes or bars with no bar data being fed into their pipes etc
  - this is why in the above example, with my poorly constructed dzen config, a crash on one bar takes down the whole application _by design..._ I endevour as much as possible to make this robust and because I haven't gotten around to implementing a per-bar restart handler yet, the application self terminates completely saving me the hassle of cleaning it up in a semi-crashed state
  - point is, as far as I know, this bunch of bash scripts being orchestrated by a python pipe manager doesn't leak processes despite needing to support a lot of arbitrary child process spawning by design

## "bartending"* script? (the story so far, for the uninitiated and/or truly lost..)

### DEs vs VMs

(circa 2018CE)

If you're unfamiliar with the concept of tiling Window Managers (WMs,) bars and bar scripts might be unfamiliar to you as well. That's okay. I'm not sure how you ended up here but never the less, here we are. And since, if you don't know why you're here, but you're here anyway, I've got you now- you're just wasting time, so here let me indulge both of us in some rambling backstory and world building for this bit of shitty software.

-------

The average desktop/laptop/doin'-human-things Linux user, who wants to use a graphical desktop environment like the usual GUI (s)hells provided by OSes like Windows and OSX, will generally install a Linux distribution that ships a flagship desktop environment, maybe a choice of them. These desktop environments are all that and a dime sack- they incorporate workspace management, providing you with a clock.. uh.. packaging up note taking applications.. give you .. um, I dunno, a start menu? You know. The place where windows are drawn and controlled.

Desktop environments are pretty cool and generally good. For example the build of Gnome (I think it is? on Wayland even?) that Fedora most recently ships with at time of writing handles mixed DPI displays almost perfectly (very rare at this historical juncture,) along with its seamless handling of docking and undocking laptops from multimonitor configurations, handling the screen orientation changes by reading the accelerometer in a convertible laptop, stuff like that made it a clear winner for somebody wanting an out-of-the-box "wow this is better than I imagined" experience" on a modern convertible laptop intended to be used in every feasible configuration.

Desktop environments with their integrated notification systems, bundled package managers and all that good shit intended to give you enough control to make sure your Linux is still up to date, find new software and generally let you do computer user type things.

...

Never-the-less some people like to do things the hard way. So here I am, several years after first buying this damn laptop and having the bright idea of "making it sooo coool mannn" **STILL** trying to coerce my computer into just bloody behaving itself nicely for once. A window manager just like.. draws windows, basically. Draws, positions and perhaps depending on the window manager, gives control over application window grouping, position, etc. WMs don't provide much, but they do provide a couple of really important things- a sense of superiority over everyone who isn't using exactly the best one according to you and, generally, the sort of compartmentalisation of duties that old Linux heads generally expect. You know what they say, "do one thing and do it well."

As I implied, it's several years later. Still chasing conveniences in UX that I could have had on day one if I'd just accepted my fate and installed a Redhat distro. But then I wouldn't be able to tell you I use Arch or (hypothetically) post sexy screenshots to `r/unixporn` so really what is a nerd-hermit to do? I could justify to you fifty which-ways why I don't want to use a Redhat backed distro, or how I would prefer if history had gone a different route at many different points in living memory. But here we are with the worlds' largest intelligence agencies contributing to our counter-culture OS and ecosystem and, well, it ain't counter-culture anything anymore. These are the engines of business now. I..

I prefer to keep my personal Linux experience.. personal. I don't _want_ homgeneity in all our experiences with and interfaces into this dope operating system. Sure the NSA being in bed with Redhat is _probably_, actually, about improving kernel security layers and tooling and the changes are _probably_ benign  and the systemd mafia working at Redhat _probably_ have everyone's best intentions at heart, but.. whatever. All these machines are basically fundamentally compromised anyway so all those arguments are ultimately a bit of a cop-out. I choose the dumbshit bleeding edge distro and I just want a nice personal user interface taylored to my particular tastes.

I want the future UXes promised in sci-fi on our computers today. Those dope tablets all the rubes are using in Westworld (the TV series) to run the park? Have you SEEN how sick those UIs look? Terrible ergonomics I'm sure- but why isn't my linux like that? That's the question, along with the purchase of a convertible laptop, that ultimately lead to this half arsed project and now, repository. There's probably more lines of text in this self indulgent ramble than there are in the code I will be checking in when I'm done and get over my inferiority complex long enough to push to remote.


### Bars, bar scripts and bartending

It could be easy to miss if you're wading through this this self indulgent waffle, but I mentioned that WMs don't really do much. You can do your own research if you care about the scope of what things calling themselves Window Managers provide, it's varied, there are many philosophies.

Commonly though, window managers don't come with the equivalent of the Windows (tm) Start Bar (tm) or the menu bar on OSX (and Gnome.. ) and it's up to the user to pick an application to fill that role for them. The choices people make as to whether and how to replace that "ubiquitous bar on the screen" experience depend from person to person. Common amongst the _"do one thing and do it well"_ set are bars and bar scripts. Some absolute mind blowing alternatives to the norm exist if you care to look for them and figure out how they're made.

You never know, Apple's idea of your ideal man-machine interface might not be as good of a fit for how your brain works or your workflows or the multiple discrete uses you put your computer to as something you build from nothing based just on exploring "what if there was nothing" and going from there. Generally since linux systems are build from a series of simple building blocks (that each do one thing well) it is fairly trivial for a novice to customise their entire desktop experience including the very paradigms of how, when and where windows and notifications are delivered to the user.

Shouts out to [wmutils](https://github.com/wmutils/) for really stripping away the WM concept back to basically a set of [terminal tools](https://github.com/wmutils/core) for live-managing the layout of windows. Of course in practice from what I've seen you end up writing a lot of scripts to automate things, but they're your scripts, they do what you want and nothing more. The complexity and functionality of the graphical shell is more or less entirely defined by the user and it isn't gatekept behind some arcane server/API architecture. If you want to have your programs launched and arranged a certain way on your screen because it's 8:55am on a Monday morning, you can do that.

Anyway, I digress. A bar just renders "a bar" somewhere on the screen, with appropriate hinting to ensure that most window managers will recognise that it's supposed to stick to the side of a screen and/or be on top of other windows. What do I mean by bar? Like.. a f*^King bar.. a horizontal or vertical rectangle like your grandmother used to code for Windows's start bar, or OSX's menu bar. It's a program that renders rectangular a window that behaves slightly differently to standard windows in that it generally won't have a title bar and it'll generally be fixed in place, generally to the edge of a screen and usually it'll render on top of everything else.

There are a few choices when it comes to picking a bar in linux. Some WMs come with a bar (or some more bloated equivalent) by default, they can generally be disabled and replaced with a more traditional bar script if you're so inclined but I'm not actually suggesting anyone do that. Unless they want to, then they should. Trusting the baristocracy to respect existing authority in an advanced window manager that already went to the effort of bundling its own bar or dock or whatever is like.. a long term goal, I guess. But not a priority. I reckon you might be in for a world of hurt unless you're a developer looking to mess around wasting your occasional spare time hacking on a damn bar script.

But if your window manager doesn't come with a bar, the baristocracy might be for you! Even if you aren't using the sort of "dynamic hardware" this thing was written for, eventually I hope to provide a valuable tool for most of those use cases.

Traditional bars are basically a pipe, you feed text into the pipe and the text is rendered into the bar. Imagine in a standard keyboard driven UX, the bar is not like the start bar in windows, it is more like a status bar or a "context reminder" of sorts. You aren't reaching away from the keyboard to get to the mouse to click on the next workspace over, you're pressing a three key combo on the keyboard to switch as fast as you can think. A bar script that tells you which workspace you're on will be scripted to learn that information

So what's a bartender? Its what I was originally going to call this thing. A script for attending to the upkeep and service of your bar scripts. A layer of abstraction. Unfortunately I think someone beat me to the punch with the name and is probably doing something similar.

## So what is the baristocracy supposed to be and why in the world would I choose the product of an obviously deranged coder over some other hypothetical rival bit of software?

**Right now you probably should choose any other mature bar tending script, or learn how to do things the traditional way. This software isn't really ready for wide consumption and I'm certainly not ready to take requests or bug reports.**

**This is more like.. prototype status right now, I just finally decided to back it up. RUN AWAY, THERE'S PROBABLY ALL KINDS OF DUMB STUFF HARDCODED IN HERE STILL. HOPEFULLY NO KEYS THO AMIRITE.**

The short term **goals** can be summed up thusly:

- easy to customise using bash or whatever scripting language is preferred by the user
- basically a pipe managing and bar managing engine, with users able to drop in their own data sources and/or output renderers with minimum technical knowledge
- a lightweight daemon that can manage
  - the starting and stopping of bar scripts on their respective monitors when those monitors connect/disconnect
  - splitting information across different bars depending on how many screens are connected / bars are running, along with any other variables that might go into determining a "bar context" or profile
  - maintenance of groups of related desktops or applications, according to whatever critera the user might find useful
    - I'm thinking about (hopefully) sensible defaults like, desktops grouped on monitor B are moved together into some identifiable group in monitor A's "workspace management" bar output when monitor B is disconnected, and moved back as a group when it is re-connected.
  - clearer separation of configuration, profile management, system config / profiles, bla bla bla
  - documentation
  - "in-application" configuration, taking advantage of menu code etc
  - decoupling the reliance on bspwm/bspc, and on (ocelot-)dzen
  - ie move closer to being a pure abstraction layer that happens to provide support for bspwm/bspc
  - explore wmutils to see what tools might be available for WM-agnostic control over things we currently rely on bspwm/bspc for

The long term goals include:

- interactive bar elements which can be pulled out to reveal system controls for realtime access to system management without the need for mouse interaction
  - ie mouse, touchscreen and keyboard will all be first class citizens for accessing the bars' more complex widgets
- things like the above probably separated into extension packs with their own set of requirements and generally targeting support for particular user demographics, device support, etc. a pick and mix of compatible plugins to get a nice lightweight shell for managing a machine and its open GUI applications
- a dope science fiction-esque "knowledge and power at your fingertips" experience that the discerning oldschool linux user damn well deserves by now, made easy enough for novice users to use effectively.
