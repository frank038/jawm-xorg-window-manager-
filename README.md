Jawm - a python3+xlib stacking window manager

Free to use and modify.

Requirements:
- python3
- xlib
- PIL
- pidof or pgrep

Execute this program using the script: jawm.sh (which can also be used for environment settings and for launching other programs before this wm)

Some options can be changed in the beginning of the file jawm.py.

What is supported:
- titlebar (the decoration can be turned off/on as static option)
- titlebar buttons: close, maximize and minimize
- keyboard actions, using the mandatory Super_L key (left win key):
  - close the active window: c
  - move the window: m
  - minimize the window: n
  - exit from this wm: e
  - left mouse button: move the window
  - resize: w (up) s (bottom) a (left) d (right)
  - resize: right mouse button
- custom keyboard actions, using the mandatory Super_L key (left win key):
  - execute xterm (or other terminal o program): x
  - custom actions: 1 and 2 and 3 and 4 (actually empty)
- window resizing (bottom-right only with mouse)
- sloppy focus
- colors and borders and titlebar size (as options)

Limitations:
- no multimonitor support;
- no virtual desktops support;
- no text nor icon in the titlebar;
- other missing features.

Early release, almost finished, but usable. Tint2 can be used with this wm.

Known issues:
- firefox: fullscreen mode doesn't work properly (I have no idea)
- a little lower performance while resizing (due to expose event and buttons)

