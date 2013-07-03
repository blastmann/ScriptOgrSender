## ScriptOgrSender for ST

This is just a simple plug-in for Sublime Text. In order to post our markdown posts to our blog easily, we just don't want to leave ST and just submit the post directly.

#### Changelog 2013-07-03

* Fix proxy error under Sublime Text 2.
* Update this readme file.

#### Changelog 2013-06-30

* Refactor some codes and add ST3 support.
* If you want to use this in **Sublime Text 3**, please check out the Python3 branch.

#### Changelog 2013-02-05

* Release version 0.2.2

#### Changelog 2013-02-05

*  Add my app key.

    ##### Be careful
    
    **Please don't modify this key and don't use it in other apps.** If you want to develop your own app, you'd better apply a new app key in Scriptogr.am for your own.

#### Changelog 2013-02-03
* Refactor the command classes
* UTF8 data encode
* A new Snippet for ScriptOgr.am article headers
* Add shortcuts scope (Shortcuts will only activate in Markdown format document)

## Installation

### Package Control
That's easy to install this with Package Control. Just bring up the COmmand Palette and select "Package Control: Install Packages". Wait for a second and then select ScriptOgrSender when the list appears.

After installation, you'll have to set your own **user\_id** in the ScriptOgrSender setting file. Remember, you'd better set your **user\_id** in the user setting file in order to avoid plugin upgrading overwrite.

### Manual
1. Clone this repo into **Packages directory**.
2. Input your **user\_id** into setting file. Please find your **user\_id** in your own dashboard.
3. Save it, enjoy your simple posting.

## License
Copyright 2012 Chaoming Chen. Licensed under the BSD License.