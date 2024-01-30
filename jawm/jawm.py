#!/usr/bin/env python3

# v. 20240130

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

# give the focus to the window under the pointer: 1 enable - 0 disable
SLOPPY_FOCUS = 0

# space between buttons
BTN_SPACE = 4

# size: 1 normal (29 px) - 2 big (36 px)
TITLEBAR_SIZE = 1

# decoration color: buttons need to be recolored if changed
DECO_COLOR = "#D2AE26"

# window manager actions: Super_L Alt_l Control_l
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
COMM_4 = "tint2"

##############

from Xlib.display import Display
from Xlib import X, XK, protocol, Xatom, Xutil
import sys, os, shutil
import subprocess
import signal
# import time
from PIL import Image
from ewmh import EWMH
ewmh = EWMH()

screen = Display().screen()
root = Display().screen().root


TITLE_HEIGHT = 0
if TITLEBAR_SIZE == 1:
    TITLE_HEIGHT = 29
elif TITLEBAR_SIZE == 2:
    TITLE_HEIGHT = 36
BTN_SIZE = TITLE_HEIGHT


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
        #
        mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask
                | X.EnterWindowMask | X.LeaveWindowMask | X.FocusChangeMask
                | X.ButtonPressMask | X.ButtonReleaseMask | X.PropertyChangeMask
                | X.KeyPressMask | X.KeyReleaseMask)
        #
        self.root.change_attributes(event_mask=mask)
        #
        self.root.grab_key(self.display.keysym_to_keycode(XK.string_to_keysym(_STATE)),
            X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync)
        #
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
        # windows that are dock type
        self.dock_windows = []
        # window with transient window: window:transient
        self.transient_windows = {}
        # only one can be in this state
        self.window_in_fullscreen_state = []
        #
        self.window_in_fullscreen_state_CM = []
        # window to bring on top or move by btn1
        self.grabbed_window_btn1 = None
        # mouse button 1 for decorated window resizing
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
        self._root_change_property('_NET_NUMBER_OF_DESKTOPS',[1])
        #
        self._root_change_property('_NET_DESKTOP_VIEWPORT',[0,0])
        #
        self._root_change_property('_NET_CURRENT_DESKTOP',[0])
        #
        self._root_change_property('_NET_DESKTOP_GEOMETRY',[screen_width, screen_height])
        #
        self._root_change_property('_NET_WORKAREA',[start_x,start_y,screen_width_usable,screen_height_usable])
        #
        _string = "Desktop"
        self.root.change_property(self.display.get_atom('_NET_DESKTOP_NAMES'), self.display.intern_atom('UTF8_STRING'), 8, _string.encode())
        # 
        self._root_change_property('_NET_SHOWING_DESKTOP',[0])
        #
        self._window = None
        #
        self._wm_support()
        #
        self.display.flush()
        #
        # decoration buttons
        if NO_DECO == 0:
            self.deco_btn_width = 0
            self.deco_btn_height = 0
            self.on_deco_btn()
        #
        # self.on_start()
        #
        self.main_loop()
    
    #
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
        #
        self._window.set_wm_class('jawm', 'JAWM')
        #
        if _THIS_PID:
            self._window.change_property(
                self.display.get_atom("_NET_WM_PID"),
                Xatom.CARDINAL,
                32, [_THIS_PID], X.PropModeReplace)
        #
        self._window.set_selection_owner(self.display.intern_atom('WM_S0'), X.CurrentTime)
        
    # add a decoration to win
    def win_deco(self, win):
        if NO_DECO == 1:
            win.configure(border_width=BORDER_WIDTH)
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
                # docks
                if event.window in self.dock_windows:
                    continue
                # desktop
                if event.window in self.desktop_window:
                    continue
                # check if this window is a transient one
                w_is_transient = event.window.get_full_property(self.display.get_atom("WM_TRANSIENT_FOR"), X.AnyPropertyType)
                if w_is_transient:
                    continue
                # only managed window - no splash no notification
                if event.window not in self.all_windows:
                    continue
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
                            #
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
                    self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                    self.active_window.raise_window()
                    self.display.sync()
                    #
                    self._update_active_window(self.active_window)
            #
            elif event.type == X.MapRequest:
                if event.window == X.NONE or event.window == None:
                    continue
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
                ew_type = None
                try:
                    ew_type = ewmh.getWmWindowType(event.window, str=True)
                except Exception as E:
                    print("ew_type error:", str(E))
                # 
                if ew_type:
                    if ew_type[0] in WINDOW_WITH_NO_DECO:
                        continue
                    # dock desktop splash notification
                    elif ew_type[0] in WINDOWS_MAPPED_WITH_NO_DECO:
                        #
                        if ew_type[0] == '_NET_WM_WINDOW_TYPE_DOCK':
                            # resulta = event.window.get_full_property(self.display.get_atom('_NET_WM_STRUT_PARTIAL'), Xatom.CARDINAL)
                            #
                            global DOCK_HEIGHT_X
                            global DOCK_HEIGHT_Y
                            global DOCK_HEIGHT_T
                            global DOCK_HEIGHT_B
                            # _NET_WM_STRUT, left, right, top, bottom, CARDINAL[4]/32
                            result2 = self.getProp(event.window, 'STRUT')
                            #
                            if result2:
                                # 0 0 38 0
                                DOCK_HEIGHT_X = result2[0]
                                DOCK_HEIGHT_Y = result2[1]
                                DOCK_HEIGHT_T = result2[2]
                                DOCK_HEIGHT_B = result2[3]
                                _screen_usable()
                            else:
                                # _NET_WM_STRUT_PARTIAL, left, right, top, bottom, left_start_y, left_end_y,
                                # right_start_y, right_end_y, top_start_x, top_end_x, bottom_start_x,
                                # bottom_end_x,CARDINAL[12]/32
                                result1 = self.getProp(event.window, 'STRUT_PARTIAL')
                                #
                                if result1:
                                    # 0 0 38 0 0 0 0 0 0 1599 0 0
                                    DOCK_HEIGHT_X = result2[0]
                                    DOCK_HEIGHT_Y = result2[1]
                                    DOCK_HEIGHT_T = result2[2]
                                    DOCK_HEIGHT_B = result2[3]
                                    _screen_usable()
                            #
                            event.window.map()
                            self.dock_windows.append(event.window)
                            self.all_windows.append(event.window)
                            self._update_client_list()
                            self.all_windows_stack.append(event.window)
                            self._update_client_list_stack()
                        # desktop - TO DO
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
                        # notification - TO DO eg position
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_NOTIFICATION':
                            event.window.map()
                        # notification - TO DO eg position
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_SPLASH':
                            # win_geom = event.window.get_geometry()
                            # x = int((screen_width-win_geom.width)/2)
                            # y = int((screen_height-win_geom.height)/2)
                            # event.window.configure(x=x, y=y)
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
                if _is_transient:
                    par_win_geom = _is_transient.get_geometry()
                    x = int((par_win_geom.width-win_geom.width)/2+par_win_geom.x)
                    y = int((par_win_geom.height-win_geom.height+TITLE_HEIGHT/2)/2+par_win_geom.y)
                else:
                    x = int((screen_width-win_geom.width)/2)
                    y = int((screen_height-win_geom.height)/2)
                #
                event.window.configure(x=x, y=y)
                #
                if _is_transient:
                    # add the border
                    event.window.change_attributes(border_pixel=border_color2, border_width=BORDER_WIDTH)
                    event.window.configure(border_width=BORDER_WIDTH)
                    event.window.map()
                    event.window.raise_window()
                    event.window.set_input_focus(X.RevertToParent, 0)
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
                            self.all_windows.append(event.window)
                            self._update_client_list()
                            self.all_windows_stack.append(event.window)
                            self._update_client_list_stack()
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
                    deco.map()
                    deco.raise_window()
                    #
                    if NO_DECO == 0:
                        self.deco_btn(deco)
                #
                self.all_windows.append(event.window)
                self._update_client_list()
                self.all_windows_stack.append(event.window)
                self._update_client_list_stack()
                #
                event.window.raise_window()
                event.window.map()
                #
                # mask = X.EnterWindowMask | X.LeaveWindowMask
                mask = X.EnterWindowMask
                event.window.change_attributes(event_mask=mask)
                #
                continue
                #
            #
            elif event.type == X.Expose:
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
                        event.window.set_input_focus(X.RevertToParent, 0)
            #
            elif event.type == X.UnmapNotify:
                if event.window == X.NONE or event.window == self.root:
                    continue
                # decoration
                if event.window in self.DECO_WIN:
                    if self.DECO_WIN[event.window]:
                        self.DECO_WIN[event.window].unmap()
                    # if event.window in self.DECO_WIN:
                        # event.window.unmap()
            #
            # first unmap then destroy eventually
            elif event.type == X.DestroyNotify:
                # remove the dock
                if event.window in self.dock_windows:
                    self.dock_windows.remove(event.window)
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
                    win = None
                    deco = None
                    #
                    if event.window in self.DECO_WIN:
                        win = event.window
                        deco = self.DECO_WIN[event.window]
                    else:
                        win2 = self.find_win_of_deco(event.window)
                        if win2:
                            win = win2
                            deco = event.window
                    #
                    # if win and deco:
                    if win:
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
                            # min size
                            if ww > 75 or hh > 75:
                                if deco:
                                    deco.configure(width=ww, height=hh)
                                    win.configure(width=ww-BORDER_WIDTH*2, height=hh-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif win:
                                    win.configure(width=ww, height=hh)
                        #
                    continue
                
                #### dragging 
                if self.mouse_button_left and self.grabbed_window_btn1:
                    x = event.root_x
                    y = event.root_y
                    #
                    if not self.delta_drag_start_point:
                        continue
                    #
                    win = None
                    deco = None
                    #
                    if event.window in self.DECO_WIN:
                        win = event.window
                        deco = self.DECO_WIN[event.window]
                    else:
                        win2 = self.find_win_of_deco(event.window)
                        if win2:
                            win = win2
                            deco = event.window
                    #
                    if win and deco:
                        deco.configure(x=x - self.delta_drag_start_point[0], y=y - self.delta_drag_start_point[1])
                        win.configure(x=x - self.delta_drag_start_point[0] + BORDER_WIDTH+BORDER_WIDTH2, y=y - self.delta_drag_start_point[1] + TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                    elif win:
                        win.configure(x=x - self.delta_drag_start_point[0], y=y - self.delta_drag_start_point[1])
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
                #
                if _is_active:
                    self.key_press_window.grab_button(1, X.AnyModifier, True,
                        X.ButtonPressMask|X.ButtonReleaseMask, X.GrabModeAsync,
                        X.GrabModeAsync, X.NONE, X.NONE)
                #
                if event.state & X.Mod4Mask:
                    # close active window
                    if event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("c")):
                        self.close_window()
                    # maximize active window
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("m")):
                        if event.child in self.DECO_WIN:
                            win = event.child
                        win2 = self.find_win_of_deco(event.child)
                        if win2 in self.DECO_WIN:
                            win = win2
                        self.maximize_window(win)
                    # minimize the active window
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("n")):
                        if event.child in self.DECO_WIN:
                            win = event.child
                        win2 = self.find_win_of_deco(event.child)
                        if win2 in self.DECO_WIN:
                            win = win2
                        self.minimize_window(win, 3)
                    # execute terminal
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("x")):
                        subprocess.Popen([_TERMINAL])
                    # exit
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym(_EXIT)):
                        return
                    # custom commands
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("1")):
                        if COMM_1:
                            subprocess.Popen([COMM_1])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("2")):
                        if COMM_2:
                            subprocess.Popen([COMM_2])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("3")):
                        if COMM_3:
                            subprocess.Popen([COMM_3])
                    elif event.detail == self.display.keysym_to_keycode(XK.string_to_keysym("4")):
                        if COMM_4:
                            subprocess.Popen([COMM_4])
            #
            elif event.type == X.KeyRelease:
                # on root
                if event.child == X.NONE or event.child == None or event.child == self.root:
                    if not self.key_press_window:
                        continue
                # 
                if self.key_press_window:
                    self.key_press_window.ungrab_button(1, X.AnyModifier)
            # 
            elif event.type == X.ButtonPress:
                _active = self.display.get_input_focus().focus
                #
                if event.window == None:
                    continue
                #########
                #
                # button 1 with Super_L - move the application
                if event.state & X.Mod4Mask:
                    # skip root
                    if event.window == X.NONE:
                        continue
                    # event.window is the program
                    _can_drag = 0
                    if event.window == _active:
                        _can_drag = 1
                    # or the decoration
                    else:
                        win2 = self.find_win_of_deco(event.window)
                        if win2 and (win2 == _active):
                            _can_drag = 1
                    #
                    if _can_drag:
                        self.grabbed_window_btn1 = event.window
                        self.mouse_button_left = 1
                        #
                        event.window.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                    X.GrabModeAsync, X.NONE, X.NONE, 0)
                        #
                        geom = self.grabbed_window_btn1.get_geometry()
                        cx = geom.x
                        cy = geom.y
                        x = event.root_x
                        y = event.root_y
                        self.delta_drag_start_point = (x - cx, y - cy)
                        continue
                #
                ##################### bring to top or move ###################
                ########### window in background 
                if event.detail == 1:
                    ######## decoration buttons
                    # actions in releasebutton event
                    if event.window == self.root:
                        ddeco = event.child
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
                                    # self.close_window()
                                    continue
                            # maximize button
                            elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*2-BTN_SPACE) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE-self.deco_btn_width):
                                if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                    wwin = self.find_win_of_deco(ddeco)
                                    if wwin in self.DECO_WIN:
                                        # self.maximize_window(wwin)
                                        continue
                            # minimize button
                            elif (dx+dw-BORDER_WIDTH-self.deco_btn_width*3-BTN_SPACE*2) < ex < (dx+dw-BORDER_WIDTH-BTN_SPACE*2-self.deco_btn_width*2):
                                if (dy+BORDER_WIDTH) < ey < (dy+BORDER_WIDTH+self.deco_btn_height):
                                    # self.minimize_window(event.window, 3)
                                    continue
                    ####### move
                    # drag the active window by its decoration
                    eewin = None
                    if self.entered_window in self.DECO_WIN:
                        eewin = self.entered_window
                    else:
                        eewin2 = self.find_win_of_deco(self.entered_window)
                        if eewin2:
                            eewin = eewin2
                    #
                    if _active == self.active_window:
                        # and self.entered_window == self.active_window:
                        if eewin:
                            if eewin == self.active_window:
                                if _active == X.NONE:
                                    continue
                                if _active in self.DECO_WIN:
                                    deco = self.DECO_WIN[_active]
                                if deco == None:
                                    continue
                                #
                                _is_drag = 1
                                ewin = None
                                if self.entered_window not in self.DECO_WIN:
                                    ewin = self.find_win_of_deco(self.entered_window)
                                if ewin:
                                    if _active != ewin:
                                        _is_drag = 0
                                    if self.active_window != ewin:
                                        _is_drag = 0
                                else:
                                    if _active != self.entered_window:
                                        _is_drag = 0
                                    if self.active_window != self.entered_window:
                                        _is_drag = 0
                                #
                                if _is_drag:
                                    self.grabbed_window_btn1 = deco
                                    geom = self.grabbed_window_btn1.get_geometry()
                                    cx = geom.x
                                    cy = geom.y
                                    x = event.root_x
                                    y = event.root_y
                                    #
                                    _ready_to_resize = 0
                                    if (cx+geom.width-40) <= x <= (cx+geom.width):
                                        if (cy+geom.height-40) <= y <= (cy+geom.height):
                                            _ready_to_resize = 1
                                    # elif (cx) <= x <= (cx+40):
                                        # if (cy+geom.height-40) <= y <= (cy+geom.height):
                                            # _ready_to_resize = 2
                                    #
                                    if _ready_to_resize:
                                        _is_drag = 0
                                        self.btn1_drag = deco
                                        self.mouse_button_left = _ready_to_resize
                                        deco.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                                X.GrabModeAsync, X.NONE, X.NONE, 0)
                                        geom = self.grabbed_window_btn1.get_geometry()
                                        cx = geom.x
                                        cy = geom.y
                                        x = event.root_x
                                        y = event.root_y
                                        self.window_resize_geometry = (geom.x, geom.y, geom.width, geom.height)
                                        self.mouse_button_resize_drag_start_point = (x, y)
                                        self.delta_drag_start_point = (x - cx, y - cy)
                                        continue
                                    ###########
                                    if _is_drag:
                                        self.grabbed_window_btn1 = deco
                                        self.mouse_button_left = 1
                                        deco.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                                    X.GrabModeAsync, X.NONE, X.NONE, 0)
                                        #
                                        geom = self.grabbed_window_btn1.get_geometry()
                                        cx = geom.x
                                        cy = geom.y
                                        x = event.root_x
                                        y = event.root_y
                                        self.delta_drag_start_point = (x - cx, y - cy)
                                        continue
                    #
                    ######### back
                    # decoration
                    dwin = None
                    # window
                    win = None
                    #
                    if self.entered_window != self.active_window:
                        if self.entered_window in self.DECO_WIN:
                            win = self.entered_window
                            dwin = self.DECO_WIN[self.entered_window]
                            #
                            win.raise_window()
                            if dwin:
                                dwin.raise_window()
                        else:
                            ewin = self.find_win_of_deco(self.entered_window)
                            if ewin:
                                win = ewin
                                dwin = self.entered_window
                    ####
                    self._activate_window(win, dwin, 0)
            #
            elif event.type == X.ButtonRelease:
                ######## decoration buttons
                if event.detail == 1:
                    if event.window == self.root:
                        ddeco = event.child
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
                                    self.close_window()
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
                ########### window in background #############
                # put window in front
                if self.grabbed_window_btn1:
                    self.mouse_button_left = 0
                    self.delta_drag_start_point = None
                    self.grabbed_window_btn1.ungrab_button(1, X.AnyModifier)
                    # win.ungrab_pointer()
                    #
                    self.grabbed_window_btn1 = None
                    #
                    self.display.ungrab_pointer(X.CurrentTime)
                    continue
                # useless
                continue
                # win = 0
                # # button 1 premuto con ALT
                # # if event.state & X.Mod1Mask:
                # if event.state & X.Mod4Mask:
                    # if event.window == self.root and event.child != 0:
                        # win = event.child
                    # elif event.window == self.root and event.child == 0:
                        # continue
                    # else:
                        # win = event.window
                # #
                # elif event.detail == 1:
                    # ### decoration
                    # if event.window == self.root and event.child != 0:
                        # win = event.child
                    # else:
                        # continue
                    # #
                # #
                # if win:
                    # self.mouse_button_left = 0
                    # self.grabbed_window_btn1 = None
                    # self.delta_drag_start_point = None
                    # win.ungrab_button(1, X.AnyModifier)
                    # # win.ungrab_pointer()
                    # #
                    # self.display.ungrab_pointer(X.CurrentTime)
            #
            elif event.type == X.PropertyNotify:
                if event.window == X.NONE or event.window == None:
                    continue
                #
                if event.atom == self.NET_ACTIVE_WINDOW:
                    print("ACTIVE WINDOW CHANGED")
                #
                elif event.atom == self.NET_LIST_STACK:
                    print("LIST STACK CHANGED")
                #
                elif event.atom == self.NET_LIST:
                    print("LIST CHANGED")
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
                    continue
                
                if event.client_type == self.NET_ACTIVE_WINDOW:
                    #
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
                    #
                    fmt, data = event.data
                    #
                    if fmt == 32:
                        if data[0] == 3 or data[0] == 0:
                            self.minimize_window(event.window, data[0])
                        elif data[0] == 1:
                            self.minimize_window(event.window, data[0])
                #
                if event.client_type == self.NET_WM_STATE:
                    # 
                    fmt, data = event.data
                    # maximize
                    if fmt == 32 and data[1] == self.WM_MAXIMIZED_VERT and data[2] == self.WM_MAXIMIZED_HORZ:
                        # 1 add - 2 toggle
                        if data[0] == 1 or data[0] == 2:
                            self.maximize_window(event.window)
                        # 0 remove
                        elif data[0] == 0:
                            self.maximize_window(event.window)
                    # minimize
                    elif fmt == 32 and data[1] == self.WM_HIDDEN:
                        #
                        if data[0] == 2:
                            self.minimize_window(event.window, data[0])
                    # fullscreen
                    if fmt == 32 and data[1] == self.WM_FULLSCREEN:
                        if data[0] in [0,1,2]:
                            self.fullscreen_window(event.window, data[0])
                #
                if event.client_type == self.display.intern_atom("WM_DELETE_WINDOW"):
                    continue
                #
                if event.client_type == self.display.intern_atom("_NET_CLOSE_WINDOW"):
                    if event.window in self.DECO_WIN:
                        c_type1 = self.display.intern_atom("WM_DELETE_WINDOW")
                        c_type = self.display.intern_atom("WM_PROTOCOLS")
                        data = (32, [c_type1, 0,0,0,0])
                        #
                        sevent = protocol.event.ClientMessage(
                        window = event.window,
                        client_type = c_type,
                        data = data
                        )
                        self.display.send_event(event.window, sevent)
                #
                #
                if event.client_type == self.WM_PROTOCOLS:
                    fmt, data = event.data
                    if fmt == 32 and data[0] == self.WM_DELETE_WINDOW:
                        print("request for delete the window")
            #
            elif event.type == X.ConfigureRequest:
                #
                window = event.window
                x, y = event.x, event.y
                width, height = event.width, event.height
                mask = event.value_mask
                if mask in [0b1111,0b1100,0b0011,0b01000000]:
                    # window restore from fullscreen state
                    if self.window_in_fullscreen_state:
                        if event.window == self.window_in_fullscreen_state[0]:
                            if event.sequence_number == self.window_in_fullscreen_state[1]:
                                continue
                            if width == screen_width and height == screen_height:
                                self.window_in_fullscreen_state = []
                                continue
                            #
                            event.window.configure(x=x, y=y, width=width, height=height)
                            if self.DECO_WIN[event.window]:
                                self.DECO_WIN[event.window].map()
                                self.DECO_WIN[event.window].raise_window()
                            event.window.raise_window()
                            continue
                    # fullscreen
                    if width == screen_width and height == screen_height:
                        if self.window_in_fullscreen_state_CM:
                            continue
                        # skip unwanted request - mpv 
                        if self.window_in_fullscreen_state:
                            if event.window == self.window_in_fullscreen_state[0]:
                                continue
                        #######
                        if event.window in self.DECO_WIN:
                            if self.DECO_WIN[event.window]:
                                self.DECO_WIN[event.window].unmap()
                        event.window.raise_window()
                        event.window.configure(x=0, y=0, width=width, height=height)
                        self.window_in_fullscreen_state = [event.window, event.sequence_number]
                        continue
                    else:
                        #
                        event.window.configure(x=x, y=y, width=width, height=height)
                        #
                        if event.window in self.DECO_WIN:
                            if self.DECO_WIN[event.window]:
                                self.DECO_WIN[event.window].configure(x=x-BORDER_WIDTH-BORDER_WIDTH2, y=y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2, 
                                    width=width+BORDER_WIDTH+BORDER_WIDTH2, height=height+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                                continue
            # if not _is_running:
                # break
        # else:
            # # print("exiting from loop...")
    

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
        if win in self.DECO_WIN:
            # window x y width height sequence_number
            if self.window_in_fullscreen_state_CM:
                if win in self.DECO_WIN:
                    deco = self.DECO_WIN[win]
                    (wwin,wx,wy,ww,wh) = self.window_in_fullscreen_state_CM
                    if wwin == win:
                        #
                        if deco:
                            deco.map()
                            deco.raise_window()
                        #
                        win.configure(x=wx,y=wy,width=ww,height=wh)
                        win.map()
                        win.raise_window()
                        self.window_in_fullscreen_state_CM = []
            else:
                wgeom = win.get_geometry()
                self.window_in_fullscreen_state_CM = [win, wgeom.x, wgeom.y, wgeom.width, wgeom.height]
                deco = self.DECO_WIN[win]
                #
                if deco:
                    deco.unmap()
                #
                win.configure(x=0,y=0,width=screen_width,height=screen_height)
                
    
    def close_window(self):
        active = self.display.get_input_focus().focus
        c_type1 = Display().intern_atom("WM_DELETE_WINDOW")
        c_type = Display().intern_atom("WM_PROTOCOLS")
        data = (32, [c_type1, 0,0,0,0])
        sevent = protocol.event.ClientMessage(
        window = active,
        client_type = c_type,
        data = data
        )
        active.send_event(sevent)
        Display().flush()
    
    # activate the window by request
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
                else:
                    self.active_window.change_attributes(border_pixel=border_color2)
                self.active_window.grab_button(1, X.AnyModifier, True,
                            X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                            X.GrabModeAsync, X.NONE, X.NONE)
                # self.display.sync()
            #
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
            # if self.DECO_WIN[self.active_window]:
                # self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color1)
                # self.DECO_WIN[self.active_window].ungrab_button(1, X.AnyModifier)
            if dwin:
                dwin.change_attributes(border_pixel=border_color1)
                dwin.ungrab_button(1, X.AnyModifier)
            else:
                self.active_window.change_attributes(border_pixel=border_color1)
                self.active_window.ungrab_button(1, X.AnyModifier)
            #
            if dwin:
                dwin.raise_window()
            #
            self.active_window.set_input_focus(X.RevertToParent, X.CurrentTime)
            self.active_window.raise_window()
            self.display.sync()
            # its transient
            if self.active_window in self.transient_windows:
                w_tr = self.transient_windows[self.active_window]
                w_tr.raise_window()
                w_tr.change_attributes(border_pixel=border_color2)
            #
            #
            self._update_active_window(self.active_window)
            #
    
    
    # find a window to set as active
    def _find_and_update_the_active(self, win):
        #
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
                    if hasattr(iitem.get_wm_state(), "state"):
                        if iitem.get_wm_state().state == 0:
                            continue
                    #
                    if iitem in self.DECO_WIN:
                        if iitem == win:
                            continue
                        #
                        _has_been_found = 1
                        if iitem in self.all_windows_stack:
                            self.all_windows_stack.remove(iitem)
                        self.all_windows_stack.append(iitem)
                        self._update_client_list_stack()
                        # self.DECO_WIN[iitem].raise_window()
                        # iitem.raise_window()
                        if self.DECO_WIN[iitem]:
                            self.DECO_WIN[iitem].change_attributes(border_pixel=border_color1)
                        else:
                            iitem.change_attributes(border_pixel=border_color1)
                        #
                        self.active_window = iitem
                        # 
                        if self.DECO_WIN[iitem]:
                            self.DECO_WIN[iitem].ungrab_button(1, X.AnyModifier)
                            self.DECO_WIN[iitem].raise_window()
                        # else:
                            # iitem.ungrab_button(1, X.AnyModifier)
                        #
                        self.active_window.ungrab_button(1, X.AnyModifier)
                        #
                        self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                        self.active_window.raise_window()
                        self.display.sync()
                        #
                        # UPDATE THE ATOM
                        self._update_active_window(self.active_window)
                        # its transient window
                        if self.active_window in self.transient_windows:
                            w_tr = self.transient_windows[self.active_window]
                            w_tr.raise_window()
                        #
                        break
                #
                if _has_been_found == 0:
                    self.active_window = X.NONE
                    self._update_active_window(self.active_window)
                        
    
    # windows in miniimized state: window:[deco]
    def minimize_window(self, win, ttype):
        # minimize
        if ttype == 3 or ttype == 0 or ttype == 2:
            if not win in self.MINIMIZED_WINDOWS:
                if win in self.DECO_WIN:
                    deco = self.DECO_WIN[win]
                    # Xutil.WithdrawnState, Xutil.NormalState, Xutil.IconicState
                    win.set_wm_state(state = Xutil.WithdrawnState, icon = X.NONE)
                    self.display.sync()
                    # if deco:
                        # deco.unmap()
                    self.MINIMIZED_WINDOWS[win] = deco
                    #
                    win.unmap()
                    #
                    if win == self.active_window:
                        self._find_and_update_the_active(win)
                    return
        # unminimize
        if ttype == 1 or ttype == 2 or ttype == 3 or ttype == 77:
            if win in self.MINIMIZED_WINDOWS:
                deco = self.MINIMIZED_WINDOWS[win]
                if deco:
                    deco.map()
                win.map()
                #
                win.set_wm_state(state = Xutil.NormalState, icon = X.NONE)
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
                # self.active_window = win
                if win in self.DECO_WIN:
                    if self.DECO_WIN[win]:
                        win.change_attributes(border_pixel=border_color1)
                        self.DECO_WIN[win].raise_window()
                    else:
                        win.change_attributes(border_pixel=border_color1)
                        #self.display.flush()
                #
                win.ungrab_button(1, X.AnyModifier)
                win.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                win.raise_window()
                self.display.sync()
                #
                if win in self.all_windows_stack:
                    self.all_windows_stack.remove(win)
                self.all_windows_stack.append(win)
                self._update_client_list_stack()
                #
                self.active_window = win
                #
                self._update_active_window(self.active_window)
                # its transient window
                if self.active_window in self.transient_windows:
                    w_tr = self.transient_windows[self.active_window]
                    w_tr.raise_window()
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
            deco2 = self.DECO_WIN[win2]
            if deco2:
                deco = deco2
                win = win2
            else:
                deco = None
                win = win2
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
                deco.configure(x=x,y=y,width=width1,height=height1)
                win.configure(x=x+BORDER_WIDTH+BORDER_WIDTH2, y=y+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2, 
                    width=width1-BORDER_WIDTH-BORDER_WIDTH2, height=height1-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2)
            else:
                win.configure(x=x, y=y, width=width1-BORDER_WIDTH2*2,height=height1-BORDER_WIDTH2*2)
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
            subprocess.Popen([prog])
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
    
            