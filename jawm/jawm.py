#!/usr/bin/env python3

# v. 20240205

##############
##### OPTIONS

# the border size of the decoration (px)
BORDER_WIDTH = 3
# the other borders
BORDER_WIDTH2 = 2

# decoration border color
DECO_BORDER_COLOR1 = "#7F7F7F"

# the other border color
DECO_BORDER_COLOR2 = "#008000"

# disable window decoration: 1 disable - 0 enable
NO_DECO = 0

# space between buttons
BTN_SPACE = 4

# size: 1 normal (29 px) - 2 big (36 px)
TITLEBAR_SIZE = 1

# decoration color: buttons need to be recolored if changed
DECO_COLOR = "#D2AE26"

# notification position: 1 top - 2 bottom
_NOTIFICATION_POS = 1

# window manager actions: Super_L (win key) - Alt_l - Control_l
_STATE = "Super_L"

# terminate this program - key e
_EXIT = "e"

# terminal - key x
_TERMINAL = "xterm"

# command 1 - key 1
COMM_1 = ""

# command 2 - key 2
COMM_2 = ""

# command 3 - key 3
COMM_3 = ""

# command 4 - key 4
COMM_4 = ""

# windows always centered: 1 yes - 0 no
# if 0, try to use application infos before
ALWAYS_CENTERED = 0

# resize with Super+right mouse button: 0 no - 1 yes
RESIZE_WITH_KEY = 1

#### keybindings with Super_L
# close
_CC = "c"
# maximize
_MM = "m"
# minimize
_MN = "n"
# resize down
_RS = "s"
# resize up
_RW = "w"
# resize right
_RD = "d"
# resize left
_RA = "a"
# execute terminal
_EXEC_TERM = "x"
# custom program 1
_C1 = "1"
# custom program 2
_C2 = "2"
# custom program 3
_C3 = "3"
# custom program 4
_C4 = "4"

##############

from Xlib.display import Display
from Xlib import X, XK, protocol, Xatom, Xutil
import sys, os, shutil
import subprocess
import signal
from PIL import Image


# randr extension
_is_randr = 0
if Display().has_extension('RANDR'):
    if Display().query_extension('RANDR') != None:
        from Xlib.ext import randr
        from Xlib.ext.randr import RRScreenChangeNotify, RRScreenChangeNotifyMask
        _is_randr = 1


screen = Display().screen()
root = Display().screen().root


TITLE_HEIGHT = 0
if TITLEBAR_SIZE == 1:
    TITLE_HEIGHT = 29
elif TITLEBAR_SIZE == 2:
    TITLE_HEIGHT = 36
BTN_SIZE = TITLE_HEIGHT

# give the focus to the window under the pointer
SLOPPY_FOCUS = 1

colormap = Display().screen().default_colormap
win_color = colormap.alloc_named_color(DECO_COLOR).pixel
border_color1 = colormap.alloc_named_color(DECO_BORDER_COLOR1).pixel
border_color2 = colormap.alloc_named_color(DECO_BORDER_COLOR2).pixel


WINDOW_WITH_DECO = [
"_NET_WM_WINDOW_TYPE_UTILITY",
"_NET_WM_WINDOW_TYPE_DIALOG",
"_NET_WM_WINDOW_TYPE_NORMAL",
]

WINDOW_WITH_NO_DECO = [
'_NET_WM_WINDOW_TYPE_TOOLBAR',
'_NET_WM_WINDOW_TYPE_MENU',
'_NET_WM_WINDOW_TYPE_DND',
'_NET_WM_WINDOW_TYPE_DROPDOWN_MENU',
'_NET_WM_WINDOW_TYPE_COMBO',
'_NET_WM_WINDOW_TYPE_POPUP_MENU']

WINDOWS_MAPPED_WITH_NO_DECO = [
'_NET_WM_WINDOW_TYPE_DOCK',
'_NET_WM_WINDOW_TYPE_DESKTOP',
'_NET_WM_WINDOW_TYPE_SPLASH',
'_NET_WM_WINDOW_TYPE_NOTIFICATION']

_is_running = 1

if NO_DECO == 1:
    BORDER_WIDTH = 0
    TITLE_HEIGHT = 0

# physical screen size
screen_width = Display().screen().width_in_pixels
screen_height = Display().screen().height_in_pixels
# usable screen size
screen_width_usable = 0
screen_height_usable = 0
# usable screen x and y
start_x = 0
end_x = 0
start_y = 0
end_y = 0


DOCK_HEIGHT_X = 0
DOCK_HEIGHT_Y = 0
DOCK_HEIGHT_T = 0
DOCK_HEIGHT_B = 0

def _screen_usable():
    global screen_width_usable
    global screen_height_usable
    global start_x
    global end_x
    global start_y
    global end_y
    global DOCK_HEIGHT_X # x
    global DOCK_HEIGHT_Y # y
    global DOCK_HEIGHT_T # top
    global DOCK_HEIGHT_B # bottom
    # usable screen size
    screen_width_usable = screen_width
    screen_height_usable = screen_height - DOCK_HEIGHT_T - DOCK_HEIGHT_B
    # usable screen x and y
    start_x = 0 + DOCK_HEIGHT_X
    end_x = screen_width_usable
    start_y = 0 + DOCK_HEIGHT_Y+DOCK_HEIGHT_T
    end_y = screen_height_usable-DOCK_HEIGHT_B
    #
_screen_usable()

# this program pid
_THIS_PID = 0
ret_pid = 0
try:
    if shutil.which("pidof"):
            ret_pid = subprocess.check_output(["pidof","-s","python3", sys.argv[0]]).decode()
    elif shutil.which("pgrep"):
        ret_pid = subprocess.check_output(["pgrep","-f","python3", sys.argv[0]]).decode()
    _THIS_PID = int(ret_pid)
except:
    _THIS_PID = 0


def signal_catch(signal, frame):
    _is_running = 0
    Display().close()
    sys.exit(0)

# ctrl+c
signal.signal(signal.SIGINT, signal_catch)
# term or kill
signal.signal(signal.SIGTERM, signal_catch)

DECO_EXPOSURE = 0
if NO_DECO == 0:
    DECO_EXPOSURE = 1

if DECO_EXPOSURE:
    mask_deco = X.EnterWindowMask | X.LeaveWindowMask | X.ExposureMask | X.SubstructureNotifyMask
else:
    mask_deco = X.EnterWindowMask | X.LeaveWindowMask | X.SubstructureNotifyMask


class x_wm:
    
    def __init__(self):
        #
        self.display = Display()
        self.screen = self.display.screen()
        self.root = self.display.screen().root
        #
        self.WM_DELETE_WINDOW = self.display.intern_atom('WM_DELETE_WINDOW')
        self.WM_PROTOCOLS = self.display.intern_atom('WM_PROTOCOLS')
        self.NET_WM_STATE = self.display.intern_atom("_NET_WM_STATE")
        self.NET_STATE = self.display.intern_atom("_NET_STATE")
        self.NET_STATE_ABOVE = self.display.intern_atom("_NET_WM_STATE_ABOVE")
        self.NET_STATE_BELOW = self.display.intern_atom("_NET_WM_STATE_BELOW")
        self.CHANGE_STATE = self.display.intern_atom("_NET_CHANGE_STATE")
        self.NET_WM_NAME = self.display.intern_atom('_NET_WM_NAME')
        self.WM_NAME = self.display.intern_atom('WM_NAME')
        self.WM_FULLSCREEN = self.display.intern_atom("_NET_WM_STATE_FULLSCREEN")
        self.WM_MAXIMIZED_HORZ = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_HORZ")
        self.WM_MAXIMIZED_VERT = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_VERT")
        self.WM_HIDDEN = self.display.intern_atom("_NET_WM_STATE_HIDDEN")
        self.WM_CHANGE_STATE = self.display.intern_atom("WM_CHANGE_STATE")
        self.WM_NET_CHANGE_STATE = self.display.intern_atom("_NET_WM_CHANGE_STATE")
        self.NET_ACTIVE_WINDOW = self.display.intern_atom("_NET_ACTIVE_WINDOW")
        self.NET_LIST = self.display.intern_atom("_NET_CLIENT_LIST")
        self.NET_LIST_STACK = self.display.intern_atom("_NET_CLIENT_LIST_STACKING")
        self.STATE_DEMANDS_ATTENTION = self.display.intern_atom("_NET_WM_STATE_DEMANDS_ATTENTION")
        self.WM_S = self.display.intern_atom('WM_S0')
        #
        mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask
                | X.EnterWindowMask | X.LeaveWindowMask | X.FocusChangeMask
                | X.ButtonPressMask | X.ButtonReleaseMask | X.PropertyChangeMask
                | X.KeyPressMask | X.KeyReleaseMask)
        #
        self.root.change_attributes(event_mask=mask)
        # Super_L Alt_L Control_L
        self.root.grab_key(self.display.keysym_to_keycode(XK.string_to_keysym(_STATE)),
            X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync)
        # windows with decoration: window:decoration
        self.DECO_WIN = {}
        # all managed windows
        self.all_windows = []
        # all managed windows - stack
        self.all_windows_stack = []
        # windows in maximized state: window:[prev_win_x, prev_win_y, win_unmaximized_width, win_unmaximized_height]
        self.MAXIMIZED_WINDOWS = {}
        # windows in minimized state: window:[deco]
        self.MINIMIZED_WINDOWS = {}
        # current active window (the program)
        self.active_window = None
        # a window is desktop type
        self.desktop_window = []
        # windows that are dock type: window - x y t b
        self.dock_windows = {}
        # window with transient window: window:transient
        self.transient_windows = {}
        # windows belonging to window leader: window:[list of window with window_group hint (except transient)]
        self.windows_group = {}
        # only one can be in this state
        self.window_in_fullscreen_state = []
        #
        self.window_in_fullscreen_state_CM = []
        # window to bring on top or move by btn1: window or decoration
        self.grabbed_window_btn1 = None
        # mouse button 1 for resizing: decoration otherwise window
        self.btn1_drag = None
        # 
        self.window_resize_geometry = None
        self.mouse_button_resize_drag_start_point = None
        # the window or the decoration when a key is been pressed
        self.key_press_window = None
        # the window that has the pointer in
        self.entered_window = None
        ########
        self.mouse_button_left = 0
        self.delta_drag_start_point = None
        #
        self.on_supported_attributes()
        #
        # self._root_change_property('_NET_NUMBER_OF_DESKTOPS',[1])
        self._root_change_property('_NET_NUMBER_OF_DESKTOPS',[1,0,0,0,0])
        #
        # self._root_change_property('_NET_DESKTOP_VIEWPORT',[0,0])
        self._root_change_property('_NET_DESKTOP_VIEWPORT',[0,0,0,0,0])
        #
        # self._root_change_property('_NET_CURRENT_DESKTOP',[0])
        self._root_change_property('_NET_CURRENT_DESKTOP',[0, X.CurrentTime,0,0,0])
        #
        # self._root_change_property('_NET_DESKTOP_GEOMETRY',[screen_width, screen_height])
        self._root_change_property('_NET_DESKTOP_GEOMETRY',[screen_width, screen_height,0,0,0])
        #
        self._root_change_property('_NET_WORKAREA',[start_x,start_y,screen_width_usable,screen_height_usable])
        #
        _string = "Desktop"
        self.root.change_property(self.display.get_atom('_NET_DESKTOP_NAMES'), self.display.intern_atom('UTF8_STRING'), 8, _string.encode())
        # 
        self._root_change_property('_NET_SHOWING_DESKTOP',[0])
        #
        self._window = None
        self._wm_support()
        #
        self.display.flush()
        # decoration buttons
        if NO_DECO == 0:
            self.deco_btn_width = 0
            self.deco_btn_height = 0
            self.on_deco_btn()
        #
        # self.on_start()
        #
        self.main_loop()
    
    
    # problema col numero di desktop: Xatom.WINDOW o 32 o data?
    def _root_change_property(self, _type, _data):
        self.root.change_property(
            self.display.get_atom(_type),
            Xatom.CARDINAL,
            32, _data)
    
    #
    def _wm_support(self):
        self._window = self.screen.root.create_window(0, 0, 1, 1, 0,
            self.screen.root_depth,override_redirect=1)
        self.display.sync()
        #
        for ww in [self.root, self._window]:
            ww.change_property(self.display.get_atom('_NET_SUPPORTING_WM_CHECK'),
                Xatom.WINDOW,32,[self._window.id])
        #
        self._window.change_property(
            self.display.get_atom('_NET_WM_NAME'),
            self.display.intern_atom('UTF8_STRING'),
            8,'jawm'.encode())
        # cmd, cls
        self._window.set_wm_class('jawm', 'JAWM')
        #
        if _THIS_PID:
            self._window.change_property(
                self.display.get_atom("_NET_WM_PID"),
                Xatom.CARDINAL,
                32, [_THIS_PID], X.PropModeReplace)
        #
        self._window.set_selection_owner(self.WM_S, X.CurrentTime)
        #
        if _is_randr == 1:
            # Enable all RandR events.
            self._window.xrandr_select_input(randr.RRScreenChangeNotifyMask)

   
    # add a decoration to win
    def win_deco(self, win):
        if NO_DECO == 1:
            win.configure(border_width=BORDER_WIDTH2)
            self.DECO_WIN[win] = None
            return -1
        #
        geom = win.get_geometry()
        DECO_WIDTH = geom.width+BORDER_WIDTH*2
        DECO_HEIGHT = geom.height+TITLE_HEIGHT+BORDER_WIDTH*2
        #
        deco = self.screen.root.create_window(
            geom.x-BORDER_WIDTH-BORDER_WIDTH2,
            geom.y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2,
            DECO_WIDTH,
            DECO_HEIGHT,
            0,
            self.screen.root_depth,
            X.InputOutput,
            background_pixel=win_color,
            override_redirect=1,
        )
        #
        deco.change_attributes(border_pixel=border_color1, border_width=BORDER_WIDTH2)
        deco.configure(border_width=BORDER_WIDTH2)
        #
        deco.change_attributes(event_mask=mask_deco)
        self.display.sync()
        #
        # wret = 0
        # def werror(err, ww):
            # wret = -1
        #
        # win.reparent(deco, BORDER_WIDTH, TITLE_HEIGHT, onerror=werror)
        #
        return deco
    
    def on_deco_btn(self):
        # close
        im = Image.open('icons/close40x28.png').convert('RGB')
        # im = im.resize((40,28))
        iw, ih = im.size
        self.deco_btn_width = iw
        self.deco_btn_height = ih
        self.l_mask = self.screen.root.create_pixmap(iw, ih, self.screen.root_depth)
        self.l_gc = self.l_mask.create_gc()
        self.l_mask.put_pil_image(self.l_gc, 0, 0, im)
        # maximize
        im1 = Image.open('icons/max40x28.png').convert('RGB')
        # im1 = im1.resize((40,28))
        iw1, ih1 = im1.size
        self.l_mask1 = self.screen.root.create_pixmap(iw1, ih1, self.screen.root_depth)
        self.l_gc1 = self.l_mask1.create_gc()
        self.l_mask1.put_pil_image(self.l_gc1, 0, 0, im1)
        # minimize
        im2 = Image.open('icons/min40x28.png').convert('RGB')
        # im2 = im2.resize((40,28))
        iw2, ih2 = im2.size
        self.l_mask2 = self.screen.root.create_pixmap(iw2, ih2, self.screen.root_depth)
        self.l_gc2 = self.l_mask2.create_gc()
        self.l_mask2.put_pil_image(self.l_gc2, 0, 0, im2)
        
    
    def deco_btn(self, deco):
        dgeom = deco.get_geometry()
        dx = dgeom.x
        dw = dgeom.width
        # normal
        if TITLEBAR_SIZE == 1:
            imx = dw-BORDER_WIDTH-BORDER_WIDTH2-self.deco_btn_width
            imy = 2
        # big
        elif TITLEBAR_SIZE == 2:
            imx = dw-BORDER_WIDTH-BORDER_WIDTH2-self.deco_btn_width
            imy = BORDER_WIDTH+BORDER_WIDTH2
        # close
        deco.copy_area(self.l_gc, self.l_mask, 0, 0, self.deco_btn_width,self.deco_btn_height, imx,imy)
        # maximize
        imx1 = imx - BTN_SPACE - self.deco_btn_width
        imy1 = imy
        deco.copy_area(self.l_gc1, self.l_mask1, 0, 0, self.deco_btn_width,self.deco_btn_height, imx1,imy1)
        # minimize
        imx2 = imx - BTN_SPACE - self.deco_btn_width - BTN_SPACE - self.deco_btn_width
        imy2 = imy
        deco.copy_area(self.l_gc2, self.l_mask2, 0, 0, self.deco_btn_width,self.deco_btn_height, imx2,imy2)
        
        
    
    # find the window from its decoration
    def find_win_of_deco(self, deco):
        for iitem in self.DECO_WIN:
            if self.DECO_WIN[iitem] == deco:
                return iitem
        #
        return None
    
    def main_loop(self):
        global screen_width
        global screen_height
        #
        while _is_running:
            #
            event = self.root.display.next_event()
            #
            if event.type == X.MapNotify:
                #
                if event.window == X.NONE or event.window == None or event.window == self.root:
                    continue
                # trying to use another wm causes an error on asking its attrs
                try:
                    attrs = event.window.get_attributes()
                except:
                    continue
                if attrs is None:
                    continue
                # decoration too
                win = None
                if attrs.override_redirect:
                    # find the window from decoration
                    win2 = self.find_win_of_deco(event.window)
                    if win2:
                        continue
                    else:
                        continue
                    #
                    if not win:
                        continue
                # skip if already present
                if event.window in self.all_windows:
                    continue
                if event.window in self.all_windows_stack:
                    continue
                # docks
                if event.window in self.dock_windows:
                    continue
                # desktop
                if event.window in self.desktop_window:
                    continue
                # check if this window is a transient one
                w_is_transient = event.window.get_full_property(self.display.get_atom("WM_TRANSIENT_FOR"), X.AnyPropertyType)
                if w_is_transient:
                    event.window.set_input_focus(X.RevertToParent, 0)
                    continue
                #
                # window inside the decoration or window (without decoration)
                if event.window in self.DECO_WIN:
                    wwin = event.window
                    deco = self.DECO_WIN[wwin]
                    #
                    if self.active_window:
                        # the old active window
                        if self.active_window != wwin:
                            # grab LMB - will be the old active window
                            self.active_window.grab_button(1, X.AnyModifier, True,
                                X.ButtonPressMask|X.ButtonReleaseMask, X.GrabModeAsync,
                                X.GrabModeAsync, X.NONE, X.NONE)
                            #
                            if self.DECO_WIN[self.active_window]:
                                self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                            else:
                                self.active_window.change_attributes(border_pixel=border_color2)
                            # its transient
                            if self.active_window in self.transient_windows:
                                self.transient_windows[self.active_window].change_attributes(border_pixel=border_color2)
                                self.transient_windows[self.active_window].grab_button(1, X.AnyModifier, True,
                                X.ButtonPressMask|X.ButtonReleaseMask, X.GrabModeAsync,
                                X.GrabModeAsync, X.NONE, X.NONE)
                            # the new active window
                            self.active_window = wwin
                    else:
                        # the new active window
                        self.active_window = wwin
                        #
                        if self.DECO_WIN[self.active_window]:
                            self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color1)
                        else:
                            self.active_window.change_attributes(border_pixel=border_color1)
                    #
                    self.all_windows.append(wwin)
                    self._update_client_list()
                    self.all_windows_stack.append(wwin)
                    self._update_client_list_stack()
                    #
                    ew_type = None
                    #
                    ew_type_tmp = self.get_window_type(event.window)
                    if ew_type_tmp != 1:
                        if self.display.intern_atom("_NET_WM_WINDOW_TYPE_DIALOG") in ew_type_tmp:
                            self.active_window.set_input_focus(X.RevertToParent, 0)
                        elif self.display.intern_atom("_NET_WM_WINDOW_TYPE_UTILITY") in ew_type_tmp:
                            self.active_window.set_input_focus(X.RevertToParent, 0)
                        else:
                            self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                    else:
                        self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                    #
                    self.active_window.raise_window()
                    self.display.sync()
                    #
                    # self.display.flush()
                    #
                    self._update_active_window(self.active_window)
                    #
            #
            elif event.type == X.MapRequest:
                if event.window == X.NONE or event.window == None:
                    continue
                #
                # check if this window is a transient one
                _is_transient = None
                prop = None
                try:
                    prop = event.window.get_full_property(self.display.get_atom("WM_TRANSIENT_FOR"), X.AnyPropertyType)
                except:
                    pass
                if prop:
                    w_id = prop.value.tolist()[0]
                    #
                    for win in self.DECO_WIN:
                        if win.id == w_id:
                            self.transient_windows[win] = event.window
                            _is_transient = win
                            break
                #
                attrs = event.window.get_attributes()
                if attrs is None:
                    continue
                # not to be managed by window manager
                if attrs.override_redirect:
                    continue
                #
                # window_group hint
                whints = event.window.get_wm_hints()
                if hasattr(whints, "window_group"):
                    pwin = whints["window_group"]
                    if not pwin in self.windows_group:
                        self.windows_group[pwin] = [event.window]
                    else:
                        self.windows_group[pwin].append(event.window)
                #
                ew_type = None
                #
                ew_type_tmp = self.get_window_type(event.window)
                ew_type = []
                if ew_type_tmp != 1:
                    for ee in ew_type_tmp:
                        ew_type.append(self.display.get_atom_name(ee))
                #
                if ew_type:
                    if ew_type[0] in WINDOW_WITH_NO_DECO:
                        # win_geom = event.window.get_geometry()
                        # x = max(win_geom.x, start_x)
                        # y = max(win_geom.y, start_y)
                        # event.window.configure(x=x, y=y+50)
                        event.window.map()
                        continue
                    # dock desktop splash notification
                    elif ew_type[0] in WINDOWS_MAPPED_WITH_NO_DECO:
                        #
                        if ew_type[0] == '_NET_WM_WINDOW_TYPE_DOCK':
                            geom = event.window.get_geometry()
                            global DOCK_HEIGHT_X
                            global DOCK_HEIGHT_Y
                            global DOCK_HEIGHT_T
                            global DOCK_HEIGHT_B
                            # _NET_WM_STRUT, left, right, top, bottom, CARDINAL[4]/32
                            _result = self.getProp(event.window, 'STRUT')
                            if _result:
                                # 0 0 38 0
                                DOCK_HEIGHT_X += _result[0]
                                DOCK_HEIGHT_Y += _result[1]
                                DOCK_HEIGHT_T += _result[2]
                                DOCK_HEIGHT_B += _result[3]
                                _screen_usable()
                            else:
                                # _NET_WM_STRUT_PARTIAL, left, right, top, bottom, left_start_y, left_end_y,
                                # right_start_y, right_end_y, top_start_x, top_end_x, bottom_start_x,
                                # bottom_end_x,CARDINAL[12]/32
                                _result = self.getProp(event.window, 'STRUT_PARTIAL')
                                if _result:
                                    # 0 0 38 0 0 0 0 0 0 1599 0 0
                                    DOCK_HEIGHT_X += _result[0]
                                    DOCK_HEIGHT_Y += _result[1]
                                    DOCK_HEIGHT_T += _result[2]
                                    DOCK_HEIGHT_B += _result[3]
                                    _screen_usable()
                            # 
                            event.window.configure(x=geom.x, y=geom.y)#, width=screen_width, height=screen_height)
                            #
                            event.window.map()
                            if _result:
                                _struct_data = [_result[0],_result[1],_result[2],_result[3]]
                            else:
                                _struct_data = []
                            self.dock_windows[event.window] = _struct_data
                            self.all_windows.insert(len(self.desktop_window), event.window)
                            self._update_client_list()
                            self.all_windows_stack.insert(len(self.desktop_window), event.window)
                            self._update_client_list_stack()
                            #
                            prop = event.window.get_full_property(self.display.get_atom("_NET_WM_STATE_ABOVE"), X.AnyPropertyType)
                        # desktop
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_DESKTOP':
                            if  self.desktop_window == []:
                                self.desktop_window.append(event.window)
                                event.window.configure(x=0, y=0, width=screen_width, height=screen_height)
                                # put at bottom of all
                                self.all_windows.insert(0, event.window)
                                self._update_client_list()
                                self.all_windows_stack.insert(0, event.window)
                                self._update_client_list_stack()
                                event.window.map()
                        #
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_NOTIFICATION':
                            ngeom = event.window.get_geometry()
                            x = end_x - ngeom.width - 4
                            if _NOTIFICATION_POS == 2:
                                y = end_y - 4
                            else:
                                y = start_y + 4
                            event.window.configure(x=x, y=y)
                            self.display.sync()
                            event.window.map()
                        #
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_SPLASH':
                            win_geom = event.window.get_geometry()
                            x = int((screen_width-win_geom.width)/2)
                            y = int((screen_height-win_geom.height)/2)
                            event.window.configure(x=x, y=y)
                            event.window.map()
                        #
                        continue
                #
                if not event.window:
                    continue
                if event.window in self.DECO_WIN:
                    continue
                # remove the border from the program
                event.window.change_attributes(
                         border_pixel=border_color1,
                         border_width=0)
                # center the window
                win_geom = event.window.get_geometry()
                #
                x = 0
                y = 0
                if _is_transient:
                    par_win_geom = _is_transient.get_geometry()
                    x = int((par_win_geom.width-win_geom.width)/2+par_win_geom.x)
                    y = int((par_win_geom.height-win_geom.height+TITLE_HEIGHT/2)/2+par_win_geom.y)
                    # always in the screen
                    if (x + win_geom.width) > screen_width_usable or (y + win_geom.height) > screen_height_usable:
                        x = int((screen_width_usable-win_geom.width)/2)
                        y = int((screen_height_usable-win_geom.height)/2)
                else:
                    if ALWAYS_CENTERED == 0:
                        # if win_geom.x > 0 or win_geom.y > 0:
                        if win_geom.x > start_x or win_geom.y > start_y:
                            x = max(win_geom.x, start_x)
                            y = max(win_geom.y, start_y)
                        else:
                            x = max(int((screen_width_usable-win_geom.width)/2), start_x)
                            y = max(int((screen_height_usable-win_geom.height)/2), start_y)
                    elif ALWAYS_CENTERED == 1:
                        x = int((screen_width_usable-win_geom.width)/2)
                        y = int((screen_height_usable-win_geom.height)/2)
                #
                event.window.configure(x=x, y=y)
                # self.display.sync()
                #
                if _is_transient:
                    # add the border
                    event.window.change_attributes(border_pixel=border_color2, border_width=BORDER_WIDTH)
                    event.window.configure(border_width=BORDER_WIDTH)
                    #
                    mask = X.EnterWindowMask
                    event.window.change_attributes(event_mask=mask)
                    self.display.sync()
                    #
                    event.window.map()
                    event.window.raise_window()
                    #
                    continue
                #
                # skip window that doesnt want the decoration
                pprop = event.window.get_full_property(self.display.intern_atom('_MOTIF_WM_HINTS'), X.AnyPropertyType)
                # 
                if pprop != None:
                    if pprop.value:
                        if pprop.value.tolist()[2] == 0:
                            # add the border
                            event.window.configure(border_width=BORDER_WIDTH2)
                            #
                            # mask = X.EnterWindowMask | X.LeaveWindowMask
                            mask = X.EnterWindowMask|X.StructureNotifyMask
                            event.window.change_attributes(event_mask=mask)
                            #
                            self.DECO_WIN[event.window] = None
                            #
                            event.window.map()
                            event.window.raise_window()
                            #
                            continue
                #
                deco = self.win_deco(event.window)
                #
                if deco != -1:
                    deco.change_attributes(attrs)
                    self.display.sync()
                    #
                    self.DECO_WIN[event.window] = deco
                    # deco.map()
                    deco.raise_window()
                    #
                    if NO_DECO == 0:
                        self.deco_btn(deco)
                #
                event.window.raise_window()
                event.window.map()
                if deco != -1:
                    #deco.configure(x=x, y=y)
                    deco.map()
                #
                if NO_DECO == 0:
                    dgeom = deco.get_geometry()
                    if dgeom.y < start_y:
                        deco.configure(x=x, y=start_y)
                        event.window.configure(x=x+BORDER_WIDTH+BORDER_WIDTH2, y=start_y+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                        
                # mask = X.EnterWindowMask | X.LeaveWindowMask
                mask = X.EnterWindowMask
                event.window.change_attributes(event_mask=mask)
                #
                continue
                #
            #
            elif event.type == X.Expose:
                # if event.count == 0:
                if NO_DECO == 0:
                    deco = self.find_win_of_deco(event.window)
                    if deco:
                        # decoration buttons
                        self.deco_btn(event.window)
            #
            elif event.type == X.EnterNotify:
                if event.window == None:
                    continue
                if event.window == self.root:
                    self.entered_window = None
                #
                self.entered_window = event.window
                #
                if SLOPPY_FOCUS:
                    if event.window in self.DECO_WIN:
                        event.window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                    else:
                        for iitem in self.transient_windows:
                            if self.transient_windows[iitem] == event.window:
                                event.window.set_input_focus(X.RevertToParent, 0)
                                break
            #
            elif event.type == self.display.extension_event.ScreenChangeNotify:
                screen_width = event.width_in_pixels
                screen_height = event.height_in_pixels
                _screen_usable()
                #
                self._root_change_property('_NET_DESKTOP_GEOMETRY',[screen_width, screen_height])
                self._root_change_property('_NET_WORKAREA',[start_x,start_y,screen_width_usable,screen_height_usable])
            #
            elif event.type == X.UnmapNotify:
                if event.window == X.NONE or event.window == self.root:
                    continue
                # decoration
                if event.window in self.DECO_WIN:
                    if self.DECO_WIN[event.window]:
                        self.DECO_WIN[event.window].unmap()
            #
            # first unmap then destroy eventually
            elif event.type == X.DestroyNotify:
                # window_group hint
                _witem = None
                for witem in self.windows_group:
                    for iitem in self.windows_group[witem]:
                        if event.window == iitem:
                            self.windows_group[witem].remove(event.window)
                            _witem = witem
                            break
                if _witem:
                    if self.windows_group[_witem] == []:
                        del self.windows_group[_witem]
                # remove the dock
                if event.window in self.dock_windows:
                    _result = self.dock_windows[event.window]
                    if _result:
                        DOCK_HEIGHT_X -= _result[0]
                        DOCK_HEIGHT_X = max(DOCK_HEIGHT_X, 0)
                        DOCK_HEIGHT_Y -= _result[1]
                        DOCK_HEIGHT_Y = max(DOCK_HEIGHT_Y, 0)
                        DOCK_HEIGHT_T -= _result[2]
                        DOCK_HEIGHT_T = max(DOCK_HEIGHT_T, 0)
                        DOCK_HEIGHT_B -= _result[3]
                        DOCK_HEIGHT_B = max(DOCK_HEIGHT_B, 0)
                        _screen_usable()
                    #
                    # self.dock_windows.remove(event.window)
                    del self.dock_windows[event.window]
                    self.all_windows.remove(event.window)
                    self._update_client_list()
                    self.all_windows_stack.remove(event.window)
                    self._update_client_list_stack()
                    continue
                # remove the desktop
                if event.window in self.desktop_window:
                    self.desktop_window.remove(event.window)
                    self.all_windows.remove(event.window)
                    self._update_client_list()
                    self.all_windows_stack.remove(event.window)
                    self._update_client_list_stack()
                    continue
                #
                if event.window == X.NONE or event.window == None or event.window == self.root:
                    continue
                #
                # it is a transient window
                w_is_transient = None
                for wwin in self.transient_windows:
                    if self.transient_windows[wwin] == event.window:
                        wwin.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                        wwin.raise_window()
                        self.display.sync()
                        #
                        del self.transient_windows[wwin]
                        w_is_transient = 1
                        break
                if w_is_transient:
                    continue
                #
                # find the window not the decoration
                win = None
                deco = None
                # the window
                if event.window in self.DECO_WIN:
                    win = event.window
                    deco2 = self.find_win_of_deco(event.window)
                    # the decoration
                    if deco2:
                        deco = deco2
                # the decoration
                else:
                    win2 = self.find_win_of_deco(event.window)
                    if win2:
                        win = win2
                        deco = event.window
                #
                if win:
                    # with decoration
                    if self.DECO_WIN[win]:
                        self.DECO_WIN[win].destroy()
                        del self.DECO_WIN[win]
                    # without decoration
                    else:
                        del self.DECO_WIN[win]
                    #
                    if win in self.all_windows:
                        self.all_windows.remove(win)
                        self._update_client_list()
                    #
                    if win in self.all_windows_stack:
                        self.all_windows_stack.remove(win)
                        self._update_client_list_stack()
                    #
                    if win in self.window_in_fullscreen_state:
                        self.window_in_fullscreen_state = []
                    if win in self.window_in_fullscreen_state_CM:
                        self.window_in_fullscreen_state_CM = []
                    #
                    self._find_and_update_the_active(win)
            #
            elif event.type == X.MotionNotify:
                #### window resizing
                if self.mouse_button_left and self.btn1_drag:
                    if not self.delta_drag_start_point:
                        continue
                    #
                    x = event.root_x
                    y = event.root_y
                    #
                    ddeco = None
                    wwin = None
                    #
                    wwin = self.find_win_of_deco(self.btn1_drag)
                    if wwin:
                        ddeco = self.btn1_drag
                    else:
                        wwin = self.btn1_drag
                    #
                    dgeom = self.btn1_drag.get_geometry()
                    dwidth = dgeom.width
                    dheight = dgeom.height
                    dx = dgeom.x
                    dy = dgeom.y
                    #
                    # right
                    if self.mouse_button_left == 1:
                        ww = self.window_resize_geometry[2] + (x-self.mouse_button_resize_drag_start_point[0])
                        hh = self.window_resize_geometry[3] + (y-self.mouse_button_resize_drag_start_point[1])
                        #
                        # min size of the window
                        if ww > 75 or hh > 75:
                            if ddeco:
                                ddeco.configure(width=ww, height=hh)
                                wwin.configure(width=ww-BORDER_WIDTH*2, height=hh-BORDER_WIDTH*2-TITLE_HEIGHT)
                            elif wwin:
                                wwin.configure(width=ww, height=hh)
                    #
                    # # left
                            # ww = self.window_resize_geometry[2] + (x-self.mouse_button_resize_drag_start_point[0])
                            # hh = self.window_resize_geometry[3] + (y-self.mouse_button_resize_drag_start_point[1])
                            # #
                            # # min size
                            # if ww > 75 or hh > 75:
                                # if deco:
                                    # deco.configure(x=x-ww ,y=y+hh, width=ww, height=hh)
                                    # # win.configure(width=ww-BORDER_WIDTH*2, height=hh-BORDER_WIDTH*2-TITLE_HEIGHT)
                    #
                    continue
                #### dragging
                if self.mouse_button_left and self.grabbed_window_btn1:
                    x = event.root_x
                    y = event.root_y
                    #
                    ddeco = None
                    wwin = None
                    #
                    if self.grabbed_window_btn1 in self.DECO_WIN:
                        wwin = self.grabbed_window_btn1
                        ddeco = self.DECO_WIN[self.grabbed_window_btn1]
                    else:
                        wwin = self.find_win_of_deco(self.grabbed_window_btn1)
                        if wwin:
                            ddeco = self.grabbed_window_btn1
                    #
                    if wwin == None and ddeco == None:
                        # transient
                        for iitem in self.transient_windows:
                            if self.transient_windows[iitem] == self.grabbed_window_btn1:
                                wwin = self.grabbed_window_btn1
                                break
                    #
                    if not self.delta_drag_start_point:
                        continue
                    #
                    if self.mouse_button_left == 1:
                        if (y - self.delta_drag_start_point[1]) <= start_y:
                            continue
                    #
                    if ddeco and wwin:
                        ddeco.configure(x=x - self.delta_drag_start_point[0], y=y - self.delta_drag_start_point[1])
                        wwin.configure(x=x - self.delta_drag_start_point[0] + BORDER_WIDTH+BORDER_WIDTH2, y=y - self.delta_drag_start_point[1]+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                    elif wwin:
                        wwin.configure(x=x - self.delta_drag_start_point[0], y=y - self.delta_drag_start_point[1])
                    #
                    continue
            #
            elif event.type == X.KeyPress:
                # on root
                if event.child == None:
                    continue
                #
                _is_active = 0
                if event.child in self.DECO_WIN:
                    if event.child == self.active_window:
                        _is_active = 1
                        self.key_press_window = event.child
                else:
                    win = self.find_win_of_deco(event.child)
                    if win:
                        _is_active = 1
                        self.key_press_window = event.child
                # transient
                for iitem in self.transient_windows:
                    if self.transient_windows[iitem] == event.child:
                        _is_active = 1
                        self.key_press_window = event.child
                        break
                #
                if _is_active:
                    self.key_press_window.grab_button(1, X.AnyModifier, True,
                        X.ButtonPressMask|X.ButtonReleaseMask, X.GrabModeAsync,
                        X.GrabModeAsync, X.NONE, X.NONE)
                    #
                    if RESIZE_WITH_KEY:
                        self.key_press_window.grab_button(3, X.AnyModifier, True,
                            X.ButtonPressMask|X.ButtonReleaseMask, X.GrabModeAsync,
                            X.GrabModeAsync, X.NONE, X.NONE)
                #
                if event.state & X.Mod4Mask:
                    # close active window
                    if event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_CC)):
                        if self.active_window:
                            active = self.display.get_input_focus().focus
                            self.close_window(active)
                    # maximize active window
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_MM)):
                        if event.child in self.DECO_WIN:
                            win = event.child
                        win2 = self.find_win_of_deco(event.child)
                        if win2 in self.DECO_WIN:
                            win = win2
                        self.maximize_window(win)
                    # minimize the active window
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_MN)):
                        if event.child in self.DECO_WIN:
                            win = event.child
                        win2 = self.find_win_of_deco(event.child)
                        if win2 in self.DECO_WIN:
                            win = win2
                        self.minimize_window(win, 3)
                    # resize - down
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_RS)):
                        if event.child in self.DECO_WIN:
                            cdeco = self.DECO_WIN[event.child]
                            if cdeco:
                                cdgeom = cdeco.get_geometry()
                                cdeco.configure(height=cdgeom.height+10)
                            #
                            cgeom = event.child.get_geometry()
                            event.child.configure(height=cgeom.height+10)
                    # resize - up
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_RW)):
                        if event.child in self.DECO_WIN:
                            cdeco = self.DECO_WIN[event.child]
                            if cdeco:
                                cdgeom = cdeco.get_geometry()
                                cdeco.configure(height=cdgeom.height-10)
                            #
                            cgeom = event.child.get_geometry()
                            event.child.configure(height=cgeom.height-10)
                    # resize - right
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_RD)):
                        if event.child in self.DECO_WIN:
                            cdeco = self.DECO_WIN[event.child]
                            if cdeco:
                                cdgeom = cdeco.get_geometry()
                                cdeco.configure(width=cdgeom.width+10)
                            #
                            cgeom = event.child.get_geometry()
                            event.child.configure(width=cgeom.width+10)
                    # resize - left
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_RA)):
                        if event.child in self.DECO_WIN:
                            cdeco = self.DECO_WIN[event.child]
                            if cdeco:
                                cdgeom = cdeco.get_geometry()
                                cdeco.configure(width=cdgeom.width-10)
                            #
                            cgeom = event.child.get_geometry()
                            event.child.configure(width=cgeom.width-10)
                    # execute terminal
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_EXEC_TERM)):
                        if shutil.which(_TERMINAL):
                            subprocess.Popen([_TERMINAL])
                    # exit
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_EXIT)):
                        return
                    # custom commands
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_C1)):
                        if COMM_1:
                            if shutil.which(COMM_1):
                                subprocess.Popen([COMM_1])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_C2)):
                        if COMM_2:
                            if shutil.which(COMM_2):
                                subprocess.Popen([COMM_2])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_C3)):
                        if COMM_3:
                            if shutil.which(COMM_3):
                                subprocess.Popen([COMM_3])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_C4)):
                        if COMM_4:
                            if shutil.which(COMM_4):
                                subprocess.Popen([COMM_4])
            #
            elif event.type == X.CirculateRequest:
                print("circulate req")
            #
            elif event.type == X.KeyRelease:
                # on root
                if event.child == X.NONE or event.child == None or event.child == self.root:
                    if not self.key_press_window:
                        continue
                # 
                if self.key_press_window:
                    self.key_press_window.ungrab_button(1, X.AnyModifier)
                    if RESIZE_WITH_KEY:
                        self.key_press_window.ungrab_button(3, X.AnyModifier)
            # 
            elif event.type == X.ButtonPress:
                # child is the window or deco
                _QP_DATA = self.root.query_pointer()
                # could be root
                if event.window == None or event.window == X.NONE:
                    continue
                # 
                if _QP_DATA.child == 0:
                    continue
                #
                if event.state & X.Mod4Mask:
                    if event.detail == 1:
                        # skip fullscreen windows
                        if self.window_in_fullscreen_state:
                            continue
                        if self.window_in_fullscreen_state_CM:
                            continue
                        ########### drag with super ###########
                        # do not skip window in back
                        #
                        pdatawin = _QP_DATA.child
                        wwin = None
                        ddeco = None
                        if pdatawin in self.DECO_WIN:
                            wwin = pdatawin
                            ddeco = self.DECO_WIN[pdatawin]
                        else:
                            wwin = self.find_win_of_deco(pdatawin)
                            if wwin:
                                ddeco = pdatawin
                        #
                        if wwin == None and ddeco == None:
                            # transient
                            for iitem in self.transient_windows:
                                if self.transient_windows[iitem] == pdatawin:
                                    wwin = pdatawin
                                    break
                        #
                        if wwin:
                            self.grabbed_window_btn1 = wwin
                            if ddeco:
                                self.grabbed_window_btn1 = ddeco
                            self.mouse_button_left = 11
                            self.grabbed_window_btn1.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                        X.GrabModeAsync, X.NONE, X.NONE, 0)
                            #
                            geom = self.grabbed_window_btn1.get_geometry()
                            cx = geom.x
                            cy = geom.y
                            x = event.root_x
                            y = event.root_y
                            self.delta_drag_start_point = (x - cx, y - cy)
                            continue
                    ##### resize with super
                    elif event.detail == 3:
                        pdatawin = _QP_DATA.child
                        wwin = None
                        ddeco = None
                        if pdatawin in self.DECO_WIN:
                            wwin = pdatawin
                            ddeco = self.DECO_WIN[pdatawin]
                        else:
                            decotemp = self.find_win_of_deco(pdatawin)
                            if decotemp:
                                ddeco = pdatawin
                                wwin = decotemp
                        #
                        if not ddeco:
                            ddeco = wwin
                        # it could be transient
                        if not wwin:
                            continue
                        dgeom = ddeco.get_geometry()
                        dpos = dgeom.root.translate_coords(ddeco.id, 0, 0)
                        dx = dpos.x
                        dy = dpos.y
                        cx = dgeom.x
                        cy = dgeom.y
                        dw = dgeom.width
                        dh = dgeom.height
                        ex = event.root_x
                        ey = event.root_y
                        # decoration, otherwise window
                        self.btn1_drag = ddeco
                        # decoration, otherwise window
                        self.grabbed_window_btn1 = ddeco
                        self.mouse_button_left = 1
                        self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                X.GrabModeAsync, X.NONE, X.NONE, 0)
                        #
                        self.window_resize_geometry = (dx, dy, dw, dh)
                        self.mouse_button_resize_drag_start_point = (ex, ey)
                        self.delta_drag_start_point = (ex - cx, ey - cy)
                        #
                        continue
                        
                ##########
                #
                if event.detail == 1:
                    #
                    if _QP_DATA.root == self.root:
                        pdatawin = _QP_DATA.child
                        wwin = None
                        ddeco = None
                        if pdatawin in self.DECO_WIN:
                            wwin = pdatawin
                            ddeco = self.DECO_WIN[pdatawin]
                        else:
                            decotemp = self.find_win_of_deco(pdatawin)
                            if decotemp:
                                ddeco = pdatawin
                                wwin = decotemp
                        #
                        _bring_to_front = 0
                        # skip window at back
                        if wwin != self.active_window:
                            _bring_to_front = 1
                            # continue
                        if ddeco != None and _bring_to_front == 0:
                            dgeom = ddeco.get_geometry()
                            # decoration starting x and y without borders
                            dpos = dgeom.root.translate_coords(ddeco.id, 0, 0)
                            dx = dpos.x
                            dy = dpos.y
                            cx = dgeom.x
                            cy = dgeom.y
                            dw = dgeom.width
                            dh = dgeom.height
                            ex = event.root_x
                            ey = event.root_y
                            ######## decoration buttons #############
                            # close button
                            if (dx+dw-BORDER_WIDTH-self.deco_btn_width) < ex < (dx+dw-BORDER_WIDTH):
                                if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                    continue
                            # maximize button
                            elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*2-BTN_SPACE) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE-self.deco_btn_width):
                                if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                    # wwin = self.find_win_of_deco(ddeco)
                                    if wwin in self.DECO_WIN:
                                        continue
                            # minimize button
                            elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*3-BTN_SPACE*2) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE*2-self.deco_btn_width*2):
                                if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                    continue
                            ############## resizing - bottom right ###############
                            elif (cx+dw-40) <= ex <= (cx+dw):
                                if (cy+dh-40) <= ey <= (cy+dh):
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    continue
                            ############## DRAG - decoration #############
                            else:
                                # skip window at back
                                # TO DO: make wwin active and drag
                                if wwin != self.active_window:
                                    continue
                                #
                                self.grabbed_window_btn1 = ddeco
                                self.mouse_button_left = 1
                                self.grabbed_window_btn1.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                #
                                geom = self.grabbed_window_btn1.get_geometry()
                                cx = geom.x
                                cy = geom.y
                                x = event.root_x
                                y = event.root_y
                                self.delta_drag_start_point = (x - cx, y - cy)
                                #
                                continue
                        #
                        ################ window to front #############
                        if _bring_to_front == 1:
                            #
                            for iitem in self.transient_windows:
                                if self.transient_windows[iitem] == pdatawin:
                                    wwin = iitem
                                    ddeco = self.DECO_WIN[iitem]
                                    break
                                #
                            #
                            if wwin:
                                if ddeco:
                                    ddeco.raise_window()
                                #
                                wwin.raise_window()
                                #
                                self._activate_window(wwin, ddeco, 0)
                        continue
            #
            elif event.type == X.ButtonRelease:
                # child is the window or deco
                _QP_DATA = self.root.query_pointer()
                ######## decoration buttons
                if event.detail == 1:
                    #
                    pdatawin = _QP_DATA.child
                    wwin = None
                    ddeco = None
                    if pdatawin in self.DECO_WIN:
                        wwin = pdatawin
                        ddeco = self.DECO_WIN[pdatawin]
                    else:
                        decotemp = self.find_win_of_deco(pdatawin)
                        if decotemp:
                            ddeco = pdatawin
                            wwin = decotemp
                    #
                    if ddeco:
                        dgeom = ddeco.get_geometry()
                        # decoration starting x and y without borders
                        dpos = dgeom.root.translate_coords(ddeco.id, 0, 0)
                        dx = dpos.x
                        dy = dpos.y
                        dw = dgeom.width
                        dh = dgeom.height
                        ex = event.root_x
                        ey = event.root_y
                        # close button
                        if (dx+dw-BORDER_WIDTH-self.deco_btn_width) < ex < (dx+dw-BORDER_WIDTH):
                            if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                self.close_window(wwin)
                                continue
                        # maximize button
                        elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*2-BTN_SPACE) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE-self.deco_btn_width):
                            if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                wwin = self.find_win_of_deco(ddeco)
                                if wwin in self.DECO_WIN:
                                    self.maximize_window(wwin)
                                continue
                        # minimize button
                        elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*3-BTN_SPACE*2) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE*2-self.deco_btn_width*2):
                            if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                wwin = self.find_win_of_deco(ddeco)
                                if wwin in self.DECO_WIN:
                                    self.minimize_window(wwin, 3)
                                continue
                #
                # window resizing
                if self.btn1_drag:
                    self.btn1_drag = None
                    self.window_resize_geometry = None
                    self.mouse_button_resize_drag_start_point = None
                # put window in front - reset
                if self.grabbed_window_btn1:
                    self.mouse_button_left = 0
                    self.delta_drag_start_point = None
                    self.grabbed_window_btn1.ungrab_button(1, X.AnyModifier)
                    if RESIZE_WITH_KEY:
                        self.grabbed_window_btn1.ungrab_button(3, X.AnyModifier)
                    #
                    self.grabbed_window_btn1 = None
                    #
                    self.display.ungrab_pointer(X.CurrentTime)
                    continue
            #
            elif event.type == X.PropertyNotify:
                if event.window == X.NONE or event.window == None:
                    continue
                #
                if event.atom == self.NET_ACTIVE_WINDOW:
                    print("ACTIVE WINDOW CHANGED")
                    continue
                #
                elif event.atom == self.NET_LIST_STACK:
                    print("LIST STACK CHANGED")
                    continue
                #
                elif event.atom == self.NET_LIST:
                    print("LIST CHANGED")
                    continue
            #
            elif event.type == X.ClientMessage:
                #
                if event.client_type == self.display.intern_atom("_NET_WM_MOVERESIZE"):
                    fmt, data = event.data
                    if fmt == 32:
                        # move using mouse
                        if data[2] == 8:
                            self.grabbed_window_btn1 = deco
                            self.mouse_button_left = 1
                            event.window.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                        X.GrabModeAsync, X.NONE, X.NONE, 0)
                            #
                            x = data[0]
                            y = data[1]
                            self.mouse_button_left = 1
                            #
                            self.grabbed_window_btn1 = event.window
                            geom = self.grabbed_window_btn1.get_geometry()
                            cx = geom.x
                            cy = geom.y
                            self.delta_drag_start_point = (x - cx, y - cy)
                            ########
                        # resize at bottom-right
                        elif data[2] == 4:
                            self.btn1_drag = event.window
                            self.grabbed_window_btn1 = event.window
                            self.mouse_button_left = 1
                            event.window.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                    X.GrabModeAsync, X.NONE, X.NONE, 0)
                            geom = self.grabbed_window_btn1.get_geometry()
                            cx = geom.x
                            cy = geom.y
                            x = data[0]
                            y = data[1]
                            self.window_resize_geometry = (geom.x, geom.y, geom.width, geom.height)
                            self.mouse_button_resize_drag_start_point = (x, y)
                            self.delta_drag_start_point = (x - cx, y - cy)
                        # terminate
                        elif data[2] == 11:
                            if self.btn1_drag:
                                self.btn1_drag = None
                                self.window_resize_geometry = None
                                self.mouse_button_resize_drag_start_point = None
                            #
                            if self.grabbed_window_btn1:
                                self.mouse_button_left = 0
                                self.delta_drag_start_point = None
                                self.grabbed_window_btn1.ungrab_button(1, X.AnyModifier)
                                #
                                self.grabbed_window_btn1 = None
                                #
                                self.display.ungrab_pointer(X.CurrentTime)
                                #
                    #
                    continue
                #
                if event.client_type == self.display.intern_atom("_NET_RESTACK_WINDOW"):
                    print("** cl restack")
                    continue
                #
                if event.client_type == self.NET_ACTIVE_WINDOW:
                    fmt, data = event.data
                    #
                    if fmt == 32 and data[0] in [1,2]:
                        win = None
                        dwin = None
                        if event.window in self.DECO_WIN:
                            win = event.window
                            dwin = self.DECO_WIN[win]
                            # restore from minimize eventually
                            ret = self.minimize_window(win, 77)
                            if ret:
                                self._activate_window(win, dwin, 0)
                    continue
                #
                if event.client_type == self.WM_CHANGE_STATE:
                    fmt, data = event.data
                    # WithdrawnState 0 - NormalState 1 - IconicState 3
                    if fmt == 32:
                        if data[0] == 3 or data[0] == 0:
                            self.minimize_window(event.window, data[0])
                        elif data[0] == 1:
                            self.minimize_window(event.window, data[0])
                    #
                    continue
                #
                if event.client_type == self.NET_WM_STATE:
                    fmt, data = event.data
                    # maximize
                    if fmt == 32 and data[1] == self.WM_MAXIMIZED_VERT and data[2] == self.WM_MAXIMIZED_HORZ:
                        # 1 add - 2 toggle
                        if data[0] == 1 or data[0] == 2:
                            self.maximize_window(event.window)
                        # 0 remove
                        elif data[0] == 0:
                            self.maximize_window(event.window)
                    # 
                    elif fmt == 32 and data[1] == self.WM_HIDDEN:
                        #
                        if data[0] == 2 or data[0] == 1:
                            self.minimize_window(event.window, data[0])
                        elif data[0] == 0:
                            self.minimize_window(event.window, data[0])
                            #
                    # fullscreen
                    elif fmt == 32 and data[1] == self.WM_FULLSCREEN:
                        if data[0] in [0,1,2]:
                            self.fullscreen_window(event.window, data[0])
                    #
                    # demands attention - WM_HINTS.flags property of window - set_wm_hints
                    elif fmt == 32 and data[1] == self.STATE_DEMANDS_ATTENTION:
                        if data[0] == 1:
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            hints['flags'] |= Xutil.UrgencyHint
                            event.window.set_wm_hints(hints)
                            hints = event.window.get_wm_hints()
                            self.display.flush()
                        elif data[0] == 0:
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            hints['flags'] &= ~Xutil.UrgencyHint
                            event.window.set_wm_hints(hints)
                            self.display.flush()
                            hints = event.window.get_wm_hints()
                        # toggle urgency
                        elif data[0] == 2:
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            if hints['flags'] & Xutil.UrgencyHint:
                                hints['flags'] &= ~Xutil.UrgencyHint
                                event.window.set_wm_hints(hints)
                                self.display.flush()
                            else:
                                hints = event.window.get_wm_hints() or { 'flags': 0 }
                                hints['flags'] |= Xutil.UrgencyHint
                                event.window.set_wm_hints(hints)
                                hints = event.window.get_wm_hints()
                                self.display.flush()
                    #
                    continue
                #
                if event.client_type == self.display.intern_atom("WM_DELETE_WINDOW"):
                    if event.window in self.DECO_WIN:
                        self.close_window(event.window)
                    continue
                #
                if event.client_type == self.display.intern_atom("_NET_CLOSE_WINDOW"):
                    if event.window in self.DECO_WIN:
                        # fmt, data = event.data
                        # # 1 from application - 2 from pagers and others
                        # if fmt == 32 and data[1] == 2:
                            # ddeco = self.DECO_WIN[event.window]
                            # if ddeco:
                                # ddeco.destroy()
                            # event.window.destroy()
                        # else:
                        self.close_window(event.window)
                    #
                    continue
                #
                # Somebody wants to tell us something
                if event.client_type == self.WM_PROTOCOLS:
                    fmt, data = event.data
                    if fmt == 32 and data[0] == self.WM_DELETE_WINDOW:
                        if event.window in self.DECO_WIN:
                            self.close_window(event.window)
                    #
                    continue
                # another WM wants to take the ownership
                if event.client_type == self.display.intern_atom("MANAGER"):
                    # num WM_S0 num 0 0
                    fmt, data = event.data
                    if fmt == 32:
                        if data[1] == self.WM_S:
                            # if self.display.get_selection_owner(self.WM_S) == 0 or self.display.get_selection_owner != self._window:
                                # self._window.set_selection_owner(X.NONE, X.CurrentTime)
                                # for ww in [self.root, self._window]:
                                    # ww.change_property(self.display.get_atom('_NET_SUPPORTING_WM_CHECK'),
                                        # Xatom.WINDOW,32,[X.NONE])
                                # # #
                                # # self._window.destroy()
                                # # os.kill(_THIS_PID, 9)
                                # return
                            #
                            continue
            #
            elif event.type == X.ConfigureRequest:
                #
                if event.window == None or event.window == self.root:
                    continue
                #
                window = event.window
                x = max(event.x, start_x)
                y = max(event.y, start_y)
                #
                ew_type = None
                ew_type = self.get_window_type(event.window)
                if ew_type:
                    ew_name = self.display.get_atom_name(ew_type[0])
                    if ew_name == '_NET_WM_WINDOW_TYPE_DOCK':
                        x = event.x
                        y = event.y
                    elif ew_name == '_NET_WM_WINDOW_TYPE_DESKTOP':
                        x = 0
                        y = 0
                #
                width, height = event.width, event.height
                #
                if NO_DECO == 1:
                    window.configure(x=x, y=y, width=width, height=height)
                    continue
                #
                window.configure(x=x, y=y, width=width, height=height)
                if window in self.DECO_WIN:
                    if self.DECO_WIN[window]:
                        # #
                        # # # window restore from fullscreen state
                        # if self.window_in_fullscreen_state:
                            # if event.window == self.window_in_fullscreen_state[0]:
                                # if event.sequence_number == self.window_in_fullscreen_state[1]:
                                    # continue
                                # if width == screen_width and height == screen_height:
                                    # self.window_in_fullscreen_state = []
                                    # continue
                                # #
                                # event.window.configure(x=x, y=y, width=width, height=height)
                                # if self.DECO_WIN[event.window]:
                                    # # self.DECO_WIN[event.window].map()
                                    # self.DECO_WIN[event.window].raise_window()
                                # #
                                # event.window.raise_window()
                                # if self.DECO_WIN[event.window]:
                                    # self.DECO_WIN[event.window].map()
                                # #
                                # # self.window_in_fullscreen_state = []
                                # continue
                        # #
                        # # into fullscreen
                        # if width == screen_width and height == screen_height:
                            # if self.window_in_fullscreen_state_CM:
                                # continue
                            # # skip unwanted request - mpv
                            # if self.window_in_fullscreen_state:
                                # if event.window == self.window_in_fullscreen_state[0]:
                                    # continue
                            # #######
                            # if event.window in self.DECO_WIN:
                                # if self.DECO_WIN[event.window]:
                                    # self.DECO_WIN[event.window].unmap()
                            # event.window.raise_window()
                            # event.window.configure(x=0, y=0, width=screen_width, height=screen_height)
                            # self.window_in_fullscreen_state = [event.window, event.sequence_number]
                            # continue
                        # #
                        # else:
                            #
                        self.DECO_WIN[event.window].configure(x=x-BORDER_WIDTH-BORDER_WIDTH2, y=y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2, 
                                width=width+BORDER_WIDTH+BORDER_WIDTH2, height=height+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
            #
            if not _is_running:
                return
        
    
    def on_supported_attributes(self):
        attributes = [
            '_NET_SUPPORTED',
            '_NET_ACTIVE_WINDOW',
            '_NET_CLIENT_LIST',
            '_NET_CLIENT_LIST_STACKING',
            '_NET_WM_STATE',
            '_NET_WM_MOVERESIZE',
            '_NET_CLOSE_WINDOW',
            '_NET_RESTACK_WINDOW',
            '_NET_WM_ACTION_MOVE',
            '_NET_WM_ACTION_RESIZE',
            '_NET_WM_ACTION_MINIMIZE',
            '_NET_WM_ACTION_MAXIMIZE_VERT',
            '_NET_WM_ACTION_MAXIMIZE_HORZ',
            '_NET_WM_ACTION_FULLSCREEN',
            '_NET_WM_ACTION_ABOVE',
            '_NET_WM_ACTION_BELOW',
            '_NET_WM_ACTION_STICK',
            '_NET_WM_STRUT_PARTIAL',
            '_NET_WM_STRUT',
            '_NET_WM_STATE_FULLSCREEN',
            '_NET_WM_STATE_MAXIMIZE_VERT',
            '_NET_WM_STATE_MAXIMIZE_HORZ',
            '_NET_WM_STATE_ABOVE',
            '_NET_WM_STATE_BELOW',
            '_NET_SUPPORTING_WM_CHECK',
            '_NET_WM_ACTION_CLOSE',
            '_NET_WM_ALLOWED_ACTIONS',
            '_NET_WM_ICON',
            '_NET_WM_NAME',
            '_NET_WM_PID',
            '_NET_WM_STATE_DEMANDS_ATTENTION',
            '_NET_WM_WINDOW_TYPE',
            '_NET_WM_WINDOW_TYPE_DESKTOP',
            '_NET_WM_WINDOW_TYPE_DIALOG',
            '_NET_WM_WINDOW_TYPE_DOCK',
            '_NET_WM_WINDOW_TYPE_MENU',
            '_NET_WM_WINDOW_TYPE_NORMAL',
            '_NET_WM_WINDOW_TYPE_SPLASH',
            '_NET_WM_WINDOW_TYPE_TOOLBAR',
            '_NET_WM_WINDOW_TYPE_UTILITY',
            '_NET_WORKAREA',
            '_NET_DESKTOP_GEOMETRY',
            '_NET_NUMBER_OF_DESKTOPS',
            '_NET_DESKTOP_VIEWPORT',
            '_NET_CURRENT_DESKTOP',
            '_NET_DESKTOP_NAMES',
            'WM_S0',
            'MANAGER',
            'WM_DELETE_WINDOW',
        ]
        self.root.change_property(
            self.display.get_atom('_NET_SUPPORTED'),
            Xatom.ATOM,
            32,
            [self.display.get_atom(x) for x in attributes],)
        
    def _update_client_list(self):
        self.root.change_property(
            self.display.get_atom('_NET_CLIENT_LIST'),
            Xatom.WINDOW,
            32,
            [window.id for window in self.all_windows],)
        
    def _update_client_list_stack(self):
        self.root.change_property(
            self.display.get_atom('_NET_CLIENT_LIST_STACKING'),
            Xatom.WINDOW,
            32,
            [window.id for window in self.all_windows_stack],)
        
    def _update_active_window(self, win):
        if win:
            win_id = win.id
        else:
            win_id = X.NONE
        self.root.change_property(
            self.display.get_atom('_NET_ACTIVE_WINDOW'),
            Xatom.WINDOW,
            32,
            [win_id])
    
    def fullscreen_window(self, win, _type):
        # _type = 2 is toggle
        if win in self.DECO_WIN:
            # window x y width height sequence_number
            if self.window_in_fullscreen_state_CM:
                if win in self.DECO_WIN:
                    deco = self.DECO_WIN[win]
                    (wwin,wx,wy,ww,wh) = self.window_in_fullscreen_state_CM
                    if wwin == win:
                        #
                        if deco:
                            # deco.map()
                            deco.raise_window()
                        #
                        win.configure(x=wx,y=wy,width=ww,height=wh)
                        win.map()
                        win.raise_window()
                        if deco:
                            deco.map()
                        self.window_in_fullscreen_state_CM = []
            else:
                wgeom = win.get_geometry()
                self.window_in_fullscreen_state_CM = [win, wgeom.x, wgeom.y, wgeom.width, wgeom.height]
                deco = self.DECO_WIN[win]
                #
                if deco:
                    deco.unmap()
                #
                win.configure(x=0-BORDER_WIDTH,y=0-BORDER_WIDTH,width=screen_width+BORDER_WIDTH,height=screen_height+BORDER_WIDTH)
                
    
    #
    def close_window(self, win):
        _DELETE_PROTOCOL = 0
        #
        protc = win.get_wm_protocols()
        if protc:
            for iitem in protc.tolist():
                if iitem == self.WM_DELETE_WINDOW:
                    _DELETE_PROTOCOL = 1
                    break
        #
        if _DELETE_PROTOCOL == 0:
            ppid = self.getProp(win, 'PID')
            if ppid:
                # 9 signal.SIGKILL - 15 signal.SIGTERM
                os.kill(ppid[0], 15)
                return
            #
            win.kill_client()
            return
        #
        active = win
        c_type1 = self.WM_DELETE_WINDOW
        c_type = self.WM_PROTOCOLS
        data = (32, [c_type1, 0,0,0,0])
        sevent = protocol.event.ClientMessage(
        window = active,
        client_type = c_type,
        data = data
        )
        self.display.send_event(win, sevent)
        # self.display.flush()
        self.display.sync()
    
    
    # activate the window by request - win deco type
    def _activate_window(self, win, dwin, _type):
        if win:
            # the old active window
            if self.active_window:
                if self.DECO_WIN[self.active_window]:
                    self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                    # self.display.sync()
                    self.DECO_WIN[self.active_window].grab_button(1, X.AnyModifier, True,
                                X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                X.GrabModeAsync, X.NONE, X.NONE)
                    self.display.sync()
                else:
                    self.active_window.change_attributes(border_pixel=border_color2)
                #
                self.active_window.grab_button(1, X.AnyModifier, True,
                        X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                        X.GrabModeAsync, X.NONE, X.NONE)
                self.display.sync()
                #
                if self.active_window in self.transient_windows:
                    w_tr = self.transient_windows[self.active_window]
                    w_tr.grab_button(1, X.AnyModifier, True,
                            X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                            X.GrabModeAsync, X.NONE, X.NONE)
                    #
                    self.display.sync()
            #
            ############
            # the new active window
            self.active_window = win
            #
            self.grabbed_window_btn1 = self.active_window
            #
            if self.active_window in self.all_windows_stack:
                self.all_windows_stack.remove(self.active_window)
                self.all_windows_stack.append(self.active_window)
                self._update_client_list_stack()
            #
            if dwin:
                dwin.change_attributes(border_pixel=border_color1)
                dwin.ungrab_button(1, X.AnyModifier)
                self.display.sync()
            else:
                self.active_window.change_attributes(border_pixel=border_color1)
            self.active_window.ungrab_button(1, X.AnyModifier)
            self.display.sync()
            #
            if dwin:
                # unmap to avoid something from deco
                dwin.unmap()
                dwin.raise_window()
            #
            self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
            self.active_window.raise_window()
            # to avoid something from deco
            if dwin:
                dwin.map()
            # its transient
            if self.active_window in self.transient_windows:
                w_tr = self.transient_windows[self.active_window]
                w_tr.raise_window()
                w_tr.change_attributes(border_pixel=border_color2)
                # self.display.sync()
                w_tr.ungrab_button(1, X.AnyModifier)
            #
            self.display.sync()
            #
            self._update_active_window(self.active_window)

    
    # find a window to set as active
    # after destroy and mini/maximize
    def _find_and_update_the_active(self, win):
        # the active window closed or minimized
        if win == self.active_window:
            #
            if self.active_window in self.DECO_WIN:
                if self.DECO_WIN[self.active_window]:
                    self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                    self.display.sync()
                    self.DECO_WIN[self.active_window].grab_button(1, X.AnyModifier, True,
                                X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                X.GrabModeAsync, X.NONE, X.NONE)
                else:
                    self.active_window.change_attributes(border_pixel=border_color2)
                #
                self.active_window.grab_button(1, X.AnyModifier, True,
                            X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                            X.GrabModeAsync, X.NONE, X.NONE)
                # self.display.sync()
                #
                # its transient
                if self.active_window in self.transient_windows:
                    w_tr = self.transient_windows[self.active_window]
                    w_tr.change_attributes(border_pixel=border_color2)
            #
            self.active_window = None
            #####
            # find another suitable window to set as active
            if len(self.all_windows_stack) > 0:
                _has_been_found = 0
                for iitem in self.all_windows_stack[::-1]:
                    # skip desktop and docks
                    if iitem in self.dock_windows:
                        continue
                    if iitem in self.desktop_window:
                        continue
                    # skip minimized windows
                    try:
                        if hasattr(iitem.get_wm_state(), "state"):
                            if iitem.get_wm_state().state == 0:
                                continue
                    except:
                        pass
                    #
                    if iitem in self.DECO_WIN:
                        if iitem == win:
                            continue
                        #
                        _has_been_found = 1
                        #
                        if self.DECO_WIN[iitem]:
                            self.DECO_WIN[iitem].change_attributes(border_pixel=border_color1)
                        else:
                            iitem.change_attributes(border_pixel=border_color1)
                        #
                        self.active_window = iitem
                        #
                        if self.DECO_WIN[iitem]:
                            self.DECO_WIN[iitem].ungrab_button(1, X.AnyModifier)
                            # unmap to avoid something from deco
                            self.DECO_WIN[iitem].unmap()
                            self.DECO_WIN[iitem].raise_window()
                        # else:
                            # iitem.ungrab_button(1, X.AnyModifier)
                        #
                        self.active_window.ungrab_button(1, X.AnyModifier)
                        #
                        self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                        self.active_window.raise_window()
                        # to avoid something from deco
                        if self.DECO_WIN[iitem]:
                            self.DECO_WIN[iitem].map()
                        self.display.sync()
                        #
                        if self.active_window in self.all_windows_stack:
                            self.all_windows_stack.remove(iitem)
                        self.all_windows_stack.append(iitem)
                        self._update_client_list_stack()
                        #
                        self._update_active_window(self.active_window)
                        # its transient window
                        if self.active_window in self.transient_windows:
                            w_tr = self.transient_windows[self.active_window]
                            w_tr.raise_window()
                            w_tr.ungrab_button(1, X.AnyModifier)
                        #
                        break
                #
                if _has_been_found == 0:
                    self.active_window = None
                    self._update_active_window(X.NONE)
                        
    
    # windows in miniimized state: window:[deco]
    def minimize_window(self, win, ttype):
        # minimize
        if ttype == 3 or ttype == 0 or ttype == 2 or ttype == 1:
            if not win in self.MINIMIZED_WINDOWS:
                if win in self.DECO_WIN:
                    deco = self.DECO_WIN[win]
                    # Xutil.WithdrawnState, Xutil.NormalState, Xutil.IconicState
                    win.set_wm_state(state = Xutil.WithdrawnState, icon = X.NONE)
                    self.display.sync()
                    # set the hidden state
                    win.change_property(
                        self.NET_WM_STATE,
                        self.WM_HIDDEN,
                        32,
                        [2],
                        X.PropModeReplace)
                    self.display.sync()
                    #
                    # if deco:
                        # deco.unmap()
                    self.MINIMIZED_WINDOWS[win] = deco
                    #
                    win.unmap()
                    # transient
                    if win in self.transient_windows:
                        self.transient_windows[win].unmap()
                    #
                    if win == self.active_window:
                        self._find_and_update_the_active(win)
                    return
        # unminimize
        if ttype == 1 or ttype == 2 or ttype == 3 or ttype == 77:
            if win in self.MINIMIZED_WINDOWS:
                deco = self.MINIMIZED_WINDOWS[win]
                if deco:
                    # deco.map()
                    deco.raise_window()
                    # self.display.sync()
                    # self.display.flush()
                win.map()
                win.raise_window()
                if deco:
                    deco.map()
                # set the hidden state
                win.change_property(
                    self.NET_WM_STATE,
                    self.WM_HIDDEN,
                    32,
                    [0],
                    X.PropModeReplace)
                self.display.sync()
                #
                del self.MINIMIZED_WINDOWS[win]
                # old active window
                if self.active_window:
                    if self.active_window in self.DECO_WIN:
                        if self.DECO_WIN[self.active_window]:
                            self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                            #
                            self.active_window.grab_button(1, X.AnyModifier, True,
                                                X.ButtonPressMask, X.GrabModeAsync,
                                                X.GrabModeAsync, X.NONE, X.NONE)
                        else:
                            self.active_window.grab_button(1, X.AnyModifier, True,
                                                X.ButtonPressMask, X.GrabModeAsync,
                                                X.GrabModeAsync, X.NONE, X.NONE)
                            self.active_window.change_attributes(border_pixel=border_color2)
                # new active window
                if self.DECO_WIN[win]:
                    # win.change_attributes(border_pixel=border_color1)
                    self.DECO_WIN[win].change_attributes(border_pixel=border_color1)
                    #self.display.flush()
                    # self.DECO_WIN[win].map()
                    # self.DECO_WIN[win].raise_window()
                else:
                    win.change_attributes(border_pixel=border_color1)
                self.display.flush()
                #
                win.ungrab_button(1, X.AnyModifier)
                win.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                #
                # win.map()
                # win.raise_window()
                #
                self.display.sync()
                #
                if win in self.all_windows_stack:
                    self.all_windows_stack.remove(win)
                self.all_windows_stack.append(win)
                self._update_client_list_stack()
                #
                self.active_window = win
                self._update_active_window(self.active_window)
                # its transient window
                if self.active_window in self.transient_windows:
                    w_tr = self.transient_windows[self.active_window]
                    w_tr.map()
                    w_tr.raise_window()
                    self.display.sync()
                # success
                return 0
            #
            else:
                return 1
                
    # windows in maximized state: window:[prev_win_x, prev_win_y, win_unmaximized_width, win_unmaximized_height]
    def maximize_window(self, win2):
        win = None
        deco = None
        if win2 in self.DECO_WIN:
            deco = self.DECO_WIN[win2]
            win = win2
        else:
            win = self.find_win_of_deco(win2)
            if win:
                deco = win2
        #
        if not win:
            return
        #
        if not win in self.MAXIMIZED_WINDOWS:
            wgeom = win.get_geometry()
            #
            self.MAXIMIZED_WINDOWS[win] = [wgeom.x, wgeom.y, wgeom.width, wgeom.height]
            #
            x = start_x
            y = start_y
            width1 = screen_width_usable
            height1 = screen_height_usable
            if deco:
                deco.unmap()
                deco.configure(x=x,y=y,width=width1-BORDER_WIDTH2*2,height=height1-BORDER_WIDTH2*2)
                win.configure(x=x+BORDER_WIDTH+BORDER_WIDTH2, y=y+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2, 
                    width=width1-BORDER_WIDTH*2-BORDER_WIDTH2*2, height=height1-TITLE_HEIGHT-BORDER_WIDTH*2-BORDER_WIDTH2*2)
                deco.map()
            else:
                win.configure(x=x, y=y, width=width1-BORDER_WIDTH2*2, height=height1-BORDER_WIDTH2*2)
        else:
            data = self.MAXIMIZED_WINDOWS[win]
            x = data[0]
            y = data[1]
            width = data[2]
            height = data[3]
            #
            if deco:
                deco.configure(x=x-BORDER_WIDTH-BORDER_WIDTH2,y=y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2,
                        width=width+BORDER_WIDTH+BORDER_WIDTH2,
                        height=height+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                win.configure(x=x,y=y,width=width,height=height)
            #
            else:
                win.configure(x=x-BORDER_WIDTH2,y=y-BORDER_WIDTH2,
                    width=width+BORDER_WIDTH2*2, height=height+BORDER_WIDTH2)
            #
            del self.MAXIMIZED_WINDOWS[win]
    
    
    def prog_execute(self, prog):
        try:
            # os.system("{} &".format(prog))
            subprocess.Popen(prog.split())
        except:
            pass
        
    def getProp(self, win, prop):
        try:
            prop = win.get_full_property(self.display.intern_atom('_NET_WM_' + prop), X.AnyPropertyType)
            if prop:
                return prop.value.tolist()
            return None
        except:
            return None
    
    def get_window_name(self, window):
        try:
            prop = window.get_full_property(self.display.intern_atom("_NET_WM_NAME"), X.AnyPropertyType)
            if prop:
                return prop.value.decode()
            else:
                prop = window.get_full_property(self.display.intern_atom("WM_NAME"), X.AnyPropertyType)
                if prop:
                    return prop.value.decode()
                else:
                    return "X"
                return "X"
        except:
            return "X"
    
    def get_window_class(self, window):
        try:
            cmd, cls = window.get_wm_class()
        except:
            return "X"
        if cls is not None:
            return cls
        else:
            return "X"
    
    def get_window_type(self, window):
        try:
            prop = window.get_full_property(self.display.get_atom("_NET_WM_WINDOW_TYPE"), X.AnyPropertyType)
            if prop:
                return prop.value.tolist()
            else:
                return 1
        except:
            return 1

        
    
    def prog_exit(self):
        global _is_running
        _is_running = 0
        self.display.close()
        sys.exit(0)
        
    

##############

x_wm()
    
            
