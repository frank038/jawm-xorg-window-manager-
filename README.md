Jawm - a python3+xlib stacking window manager

Free to use and modify.

Requirements:
- python3
- xlib
- ewmh
- PIL
- pidof or pgrep

Execute this program using the script: jawm.sh

Some options can be changed in the beginning of the file jawm.py.

What is supported:
- titlebar (can be turned off/on as static option)
- titlebar buttons: close, maximize and minimize
- keyboard actions, using the Super_L key (left win key):
  - close the active window: c
  - move the window: m
  - minimize the window: n
  - exit from this wm: e
  - execute xterm: x
  - custom actions: 1 and 2 and 3 and 4 (actually empty)
  - left mouse button: move the window
- window resizing (bottom-right only)
- sloppy focus (if enabled)
- colors and borders and titlebar size

Limitations:
- no multimonitor support;
- no virtual desktops support;
- other missing features.

Early release, but usable. Tint2 can be used with this wm.

Known issues:
- browsers in fullscreen mode
- a little low performance while resizing (due to expose event and buttons)

