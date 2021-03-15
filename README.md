# TS2-Fork - Train Signalling Simulation

## Motivation of this fork

This is a fork of the 0.6 version of http://github.com/ts2/ts2 created by npiganeau. 0.6 was the last version before the "New Arch" was implemented, where the actual simulation was split off into a simulation server written in Go. The project is pretty dead since 2019, and this is an attempt to revive it and continue development.
I have decided to continue on the base of 0.6 for the following reasons:
- Since introduction of the sim server, there have not been many new features
- The client is still full of old code from the 0.6 era, which appears to cause various subtle problems.
- I have exactly zero experience with Go, and am not in the mood right now to learn another programming language just for this
- In my opinion, a client-server concept is good, but the server should be written in Python too so that it can share code with the client and the editor.

My roadmap for this project is as follows:
- First, bring it to a state where it is usable and mostly bug-free in the current architecture
- Write one or two more simulations (probably Görlitz) to further debug it
- Think about new features
- Maybe separate the data model from the view layer so that, in a later stage, client and server can be separated.

Below is the original content of the README at the time of the fork. It will be rewritten at some point to reflect a more up-to-date state.

**IMPORTANT**
- The 0.5 version and this `master`branch is the **last version to use PyQt4** 
- Soon the `develop` branch will be merged which is **python3 + pyQt5 only** and the future path
- Also saving data in json instead of sqlite with future sharing online idea 
  - https://github.com/ts2/ts2-data
- Project moved from sourceforge to github 
   - ts2.sf.net to http://github.com/ts2 and http://ts2.github.io/


## Overview
**Train Signalling Simulation (TS2)** is a railways simulation game where you have to dispatch trains across an area and keep them on schedule. 

## Links
* TS2 Homepage - [ts2.github.io](http://ts2.github.io/)
* TS2 Chat - [irc.freenode.net#trainsigsim](irc://irc.freenode.net#trainsigsim)
* TS2 Project at Github - [github.com/ts2](http://github.com/ts2/)
* TS2 API Docs - autogen at [docs-ts2.rhcloud.com](http://docs-ts2.rhcloud.com/)

## Status
TS2 is beta software, meaning it is playable, but still lacks many features that one would expect from a real simulation, will it ever be finished.
When starting TS2, you will be able to download simulations from our [ts2-data](https://github.com/ts2/ts2-data) server.

New simulations can be created with the editor provided with ts2.

## Installation
* Released versions:
    - Windows 64 bits: use provided installer and run ts2.exe.
    - Other platforms: see source installation.
* Source installation:
    - Download and install Python v3 or above at [www.python.org](http://www.python.org).
    - Download and install PyQt v5 or above at [http://www.riverbankcomputing.co.uk](http://www.riverbankcomputing.co.uk).
    - Grab the sources from GitHub development page.
    - Run start-ts2.py

## Playing (QuickStart)
* Load a simulation from the _simulation_ directory (or the _data_ directory if you have installed from sources).
    If you want to load a simulation from a previous version of TS2, you will need to open it with the editor
    first and save it before loading it again in the main window.
* Route setting:
    - To turn a signal from red to green, you need to set a route from this signal to the next one.
    - To set a route left click on the signal and then to the next one. If you can create a route
        between these signals, the track between both signals is highlighted in white, the points are
        turned automatically for this route and the first signal color turn to yellow (or green if
        the second signal is already yellow or green).
    - To cancel a route, right-click on its first signal.
    - Routes are automatically cancelled by the first train passing through. However, you can set a
        persistent route by holding the shift key before clicking on the second signal. Persistent
        routes have a little white square next to their first signal.
    - Forcing route setting: It is possible to force a route setting by pressing _ctrl_ and _alt_ while
        clicking on the second signal. Beware as this will not check other conflicting routes and may result
        in train crashes or other unknown behaviour.
* Train information:
    - Click on a train code on the scene or on the train list to see its information on the
        "Train Information" window. The "Service information" window will also update.
* Station information:
    - Click on a platform on the scene to display the station timetable in the "Station information"
        window.
* Interact with trains:
    - Right click on a train code on the scene or on the "Train information" or on the "Train List"
    window to display the train menu. This menu enables you to:
        + Assign a new service to this train. Select the service in the popup window and click "Ok".
        + Reset the service. i.e. tell the train driver to stop at the first station again.
        + Reverse train. i.e. change the train direction.
    - Trains automatically change service when it is over (on drain demo BW01 becomes WB01 when reaching
    depot)
* You should see trains run, stop at red signals and at scheduled stations. They should depart at the
    departure time or after some time after the arrival time if the departure time is past.
* Scoring:
    Each time a train arrives late at a station, stops at the wrong platform or is routed to a wrong direction
    penalty points are added to the score.


## Change log

###Version 0.6:
- New release that is PyQt5 = Python3 only
- Announce move and infrastructure to github
- New home page, et all
- Also Data is now json and in ts2-data
- Ability to download sims / signals from ts2-data
- Trains shunting
- Trains splitting (joining postponed)
- New parametric signals
- French BAL signals (except blinking)
- UK Shunt signals
- UI improvements (toolbars, etc.)
- Catch exceptions when loading sims

###Version 0.5:
- Last PyQt4 version
- Improved editor including the following features 
    - Multi-selection
    - Copy/Paste
    - Mass setting of properties
    - Resizing of platform items with mouse
- New signals with :
    - Short length 
    - Freely positionable berth
    - New signal types, including UK 4 aspects signals
