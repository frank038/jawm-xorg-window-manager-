#!/usr/bin/env python3

# v. 20240226

##############
##### OPTIONS

# the inner border size of the decoration (px)
BORDER_WIDTH = 4
# the border of other kind of windows or the outer decoration border
BORDER_WIDTH2 = 2

# decoration main border color
DECO_BORDER_COLOR1 = "#7F7F7F"

# the other border color
DECO_BORDER_COLOR2 = "#008000"

# disable window decoration: 1 disable - 0 enable
NO_DECO = 0

# decoration color: buttons need to be recolored if changed
DECO_COLOR = "#F7630C"

# the main desktop name (name from wmclass first value or window name)
MAIN_DESKTOP_NAME = "qt5desktop-1"

# skip decocation: program name and reason, e.g.: APP_SPECIAL_DECO = [ ["xterm", "decoration-1"], [eventually other programs in the same way] ]
# the default for no actions: APP_SPECIAL_DECO = []
# PROGRAM NAME: from WMCLASS the first name (usually the launcher name without any arguments)
# REASONS:
# decoration-1 : remove the decoration from usually decorated windows
# decoration-2 : remove the decoration and the BORDER_WIDTH2 from usually decorated windows
# decoration-3 : all the undecorated windows will not have any BORDER_WIDTH2 ("*" as PROGRAM NAME is mandatory)
# decoration-4 : add the decoration and the outer border to usually undecorated windows (the PROGRAM NAME is mandatory)
APP_SPECIAL_DECO = []

# window position at the following coordinates: PROGRAM NAME - POSX POSY e.g.: APP_SPECIAL_POSITION = [ ["xterm", 100, 110] ]
# PROGRAM NAME: from WMCLASS the first name (usually the launcher name without any arguments)
APP_SPECIAL_POSITION = []

# window manager actions: Super_L (win key) - Alt_l - Control_l
_STATE = "Super_L"

# draw title in the titlebar - performance may decrease while resizing or dragging if activated
_DRAW_TITLE = 0

########### *** COMMANDS WITH WIN/CTRL+ALT *** ###########
################## PROGRAM NAMES ############
# terminal - key x
_TERMINAL = "xterm"
# command 1 - key 1
COMM_1 = "qterminal"
# command 2 - key 2
COMM_2 = "file-roller"
# command 3 - key 3
COMM_3 = "yad-icon-browser"
# command 4 - key 4
COMM_4 = "tint2"
######################### KEYS #################
# terminate this window manager
_EXIT = "e"
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
# print
_PRINT = "Print"
############## end commands ###########

from Xlib.display import Display
from Xlib import X, XK, protocol, Xatom, Xutil
import sys, os, shutil
import subprocess
import signal
import time
#import threading
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

# size: 1 normal (29 px) - 2 big (36 px)
TITLEBAR_SIZE = 1

# space between buttons
BTN_SPACE = 0

TITLE_HEIGHT = 0
if TITLEBAR_SIZE == 1:
    TITLE_HEIGHT = 29
elif TITLEBAR_SIZE == 2:
    TITLE_HEIGHT = 36
BTN_SIZE = TITLE_HEIGHT

USE_WIN=1

# focus to the window under the pointer
SLOPPY_FOCUS = 1

# windows always centered: 1 yes - 0 no
# if 0, try to use application data before
ALWAYS_CENTERED = 0

# resize with Super+right mouse button: 0 no - 1 yes
RESIZE_WITH_KEY = 1

# notification position: 1 top - 2 bottom
_NOTIFICATION_POS = 1

# font name and size
_FONT_NAME = "DejaVuSans.ttf"
_FONT_SIZE = 12
_FONT_COLOR = "white"
_STROKE_WIDTH = 0
_STROKE_FILL = "black"


font = None
if _DRAW_TITLE:
    from PIL import ImageDraw, ImageFont
    # font = ImageFont.load_default().font
    try:
        if _FONT_NAME:
            font = ImageFont.truetype(_FONT_NAME, _FONT_SIZE)
        else:
            font = ImageFont.truetype("_font.ttf", _FONT_SIZE)
    except:
        try:
            font = ImageFont.truetype("_font.ttf", _FONT_SIZE)
        except:
            _DRAW_TITLE = 0

colormap = Display().screen().default_colormap
win_color = colormap.alloc_named_color(DECO_COLOR).pixel
border_color1 = colormap.alloc_named_color(DECO_BORDER_COLOR1).pixel
border_color2 = colormap.alloc_named_color(DECO_BORDER_COLOR2).pixel


WINDOWS_WITH_DECO = [
"_NET_WM_WINDOW_TYPE_UTILITY",
"_NET_WM_WINDOW_TYPE_DIALOG",
"_NET_WM_WINDOW_TYPE_NORMAL",
]

WINDOWS_WITH_NO_DECO = [
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
'_NET_WM_WINDOW_TYPE_NOTIFICATION',
'_NET_WM_WINDOW_TYPE_TOOLTIP']

_is_running = 1

if NO_DECO == 1:
    BORDER_WIDTH = 0
    TITLE_HEIGHT = 0
    _DRAW_TITLE = 0

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
    mask_deco = X.EnterWindowMask | X.LeaveWindowMask | X.ExposureMask | X.SubstructureNotifyMask | X.ButtonPressMask | X.ButtonReleaseMask
else:
    mask_deco = X.EnterWindowMask | X.LeaveWindowMask | X.SubstructureNotifyMask | X.ButtonPressMask | X.ButtonReleaseMask


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
        self.NET_STATE_MODAL = self.display.intern_atom("_NET_WM_STATE_MODAL")
        # self.CHANGE_STATE = self.display.intern_atom("_NET_CHANGE_STATE")
        self.NET_WM_NAME = self.display.intern_atom('_NET_WM_NAME')
        self.WM_NAME = self.display.intern_atom('WM_NAME')
        self.WM_FULLSCREEN = self.display.intern_atom("_NET_WM_STATE_FULLSCREEN")
        self.WM_MAXIMIZED_HORZ = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_HORZ")
        self.WM_MAXIMIZED_VERT = self.display.intern_atom("_NET_WM_STATE_MAXIMIZED_VERT")
        self.WM_HIDDEN = self.display.intern_atom("_NET_WM_STATE_HIDDEN")
        self.WM_CHANGE_STATE = self.display.intern_atom("WM_CHANGE_STATE")
        # self.WM_NET_CHANGE_STATE = self.display.intern_atom("_NET_WM_CHANGE_STATE")
        self.NET_ACTIVE_WINDOW = self.display.intern_atom("_NET_ACTIVE_WINDOW")
        self.WM_TRANSIENT = self.display.intern_atom("WM_TRANSIENT_FOR")
        self.NET_LIST = self.display.intern_atom("_NET_CLIENT_LIST")
        self.NET_LIST_STACK = self.display.intern_atom("_NET_CLIENT_LIST_STACKING")
        self.STATE_DEMANDS_ATTENTION = self.display.intern_atom("_NET_WM_STATE_DEMANDS_ATTENTION")
        self.WM_S = self.display.intern_atom('WM_S0')
        # | X.FocusChangeMask - | X.KeyPressMask | X.KeyReleaseMask  | X.ButtonPressMask | X.ButtonReleaseMask
        
        if USE_WIN:
            mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask
                    | X.EnterWindowMask | X.LeaveWindowMask | X.ButtonPressMask | X.ButtonReleaseMask
                    | X.KeyPressMask | X.KeyReleaseMask | X.PropertyChangeMask)
        else:
            mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask
                    | X.EnterWindowMask | X.LeaveWindowMask | X.ButtonReleaseMask
                    | X.PropertyChangeMask)
        #
        self.root.change_attributes(event_mask=mask)
        #
        if USE_WIN:
            # Super_L 
            self.root.grab_key(self.display.keysym_to_keycode(XK.string_to_keysym(_STATE)),
                X.AnyModifier, 1, X.GrabModeAsync, X.GrabModeAsync)

            # 'XF86AudioLowerVolume' 'XF86AudioRaiseVolume'
            # self.root.grab_key(self.display.keysym_to_keycode("XF86AudioLowerVolume"),
                # X.NONE, 1, X.GrabModeAsync, X.GrabModeAsync)
            
            # terminal
            # if _TERMINAL:
                # keycode = self.display.keysym_to_keycode(XK.string_to_keysym(_TERMINAL))
                # modifier = X.Mod1Mask | X.ControlMask
                # self.root.grab_key(keycode, modifier, 1, X.GrabModeAsync,
                    # X.GrabModeAsync)
        else:
            #
            for _key in [_EXIT,_CC,_MM,_MN,_RS,_RW,_RD,_RA,_EXEC_TERM,_C1,_C2,_C3,_C4]:
                if _key:
                    keycode = self.display.keysym_to_keycode(XK.string_to_keysym(_key))
                    modifier = X.Mod1Mask | X.ControlMask
                    self.root.grab_key(keycode, modifier, 1, X.GrabModeAsync,
                        X.GrabModeAsync)
            
            if _PRINT:
                pass
                # keycode = self.display.keysym_to_keycode(XK.string_to_keysym(_PRINT))
                # modifier = X.NONE
                # # modifier = X.AnyModifier
                # self.root.grab_key(keycode, modifier, 1, X.GrabModeAsync,
                    # X.GrabModeAsync)
            #
            for button in [1, 3]:
                self.root.grab_button(button, X.Mod4Mask, True,
                         X.ButtonPressMask, X.GrabModeAsync,
                         X.GrabModeAsync, X.NONE, X.NONE)
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
        # the window is a desktop type
        self.desktop_window = []
        # windows that are dock type: window - x y t b
        self.dock_windows = {}
        # notification windows
        self.notification_windows = []
        # window with transient window: window:transient
        self.transient_windows = {}
        # windows belonging to window leader: window:[list of window with window_group hint (except transient)]
        self.windows_group = {}
        # # window in above state: window:decoration
        # self.windows_above = {}
        # window in below state: window:decoration
        self.windows_below = {}
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
        # resize window direction code
        self.resize_window_code = -1
        # the window or the decoration when a key is been pressed
        self.key_press_window = None
        # # the window that has the pointer in
        # self.entered_window = None
        #
        self.mouse_button_left = 0
        self.delta_drag_start_point = None
        # deco and title name
        self.title_is_changed = None
        ########
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
        #
        # decoration buttons
        if NO_DECO == 0:
            self.deco_btn_width = 0
            self.deco_btn_height = 0
            self.on_deco_btn()
        if _DRAW_TITLE:
            self.title_size = None
        #
        # self.on_start()
        #
        self.main_loop()
    
    
    def _root_change_property(self, _type, _data):
        self.root.change_property(
            self.display.get_atom(_type),
            Xatom.CARDINAL,
            32, _data)
    

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
        self._window.set_wm_class('jawm.py', 'JAWM')
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
            self._window.xrandr_select_input(randr.RRScreenChangeNotifyMask)

   
    # add a decoration to win
    def win_deco(self, win, _title):
        time.sleep(0.1)
        if NO_DECO == 1:
            win.configure(border_width=BORDER_WIDTH2)
            self.DECO_WIN[win] = None
            return -1
        #
        try:
            geom = win.get_geometry()
        except:
            return -1
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
        if _DRAW_TITLE:
            self._on_title2(deco, win)
        # if NO_DECO == 0:
            # self.on_deco_btn()
        # wret = 0
        # def werror(err, ww):
            # wret = -1
        # #
        # win.reparent(deco, BORDER_WIDTH, TITLE_HEIGHT, onerror=werror)
        #
        return deco
    
    # prepare the title
    def _on_title2(self, deco, win):
        if deco == None:
            return
        # 
        if not win:
            win = self.find_win_of_deco(deco)
        #
        _text = "X"
        if win:
            _text = self.get_window_name(win)
        else:
            return
        #
        if _text == "X":
            return
        #
        dgeom = deco.get_geometry()
        dx = dgeom.x
        dy = dgeom.y
        dw = dgeom.width
        dh = dgeom.height
        # 
        _available_width = dw-self.deco_btn_width*3-BTN_SPACE*2
        #
        if _available_width > 0:
            deco.clear_area (x=0, y=0, width=_available_width, height=TITLE_HEIGHT, exposures=0, onerror=None )
        #
        _text_size_width = int(font.getlength(_text))+1
        #
        title_size = (_text_size_width, TITLE_HEIGHT)
        imt = Image.new("RGB", title_size, DECO_COLOR)
        #
        d = ImageDraw.Draw(imt)
        xt = int(title_size[0]/2)
        yt = int((title_size[1])/2)
        #
        d.text((xt, yt), _text, fill=_FONT_COLOR, anchor="mm", font=font, stroke_width=_STROKE_WIDTH, stroke_fill=_STROKE_FILL)
        #
        iwt, iht = imt.size
        t_mask = self.screen.root.create_pixmap(iwt, iht, self.screen.root_depth)
        t_gc = t_mask.create_gc()
        t_mask.put_pil_image(t_gc, 0, 0, imt)
        t_mask_geometry = t_mask.get_geometry()
        # width and height
        iwt = t_mask_geometry.width
        iht = t_mask_geometry.height
        # x and y
        imxt = int((_available_width-iwt)/2)
        imyt = int(BORDER_WIDTH/2)
        #
        deco.copy_area(t_gc, t_mask, 0, 0, iwt, iht, imxt, imyt )
    
    
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
            # imx = dw-BORDER_WIDTH-BORDER_WIDTH2-self.deco_btn_width
            imx = dw-self.deco_btn_width
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
                # skip if already managed
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
                # Other kind of windows mapped with no decoration
                ew_type_tmp = self.get_window_type(event.window)
                ew_type = []
                if ew_type_tmp != 1:
                    for ee in ew_type_tmp:
                        ew_type.append(self.display.get_atom_name(ee))
                if ew_type:
                    if ew_type[0] in WINDOWS_MAPPED_WITH_NO_DECO:
                        continue
                # check if this window is a transient one
                w_is_transient = event.window.get_full_property(self.WM_TRANSIENT, X.AnyPropertyType)
                if w_is_transient:
                    _is_found = 0
                    for ee in self.DECO_WIN:
                        # pavucontrol-qt is a transient of what window? I hope this dont break anything else.
                        if ee.id == w_is_transient.value[0]:
                            _is_found = 1
                            break
                    if _is_found == 1:
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
                            if self.active_window in self.DECO_WIN:
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
                            #
                            self.display.sync()
                            # the new active window
                            self.active_window = wwin
                    else:
                        # the new active window
                        self.active_window = wwin
                        #
                        if self.active_window in self.DECO_WIN:
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
                    ew_type_tmp = self.get_window_type(event.window)
                    if ew_type_tmp != 1:
                        # if self.display.intern_atom("_NET_WM_WINDOW_TYPE_DIALOG") in ew_type_tmp:
                            # self.active_window.set_input_focus(X.RevertToParent, 0)
                        # elif self.display.intern_atom("_NET_WM_WINDOW_TYPE_UTILITY") in ew_type_tmp:
                            # self.active_window.set_input_focus(X.RevertToParent, 0)
                        # el
                        if ew_type_tmp[0] == self.display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL"):
                            self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                            self.active_window.set_wm_state(state = Xutil.NormalState, icon = X.NONE)
                    else:
                        self.active_window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                        # Xutil.WithdrawnState, Xutil.NormalState, Xutil.IconicState
                        self.active_window.set_wm_state(state = Xutil.NormalState, icon = X.NONE)
                    # to verify
                    if _DRAW_TITLE:
                        wwin.change_attributes(event_mask=X.PropertyChangeMask|X.EnterWindowMask)
                    # else:
                        # wwin.change_attributes(event_mask=X.EnterWindowMask)
                    #
                    # if _DRAW_TITLE and deco:
                        # self._on_title(deco)
                        # # self._on_title2(deco, wwin)
                    #
                    self.display.sync()
                    # 
                    self.active_window.raise_window()
                    self.display.sync()
                    #
                    # self.display.flush()
                    #
                    self._update_active_window(self.active_window)
                #### demands attention initial state hint
                _hints = event.window.get_wm_hints() or { 'flags': 0 }
                if (_hints["flags"] & Xutil.UrgencyHint):
                    ### message to everyone else
                    _window = self.active_window
                    _message_type = self.NET_WM_STATE
                    _format = 32
                    _atom1 = self.STATE_DEMANDS_ATTENTION
                    _data = [1, _atom1, 0, 0, 0]
                    #
                    sevent = protocol.event.ClientMessage(
                    window = _window,
                    client_type = self.NET_WM_STATE,
                    data=(32, (_data))
                    )
                    mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
                    self.root.send_event(sevent, event_mask=mask)
                    self.display.sync()
                    self.display.flush()
                    #
            #
            elif event.type == X.MapRequest:
                if event.window == X.NONE or event.window == None or event.window == self.root:
                    continue
                ##########
                # _is_above = 0
                _is_below = 0
                _is_modal = 0
                mprop = event.window.get_full_property(self.NET_WM_STATE, X.AnyPropertyType)#, sizehint = 10000)
                if mprop:
                    mvalue = mprop.value[0]
                    # if self.NET_STATE_ABOVE == mvalue:
                        # _is_above = 1
                    # el
                    if self.NET_STATE_BELOW == mvalue:
                        _is_below = 1
                    if self.NET_STATE_MODAL == mvalue:
                        _is_modal = 1
                # # delete this property - cannot be managed
                # if _is_modal:
                    # event.window.delete_property(
                        # self.NET_WM_STATE,
                        # )
                    # self.display.sync()
                    # _is_modal = 0
                #
                ##########
                # check if this window is a transient one
                _is_transient = None
                prop = None
                try:
                    prop = event.window.get_full_property(self.WM_TRANSIENT, X.AnyPropertyType)
                except:
                    pass
                #
                if prop:
                    w_id = prop.value.tolist()[0]
                    #
                    for win in self.DECO_WIN:
                        if win.id == w_id:
                            if win in self.transient_windows:
                                if self.transient_windows[win]:
                                    event.window.configure(stack_mode=X.Above, sibling=event.window)
                            #
                            self.transient_windows[win] = event.window
                            _is_transient = win
                            break
                    # # remove transient property
                    # if _is_transient == None:
                        # event.window.delete_property(
                            # self.WM_TRANSIENT,
                            # )
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
                        if not event.window in self.windows_group[pwin]:
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
                    if ew_type[0] in WINDOWS_WITH_NO_DECO:
                        win_geom = event.window.get_geometry()
                        x = max(win_geom.x, start_x)
                        y = max(win_geom.y, start_y)
                        event.window.configure(x=x, y=y)
                        event.window.map()
                        event.window.raise_window()
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
                                DOCK_HEIGHT_X += _result[0]
                                DOCK_HEIGHT_Y += _result[1]
                                DOCK_HEIGHT_T += _result[2]
                                DOCK_HEIGHT_B += _result[3]
                                _screen_usable()
                                self._root_change_property('_NET_WORKAREA',[start_x,start_y,screen_width_usable,screen_height_usable])
                            else:
                                # _NET_WM_STRUT_PARTIAL, left, right, top, bottom, left_start_y, left_end_y,
                                # right_start_y, right_end_y, top_start_x, top_end_x, bottom_start_x,
                                # bottom_end_x,CARDINAL[12]/32
                                _result = self.getProp(event.window, 'STRUT_PARTIAL')
                                #
                                if _result:
                                    DOCK_HEIGHT_X += _result[0]
                                    DOCK_HEIGHT_Y += _result[1]
                                    DOCK_HEIGHT_T += _result[2]
                                    DOCK_HEIGHT_B += _result[3]
                                    _screen_usable()
                                    self._root_change_property('_NET_WORKAREA',[start_x,start_y,screen_width_usable,screen_height_usable])
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
                            # # if  self.desktop_window == []:
                            # if self.get_window_name(event.window) == MAIN_DESKTOP_NAME:
                                # self.desktop_window.insert(0, event.window)
                            # elif self.get_window_cmd(event.window) == MAIN_DESKTOP_NAME:
                                # self.desktop_window.insert(0, event.window)
                            if MAIN_DESKTOP_NAME == self.get_window_name(event.window) or MAIN_DESKTOP_NAME == self.get_window_cmd(event.window):
                                if event.window not in self.desktop_window:
                                    self.desktop_window.insert(0, event.window)
                                    if len(self.desktop_window) > 1:
                                        for dd in self.desktop_window[1:]:
                                            dd.configure(stack_mode=X.Above, sibling=self.desktop_window[0])
                                else:
                                    self.desktop_window.append(event.window)
                            else:
                                self.desktop_window.append(event.window)
                            event.window.configure(x=0, y=0, width=screen_width, height=screen_height)
                            # put at bottom of all but desktops
                            self.all_windows.insert(len(self.desktop_window), event.window)
                            self._update_client_list()
                            self.all_windows_stack.insert(len(self.desktop_window), event.window)
                            self._update_client_list_stack()
                            # the first must be the main desktop application
                            if self.desktop_window:
                                if len(self.desktop_window) > 1:
                                    if self.desktop_window[0] != event.window:
                                        # event.window.configure(stack_mode=X.Below)
                                        # self.desktop_window[0].configure(stack_mode=X.Below)
                                        event.window.configure(stack_mode=X.Above, sibling=self.desktop_window[0])
                                else:
                                    event.window.configure(stack_mode=X.Below)
                            #
                            self.display.sync()
                            event.window.map()
                        # position managed by the notification server
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_NOTIFICATION':
                            ngeom = event.window.get_geometry()
                            # # x = end_x - ngeom.width - 4
                            # # if _NOTIFICATION_POS == 2:
                                # # y = end_y - 4
                            # # else:
                                # # y = start_y + 4
                            # x = max(start_x, ngeom.x)
                            # y = max(start_y, ngeom.y)
                            x = ngeom.x
                            y = ngeom.y
                            event.window.configure(x=x, y=y, stack_mode=X.Above)
                            self.display.sync()
                            event.window.map()
                            #
                            self.notification_windows.append(event.window)
                        #
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_SPLASH':
                            win_geom = event.window.get_geometry()
                            x = int((screen_width-win_geom.width)/2)
                            y = int((screen_height-win_geom.height)/2)
                            event.window.configure(x=x, y=y)
                            event.window.map()
                        #
                        elif ew_type[0] == '_NET_WM_WINDOW_TYPE_TOOLTIP':
                            event.window.map()
                        #
                        continue
                #
                if not event.window:
                    continue
                if event.window in self.DECO_WIN:
                    # gimp color chooser workaround: is the only unmapped state a meaningfull state?
                    # can brake other things
                    if ew_type[0] == "_NET_WM_WINDOW_TYPE_DIALOG":
                        if self.DECO_WIN[event.window]:
                            self.DECO_WIN[event.window].map()
                            self.DECO_WIN[event.window].raise_window()
                            event.window.raise_window()
                    continue
                # remove the border from the program
                event.window.change_attributes(
                         border_pixel=border_color1,
                         border_width=0)
                # center the window
                try:
                    win_geom = event.window.get_geometry()
                except:
                    continue
                #
                x = 0
                y = 0
                if _is_transient:
                    par_win_geom = _is_transient.get_geometry()
                    x = int((par_win_geom.width-win_geom.width)/2+par_win_geom.x)
                    y = int((par_win_geom.height-win_geom.height+TITLE_HEIGHT/2)/2+par_win_geom.y)
                    # always in the screen
                    if (x + win_geom.width) > screen_width_usable or (y + win_geom.height) > screen_height_usable or x < start_x or y < start_y:
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
                # the window command name
                win_name = self.get_window_cmd(event.window)
                # the window name
                win_named = self.get_window_name(event.window)
                #
                if APP_SPECIAL_POSITION == []:
                    event.window.configure(x=x, y=y)
                else:
                    xx = -999
                    yy = -999
                    for el in APP_SPECIAL_POSITION:
                        if len(el) == 3:
                            if el[0] == win_name:
                                xx = el[1]
                                yy = el[2]
                                break
                    #
                    if xx != -999 and yy != -999:
                        event.window.configure(x=xx, y=yy)
                    
                # self.display.sync()
                #
                if _is_transient:
                    # add the border
                    event.window.change_attributes(border_pixel=border_color2, border_width=BORDER_WIDTH)
                    event.window.configure(border_width=BORDER_WIDTH2)
                    #
                    mask = X.EnterWindowMask
                    event.window.change_attributes(event_mask=mask)
                    self.display.sync()
                    #
                    event.window.map()
                    event.window.raise_window()
                    #
                    # event.window.change_property(
                        # self.display.intern_atom('_MOTIF_WM_HINTS'),
                        # self.display.intern_atom('_MOTIF_WM_HINTS'),
                        # 32,
                        # [0,0,0,0,0],
                        # X.PropModeReplace,
                    # )
                    # self.display.sync()
                    #
                    continue
                #
                # some windows dont want any decoration
                try:
                    pprop = event.window.get_full_property(self.display.intern_atom('_MOTIF_WM_HINTS'), X.AnyPropertyType)
                except:
                    continue
                #
                skip_decoration = 0
                # skip windows that dont want the decoration
                if pprop != None:
                    if pprop.value:
                        if pprop.value.tolist()[2] == 0:
                            skip_decoration = 1
                #
                skip_deco = 99
                #
                if NO_DECO == 0 and APP_SPECIAL_DECO != []:
                    for el in APP_SPECIAL_DECO:
                        if el[0] == win_name or el[0] == win_named or el[0] == "*":
                            # no decoration
                            if el[1] == "decoration-1" and el[0] != "*":
                                skip_deco = 1
                                break
                            # no decoration - no outer border
                            elif el[1] == "decoration-2" and el[0] != "*":
                                skip_deco = 2
                                break
                            # no outer border around the usually undecorated windows
                            elif el[1] == "decoration-3" and el[0] == "*" and skip_decoration == 1:
                                skip_deco = 3
                                break
                            # add the decoration anyway
                            elif el[1] == "decoration-4" and el[0] != "*" and skip_decoration == 1:
                                skip_deco = 4
                                break
                            #
                # undecorated windows
                if skip_decoration == 1:
                    # skip the outer border
                    if skip_deco == 2 or skip_deco == 3:
                        skip_decoration = 3
                    elif skip_deco == 4:
                        skip_decoration = 0
                # usually decorated window
                elif skip_decoration == 0:
                    # remove the decoration
                    if skip_deco == 1:
                        skip_decoration = 1
                    # and the outer border
                    elif skip_deco == 2:
                        skip_decoration = 3
                #
                if skip_decoration > 0:
                    # add the border
                    if skip_decoration == 1:
                        event.window.configure(border_width=BORDER_WIDTH2)
                    #
                    mask = X.EnterWindowMask|X.StructureNotifyMask
                    event.window.change_attributes(event_mask=mask)
                    #
                    self.DECO_WIN[event.window] = None
                    #
                    event.window.map()
                    event.window.raise_window()
                    #
                    if _is_below:
                        self.windows_below[event.window] = None
                    # elif _is_above:
                        # self.windows_above[event.window] = None
                    ##########
                    continue
                #
                _title_text = self.get_window_name(event.window)
                deco = self.win_deco(event.window, _title_text)
                #
                if deco != -1:
                    # deco.change_attributes(attrs)
                    # self.display.sync()
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
                #
                mask = X.EnterWindowMask
                event.window.change_attributes(event_mask=mask)
                #
                if _is_below:
                    self.windows_below[event.window] = deco
                # elif _is_above:
                    # self.windows_above[event.window] = deco
                #
                continue
                #
            # elif event.type == X.CreateNotify:
                # pass
            #
            elif event.type == X.Expose:
                # if event.count == 0:
                if NO_DECO == 0:
                    win = None
                    deco = None
                    #
                    if event.window in self.DECO_WIN:
                        win = event.window
                        deco = self.DECO_WIN[event.window]
                    else:
                        win = self.find_win_of_deco(event.window)
                        if win:
                            deco = event.window
                    # decoration buttons
                    if win:
                        self.deco_btn(event.window)
                    # title
                    if _DRAW_TITLE:
                        if deco and win:
                            # if self.title_is_changed == (deco, win):
                                # continue
                            # if self.mouse_button_left == 0:
                            self._on_title2(deco, win)
                            # self.title_is_changed = (deco, win)
            #
            elif event.type == X.EnterNotify:
                if event.window == None:
                    continue
                # if event.window == self.active_window:
                    # continue
                # if event.window == self.root:
                    # self.entered_window = None
                # #
                # self.entered_window = event.window
                #
                if SLOPPY_FOCUS:
                    if event.window in self.DECO_WIN:
                        # event.window.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
                        ew_type_tmp = self.get_window_type(event.window)
                        if ew_type_tmp != 1:
                            if self.display.intern_atom("_NET_WM_WINDOW_TYPE_DIALOG") in ew_type_tmp:
                                event.window.set_input_focus(X.RevertToParent, 0)
                            elif self.display.intern_atom("_NET_WM_WINDOW_TYPE_UTILITY") in ew_type_tmp:
                                event.window.set_input_focus(X.RevertToParent, 0)
                            elif ew_type_tmp[0] == self.display.intern_atom("_NET_WM_WINDOW_TYPE_NORMAL"):
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
                # notifications
                if event.window in self.notification_windows:
                    self.notification_windows.remove(event.window)
                # decoration
                if event.window in self.DECO_WIN:
                    if self.DECO_WIN[event.window]:
                        self.DECO_WIN[event.window].unmap()
                    #
                    self._find_and_update_the_active(event.window)
            #
            # first unmap then destroy eventually
            elif event.type == X.DestroyNotify:
                if event.window == self.root or event.window == None:
                    continue
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
                # it is a transient window
                w_is_transient = None
                for wwin in self.transient_windows:
                    if self.transient_windows[wwin] == event.window:
                        # if wwin in self.root.query_tree().children:
                        if wwin == self.active_window:
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
                    deco = self.find_win_of_deco(event.window)
                # the decoration
                else:
                    win = self.find_win_of_deco(event.window)
                    if win:
                        deco = event.window
                #
                if win:
                    # with decoration
                    if win in self.DECO_WIN:
                        if self.DECO_WIN[win]:
                            self.DECO_WIN[win].unmap()
                            self.DECO_WIN[win].destroy()
                        #
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
                    # in unmapnotify
                    # self._find_and_update_the_active(win)
                    #
                    if win in self.windows_below:
                        del self.windows_below[win]
                    # elif win in self.windows_above:
                        # del self.windows_above[win]
            #
            elif event.type == X.MotionNotify:
                if event.window == self.root:
                    continue
                # skip undecorated maximized windows
                if event.window in self.DECO_WIN:
                    if self.DECO_WIN[event.window] == None and event.window in self.MAXIMIZED_WINDOWS:
                        continue
                    #
                #### window resizing with left mouse button
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
                    xx = x - self.mouse_button_resize_drag_start_point[0]
                    #
                    yy = y - self.mouse_button_resize_drag_start_point[1]
                    #
                    if ddeco:
                        dgeom = ddeco.get_geometry()
                    elif wwin:
                        dgeom = wwin.get_geometry()
                    #
                    if self.mouse_button_left == 1:
                        # bottom right - little shift to bottom-right
                        if self.resize_window_code == 4:
                            x2 = self.window_resize_geometry[0]
                            y2 = self.window_resize_geometry[1]
                            w2 = self.window_resize_geometry[2]+xx
                            h2 = self.window_resize_geometry[3]+yy
                            #
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        #
                        # top right
                        elif self.resize_window_code == 2:
                            x2 = self.window_resize_geometry[0]
                            y2 = self.window_resize_geometry[1]+yy
                            w2 = self.window_resize_geometry[2]+xx
                            h2 = self.window_resize_geometry[3]-yy
                            #
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        # bottom left
                        elif self.resize_window_code == 6:
                            x2 = self.window_resize_geometry[0]+xx
                            y2 = self.window_resize_geometry[1]
                            w2 = self.window_resize_geometry[2]-xx
                            h2 = self.window_resize_geometry[3]+yy
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                            #
                        # top left
                        elif self.resize_window_code == 0:
                            x2 = self.window_resize_geometry[0]+xx
                            y2 = self.window_resize_geometry[1]+yy
                            w2 = self.window_resize_geometry[2]-xx
                            h2 = self.window_resize_geometry[3]-yy
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        # left
                        elif self.resize_window_code == 7:
                            x2 = self.window_resize_geometry[0]+xx
                            y2 = self.window_resize_geometry[1]
                            w2 = self.window_resize_geometry[2]-xx
                            h2 = self.window_resize_geometry[3]
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        # right
                        elif self.resize_window_code == 3:
                            x2 = self.window_resize_geometry[0]
                            y2 = self.window_resize_geometry[1]
                            w2 = self.window_resize_geometry[2]+xx
                            h2 = self.window_resize_geometry[3]
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        # bottom
                        elif self.resize_window_code == 5:
                            x2 = self.window_resize_geometry[0]
                            y2 = self.window_resize_geometry[1]
                            w2 = self.window_resize_geometry[2]
                            h2 = self.window_resize_geometry[3]+yy
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
                        # top
                        elif self.resize_window_code == 1:
                            x2 = self.window_resize_geometry[0]
                            y2 = self.window_resize_geometry[1]+yy
                            w2 = self.window_resize_geometry[2]
                            h2 = self.window_resize_geometry[3]-yy
                            # min size of the window
                            if w2 > 75 and h2 > 75:
                                if ddeco:
                                    ddeco.configure(x=x2, y=y2, width=w2, height=h2)
                                    wwin.configure(x=x2+BORDER_WIDTH+BORDER_WIDTH2, y=y2+BORDER_WIDTH+BORDER_WIDTH2+TITLE_HEIGHT, width=w2-BORDER_WIDTH*2, height=h2-BORDER_WIDTH*2-TITLE_HEIGHT)
                                elif wwin:
                                    wwin.configure(x=x2, y=y2, width=w2, height=h2)
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
                    # do not go outside the top or right border
                    if self.mouse_button_left == 1:
                        #
                        if USE_WIN:
                            _MOD = X.Mod4Mask
                        else:
                            _MOD = X.Mod1Mask
                        if not event.state & _MOD:
                            #
                            if ddeco:
                                ggeom = ddeco.get_geometry()
                            else:
                                ggeom = wwin.get_geometry()
                            # top
                            if y <= self.delta_drag_start_point[1]+4+start_y:
                                #
                                if ddeco and wwin:
                                    ddeco.configure(x=x - self.delta_drag_start_point[0], y=start_y)
                                    wwin.configure(x=x - self.delta_drag_start_point[0] + BORDER_WIDTH+BORDER_WIDTH2, y=start_y+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                                elif wwin:
                                    wwin.configure(x=x - self.delta_drag_start_point[0], y=start_y)
                                #
                                continue
                            # right
                            elif end_x-4 < x+ggeom.width-self.delta_drag_start_point[0]:
                                if ddeco and wwin:
                                    x = end_x-ggeom.width-BORDER_WIDTH2*2
                                    ddeco.configure(x=x, y=y-self.delta_drag_start_point[1])
                                    wwin.configure(x=x + BORDER_WIDTH+BORDER_WIDTH2, y=y-self.delta_drag_start_point[1]+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                                elif wwin:
                                    x = end_x-ggeom.width-BORDER_WIDTH2*2
                                    wwin.configure(x=x, y=y-self.delta_drag_start_point[1])
                                #
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
                if event.detail == 122:
                    try:
                        os.system("xterm &")
                    except:
                        pass
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
                if USE_WIN:
                    _MOD = X.Mod4Mask
                else:
                    _MOD = (X.Mod1Mask | X.ControlMask)
                # if event.state & X.Mod4Mask:
                # if event.state & (X.Mod1Mask | X.ControlMask):
                if event.state & _MOD:
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
            # elif event.type == X.ConfigureNotify:
                # continue
            #
            # elif event.type == X.CirculateRequest:
                # continue
            #
            elif event.type == X.KeyRelease:
                # on root
                if event.child == X.NONE or event.child == None or event.child == self.root:
                    if not self.key_press_window:
                        continue
                # 
                if self.key_press_window:
                    if self.active_window == self.key_press_window:
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
                            # skip maximized window
                            if wwin in self.MAXIMIZED_WINDOWS:
                                continue
                            #
                            self.grabbed_window_btn1 = wwin
                            if ddeco:
                                self.grabbed_window_btn1 = ddeco
                            # self.mouse_button_left = 11
                            self.mouse_button_left = 1
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
                        # skip maximized window
                        if wwin in self.MAXIMIZED_WINDOWS:
                            continue
                        #
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
                        wgeom = wwin.get_geometry()
                        # top left
                        if wgeom.x < ex < wgeom.x+int(wgeom.width/2)-1 and wgeom.y < ey < wgeom.y+int(wgeom.height/2)-1:
                            self.resize_window_code = 0
                        # top right
                        elif  wgeom.x+int(wgeom.width/2)+1 < ex < wgeom.x+wgeom.width and wgeom.y < ey < wgeom.y+int(wgeom.height/2)-1:
                            self.resize_window_code = 2
                        # bottom left
                        if wgeom.x < ex < wgeom.x+int(wgeom.width/2)-1 and wgeom.y+int(wgeom.height/2)+1 < ey < wgeom.y+wgeom.height:
                            self.resize_window_code = 6
                        # bottom right
                        elif  wgeom.x+int(wgeom.width/2)+1 < ex < wgeom.x+wgeom.width and wgeom.y+int(wgeom.height/2)+1 < ey < wgeom.y+wgeom.height:
                            self.resize_window_code = 4
                        #
                        continue
                        
                ##########
                #
                if event.detail == 1:
                    #
                    # actions in release button event
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
                            ######
                        ################ window to front before dragging #############
                        if pdatawin == ddeco and _bring_to_front:
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
                                _bring_to_front = 0
                            ######
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
                            ############## resizing ###############
                            # bottom right
                            elif (cx+dw-40) <= ex <= (cx+dw):
                                if (cy+dh-40) <= ey <= (cy+dh):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 4
                                    #
                                    continue
                                elif (cy) <= ey <= (cy+40):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 2
                                    continue
                                # right
                                elif (cy+80) <= ey <= (cy+dh-80):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 3
                                    continue
                            # bottom left
                            elif (cx) <= ex <= (cx+40):
                                if (cy+dh-40) <= ey <= (cy+dh):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 6
                                    continue
                                # top left
                                elif (cy) <= ey <= (cy+40):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 0
                                    continue
                                # left
                                elif (cy+80) <= ey <= (cy+dh-80):
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 7
                                    continue
                            # top
                            elif (cx+80) <= ex <= (cx+dw-80) and cy <= ey <= (cy+4):
                                if BORDER_WIDTH < 4:
                                    continue
                                if BORDER_WIDTH > 8:
                                    # skip maximized window
                                    if wwin in self.MAXIMIZED_WINDOWS:
                                        continue
                                    #
                                    self.btn1_drag = ddeco
                                    self.grabbed_window_btn1 = ddeco
                                    self.mouse_button_left = 1
                                    self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                            X.GrabModeAsync, X.NONE, X.NONE, 0)
                                    #
                                    self.window_resize_geometry = (dx, dy, dw, dh)
                                    self.mouse_button_resize_drag_start_point = (ex, ey)
                                    self.delta_drag_start_point = (ex - cx, ey - cy)
                                    #
                                    self.resize_window_code = 1
                                    continue
                            # bottom
                            elif (cx+80) <= ex <= (cx+dw-80) and (cy+dh-40) <= ey <= (cy+dh):
                                # skip maximized window
                                if wwin in self.MAXIMIZED_WINDOWS:
                                    continue
                                #
                                self.btn1_drag = ddeco
                                self.grabbed_window_btn1 = ddeco
                                self.mouse_button_left = 1
                                self.btn1_drag.grab_pointer(True, X.PointerMotionMask | X.ButtonReleaseMask, X.GrabModeAsync,
                                        X.GrabModeAsync, X.NONE, X.NONE, 0)
                                #
                                self.window_resize_geometry = (dx, dy, dw, dh)
                                self.mouse_button_resize_drag_start_point = (ex, ey)
                                self.delta_drag_start_point = (ex - cx, ey - cy)
                                #
                                self.resize_window_code = 5
                                continue
                            ############## DRAG - decoration #############
                            else:
                                # skip window at back
                                if wwin != self.active_window:
                                    continue
                                #
                                # skip maximized window
                                if wwin in self.MAXIMIZED_WINDOWS:
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
                                # ######## actually useless
                                # wm_state = self.NET_WM_STATE
                                # _atm = self.display.get_atom('_NET_ACTIVE_WINDOW')
                                # # _data = [1, X.CurrentTime,window.id,0,0]
                                # _data = [0,0,0,0,0]
                                # sevent = protocol.event.ClientMessage(
                                # window = wwin,
                                # client_type = _atm,
                                # data=(32, (_data))
                                # )
                                # mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
                                # self.root.send_event(event=sevent, event_mask=mask)
                                # self.display.flush()
                                # self.display.sync()
                                # ###########
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
                # reset
                self.resize_window_code = -1
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
                    # win.ungrab_pointer()
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
                if _DRAW_TITLE:
                    if event.atom in [self.NET_WM_NAME, self.WM_NAME]:
                        wname = self.get_window_name(event.window)
                        if event.window in self.DECO_WIN:
                            deco = self.DECO_WIN[event.window]
                            if deco == None:
                                continue
                            else:
                                if self.title_is_changed == (deco, wname):
                                    continue
                                self._on_title2(deco, win)
                                self.title_is_changed = (deco, wname)
                #
                if event.atom == self.NET_ACTIVE_WINDOW:
                    continue
                #
                elif event.atom == self.NET_LIST_STACK:
                    continue
                #
                elif event.atom == self.NET_LIST:
                    continue
            #
            elif event.type == X.ClientMessage:
                # print("1313 clientMessage::", event)
                #
                if event.window not in self.all_windows:
                    continue
                #
                if event.client_type == self.display.intern_atom("_NET_WM_MOVERESIZE"):
                    # print("** cl move_resize")
                    fmt, data = event.data
                    if fmt == 32:
                        # move using mouse
                        if data[2] == 8:
                            # data.l[0] = x_root 
                            # data.l[1] = y_root
                            # data.l[2] = direction - 8 move - 11 cancel - 4 resize_bottom_right - 6 resize_bottom_left
                            # data.l[3] = button
                            # data.l[4] = source indication - 1
                            ########
                            # self.grabbed_window_btn1 = deco
                            # self.mouse_button_left = 1
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
                        # elif data[2] == 4:
                        elif data[2] in [0,1,2,3,4,5,6,7]:
                            self.resize_window_code = data[2]
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
                # if event.client_type == self.display.intern_atom("_NET_RESTACK_WINDOW"):
                    # # from pagers
                    # continue
                #
                if event.client_type == self.NET_ACTIVE_WINDOW:
                    fmt, data = event.data
                    #
                    # 1 from application - 2 from pager and other similars (tint2) - 0 from old applications
                    # data = [1/2/0, timestamp/_NET_WM_USER_TIME, win.id,0,0]
                    # Depending on the information provided with the message, 
                    # the Window Manager may decide to refuse the request 
                    # (either completely ignore it, or e.g. use _NET_WM_STATE_DEMANDS_ATTENTION).
                    #
                    # if fmt == 32 and data[0] in [1,2]:
                    if fmt == 32 and data[0] in [1,2,0]:
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
                        # hidden: 1 to hide (code 11) and 2 (code 22) to toggle - 0 (code 10) to unhide
                        if data[0] == 1:
                            self.minimize_window(event.window, 11)
                        elif data[0] == 2:
                            self.minimize_window(event.window, 22)
                        elif data[0] == 0:
                            self.minimize_window(event.window, 10)
                    # fullscreen
                    elif fmt == 32 and data[1] == self.WM_FULLSCREEN:
                        # if data[0] == 2:
                        if data[0] in [0,1,2]:
                            self.fullscreen_window(event.window, data[0])
                    #
                    # demands attention - WM_HINTS.flags property of window - set_wm_hints
                    elif fmt == 32 and data[1] == self.STATE_DEMANDS_ATTENTION:
                        # ##  Urgency
                        # Windows expecting immediate user action should 
                        # indicate this using the urgency bit in the 
                        # WM_HINTS.flags property, as defined in the ICCCM.
                        # skip actve window
                        if event.window == self.active_window:
                            continue
                        # add
                        if data[0] == 1:
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            hints['flags'] |= Xutil.UrgencyHint
                            event.window.set_wm_hints(hints)
                            hints = event.window.get_wm_hints()
                            self.display.flush()
                        # remove
                        elif data[0] == 0:
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            # remove
                            hints['flags'] &= ~Xutil.UrgencyHint
                            event.window.set_wm_hints(hints)
                            self.display.flush()
                            hints = event.window.get_wm_hints()
                        # toggle urgency
                        elif data[0] == 2:
                            #
                            hints = event.window.get_wm_hints() or { 'flags': 0 }
                            if hints['flags'] & Xutil.UrgencyHint:
                                # remove
                                hints['flags'] &= ~Xutil.UrgencyHint
                                event.window.set_wm_hints(hints)
                                self.display.flush()
                            else:
                                # add
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
                    fmt, data = event.data
                    if fmt == 32:
                        if data[1] == self.WM_S:
                            # # sys.exit(0)
                            if self.display.get_selection_owner(self.WM_S) == 0 or self.display.get_selection_owner != self._window:
                                self._window.set_selection_owner(X.NONE, X.CurrentTime)
                                for ww in [self.root, self._window]:
                                    ww.change_property(self.display.get_atom('_NET_SUPPORTING_WM_CHECK'),
                                        Xatom.WINDOW,32,[X.NONE])
                                #
                                self._window.destroy()
                                # os.kill(_THIS_PID, 9)
                                return
                            #
                            continue
            # #
            # elif event.type == X.SelectionNotify:
                # pass
            #
            elif event.type == X.ConfigureRequest:
                # print("*** 916 configure request::", event, self.get_window_name(event.window))
                #
                if event.window == None or event.window == self.root:
                    continue
                #
                x = event.x
                y = event.y
                width, height = event.width, event.height
                mask = event.value_mask
                #
                if mask & (X.CWX | X.CWY | X.CWWidth | X.CWHeight):
                    event.window.configure(x=x, y=y, width=width, height=height)
                    if event.window in self.DECO_WIN:
                        if self.DECO_WIN[event.window]:
                            self.DECO_WIN[event.window].configure(x=x-BORDER_WIDTH-BORDER_WIDTH2, y=y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2, 
                                    width=width+BORDER_WIDTH+BORDER_WIDTH2, height=height+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                    self.display.sync()
                #
                elif mask & (X.CWWidth | X.CWHeight):
                    event.window.configure(width=width, height=height)
                    if event.window in self.DECO_WIN:
                        if self.DECO_WIN[event.window]:
                            self.DECO_WIN[event.window].configure(width=width+BORDER_WIDTH+BORDER_WIDTH2, height=height+TITLE_HEIGHT+BORDER_WIDTH+BORDER_WIDTH2)
                    self.display.sync()
                #
                elif mask & (X.CWX | X.CWY):
                    event.window.configure(x=x, y=y)
                    if event.window in self.DECO_WIN:
                        if self.DECO_WIN[event.window]:
                            self.DECO_WIN[event.window].configure(x=x-BORDER_WIDTH-BORDER_WIDTH2, y=y-TITLE_HEIGHT-BORDER_WIDTH-BORDER_WIDTH2)
                    self.display.sync()
                #
                elif mask & X.CWStackMode:
                    event.window.configure(event.stack_mode)
                    self.display.sync()
                    #
                    # if event.window in self.windows_below:
                        # del self.windows_below[event.window]
                    # elif event.window in self.windows_above:
                        # del self.windows_above[event.window]
                    #
                    # deco = None
                    # if event.window in self.DECO_WIN:
                        # deco = self.DECO_WIN[event.window]
                    # if event.stack_mode == X.Above:
                        # self.windows_above[event.window] = deco
                    # elif event.stack_mode == X.Below:
                        # self.windows_below[event.window] = deco
                # 
                continue
            #
            #
            if not _is_running:
                return
        
    
    # # TO DO
    # def on_start(self):
        # children = self.root.query_tree().children
        # for win in children:
            # # skip windows dont want decoration
            # attrs = win.get_attributes()
            # if attrs.override_redirect:
                # continue
            # #
            # # skip the window manager
            # if self.get_window_name(win) == "qtwm-1":
                # if not attrs.override_redirect:
                    # event.window.change_attributes(override_redirect=1)
                # #
                # continue
            # #
            # # skip the dock
            # if self.get_window_name(win) == "qtdock-1":
                # # if not attrs.override_redirect:
                    # # event.window.change_attributes(override_redirect=1)
                # continue
            # #
            # WIN_TYPE = self.get_window_type(win, "_NET_WM_WINDOW_TYPE")
            # #
            # geom = win.get_geometry()
            # childName = self.get_window_name(win)
            # if childName == "qtdock-1":
                # continue
            # self.sig.emit([win, geom.x, geom.y, geom.width, geom.height, 1, childName])
            # #
            # global all_windows
            # global all_windows_stack
            # all_windows.append(win)
            # all_windows_stack.append(win)


    def on_supported_attributes(self):
        attributes = [
            '_NET_SUPPORTED',
            'WM_PROTOCOLS',
            '_NET_ACTIVE_WINDOW',
            '_NET_CLIENT_LIST',
            '_NET_CLIENT_LIST_STACKING',
            '_NET_WM_STATE',
            '_NET_WM_MOVERESIZE',
            '_NET_CLOSE_WINDOW',
            '_NET_WM_STRUT_PARTIAL',
            '_NET_WM_STRUT',
            '_NET_WM_STATE_FULLSCREEN',
            '_NET_WM_STATE_MAXIMIZE_VERT',
            '_NET_WM_STATE_MAXIMIZE_HORZ',
            '_NET_WM_STATE_ABOVE',
            '_NET_WM_STATE_BELOW',
            '_NET_WM_STATE_MODAL',
            'WM_TRANSIENT_FOR',
            '_NET_SUPPORTING_WM_CHECK',
            '_NET_WM_ACTION_CLOSE',
            '_NET_WM_ICON',
            '_NET_WM_NAME',
            'WM_NAME',
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
            '_NET_WM_ALLOWED_ACTIONS',
            '_NET_WM_ACTION_MOVE',
            '_NET_WM_ACTION_RESIZE',
            '_NET_WM_ACTION_MINIMIZE',
            '_NET_WM_ACTION_MAXIMIZE_VERT',
            '_NET_WM_ACTION_MAXIMIZE_HORZ',
            '_NET_WM_ACTION_FULLSCREEN',
            'WM_S0',
            'MANAGER',
            'WM_DELETE_WINDOW',
        ]
        self.root.change_property(
            self.display.get_atom('_NET_SUPPORTED'),
            Xatom.ATOM,
            32,
            [self.display.get_atom(x) for x in attributes],)
        self.display.sync()
        
        
    def _update_client_list(self):
        self.root.change_property(
            self.display.get_atom('_NET_CLIENT_LIST'),
            Xatom.WINDOW,
            32,
            [window.id for window in self.all_windows],)
        self.display.sync()
        
        
    def _update_client_list_stack(self):
        self.root.change_property(
            self.display.get_atom('_NET_CLIENT_LIST_STACKING'),
            Xatom.WINDOW,
            32,
            [window.id for window in self.all_windows_stack],)
        self.display.sync()
        
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
        self.display.sync()
    
    
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
        protc = None
        try:
            protc = win.get_wm_protocols()
        except:
            return
            # if win in self.DECO_WIN:
                # if self.DECO_WIN[win]:
                    # win = self.DECO_WIN[win]
                    # _DELETE_PROTOCOL = 0
        #
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
                #return
            #
            else:
                win.kill_client()
                #return
        #
        else:
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
            self.display.sync()
    
    # # activate the window by request - win deco type
    # def _activate_window2(self, window, dwin, _type):
        # wm_state = self.NET_WM_STATE
        # _atm = self.NET_ACTIVE_WINDOW
        # # _data = [1, X.CurrentTime,window.id,0,0]
        # _data = [0,0,0,0,0]
        # sevent = protocol.event.ClientMessage(
        # window = window,
        # client_type = _atm,
        # data=(32, (_data))
        # )
        # mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        # self.root.send_event(event=sevent, event_mask=mask)
        # self.display.flush()
        # self.display.sync()
    
    # activate the window by request - win deco type
    def _activate_window(self, win, dwin, _type):
        if win == self.active_window:
            return
        #
        if win and win in self.all_windows:
            # the old active window
            if self.active_window:
                if self.active_window in self.DECO_WIN:
                    if self.DECO_WIN[self.active_window]:
                        self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                        # self.display.sync()
                        # self.DECO_WIN[self.active_window].grab_button(1, X.AnyModifier, True,
                                    # X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                    # X.GrabModeAsync, X.NONE, X.NONE)
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
            if dwin:
                dwin.change_attributes(border_pixel=border_color1)
                # dwin.ungrab_button(1, X.AnyModifier)
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
            # remove the demands attention hint
            hints = -1
            try:
                hints = self.active_window.get_wm_hints() or { 'flags': 0 }
            except:
                pass
            if hints != -1 and (hints['flags'] & Xutil.UrgencyHint):
                hints['flags'] &= ~Xutil.UrgencyHint
                self.active_window.set_wm_hints(hints)
                self.display.flush()
                ### message to everyone else, for resetting
                _window = self.active_window
                _message_type = self.NET_WM_STATE
                _format = 32
                _atom1 = self.STATE_DEMANDS_ATTENTION
                _data = [0, _atom1, 0, 0, 0]
                #
                sevent = protocol.event.ClientMessage(
                window = _window,
                client_type = self.NET_WM_STATE,
                data=(32, (_data))
                )
                mask = (X.SubstructureRedirectMask | X.SubstructureNotifyMask)
                self.root.send_event(sevent, event_mask=mask)
                self.display.sync()
                self.display.flush()
            #
            self._update_active_window(self.active_window)
            #
            # notifications
            try:
                for nwin in self.notification_windows:
                    nwin.configure(stack_mode=X.Above)
            except:
                pass
    
    # find a window to set as active
    # after destroy and mini/maximize
    def _find_and_update_the_active(self, win):
        # the active window closed or minimized
        if win == self.active_window:
            #
            if self.active_window in self.DECO_WIN and win in self.root.query_tree().children:
                if self.DECO_WIN[self.active_window]:
                    self.DECO_WIN[self.active_window].change_attributes(border_pixel=border_color2)
                    self.display.sync()
                    # self.DECO_WIN[self.active_window].grab_button(1, X.AnyModifier, True,
                                # X.ButtonPressMask|X.ButtonReleaseMask|X.EnterWindowMask, X.GrabModeAsync,
                                # X.GrabModeAsync, X.NONE, X.NONE)
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
            _has_been_found = 0
            if len(self.all_windows_stack) > 0:
                # _has_been_found = 0
                for iitem in self.all_windows_stack[::-1]:
                    # skip desktop and docks
                    if iitem in self.dock_windows:
                        continue
                    if iitem in self.desktop_window:
                        continue
                    # skip minimized windows
                    # error without try maybe
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
                            # self.DECO_WIN[iitem].ungrab_button(1, X.AnyModifier)
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
                        
    
    # windows in minimized state: window:[deco]
    def minimize_window(self, win, ttype):
        #######
        # 3 keyboard action minimize the active window or from the minimize button
        # 77 eventually unminimize before activating a new window
        # WithdrawnState 0 - NormalState 1 - IconicState 3
        # hidden: 1 to hide (code 11) and 2 (code 22) to toggle - 0 (code 10) to unhide
        #######
        # minimize
        # if ttype == 3 or ttype == 2 or ttype == 1:
        if ttype == 3 or ttype == 0 or ttype == 11 or ttype == 22:
            if not win in self.MINIMIZED_WINDOWS:
                if win in self.DECO_WIN:
                    deco = self.DECO_WIN[win]
                    # Xutil.WithdrawnState, Xutil.NormalState, Xutil.IconicState
                    win.set_wm_state(state = Xutil.WithdrawnState, icon = X.NONE)
                    self.display.sync()
                    self.display.flush()
                    #
                    # set the hidden state
                    win.change_property(
                        self.NET_WM_STATE,
                        self.WM_HIDDEN,
                        32,
                        [2],
                        X.PropModeReplace)
                    self.display.sync()
                    #
                    # in X.UnmapNotifier
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
        # if ttype == 1 or ttype == 2 or ttype == 3 or ttype == 77:
        if ttype == 0 or ttype == 10 or ttype == 77:
            deco = None
            if win in self.MINIMIZED_WINDOWS:
                deco = self.MINIMIZED_WINDOWS[win]
            # failure - only for code 77
            else:
                if ttype == 77:
                    return 1
            ### A1
            # if deco:
                # # deco.map()
                # deco.raise_window()
                # # self.display.sync()
                # # self.display.flush()
            # win.map()
            # win.raise_window()
            # if deco:
                # deco.map()
            ###
            # Xutil.WithdrawnState, Xutil.NormalState, Xutil.IconicState
            win.set_wm_state(state = Xutil.NormalState, icon = X.NONE)
            # self.display.sync()
            # set the hidden state
            win.change_property(
                self.NET_WM_STATE,
                self.WM_HIDDEN,
                32,
                [0],
                X.PropModeReplace)
            self.display.sync()
            #
            if win in self.MINIMIZED_WINDOWS:
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
            if win in self.DECO_WIN:
                if self.DECO_WIN[win]:
                    self.DECO_WIN[win].change_attributes(border_pixel=border_color1)
                    # self.display.flush()
                    # self.DECO_WIN[win].map()
                    self.DECO_WIN[win].raise_window()
                else:
                    win.change_attributes(border_pixel=border_color1)
                self.display.flush()
            #
            win.ungrab_button(1, X.AnyModifier)
            win.set_input_focus(X.RevertToPointerRoot, X.CurrentTime)
            ### A2
            win.map()
            win.raise_window()
            if self.DECO_WIN[win]:
                self.DECO_WIN[win].map()
            ###
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
            # success - only for code 77
            return 0

                
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
        ##### fixed size window
        # _minw = 0
        # _maxw = 0
        # _minh = 0
        # _maxh = 0
        try:
            _normal_hints = win.get_wm_normal_hints()
            if hasattr(_normal_hints, 'max_height'):
                _minw = _normal_hints['min_width']
                _maxw = _normal_hints['max_width']
                _minh = _normal_hints['min_height']
                _maxh = _normal_hints['max_height']
                if _minw == _maxw and _minh == _maxh:
                    return
        except:
            pass
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
    
    def get_window_cmd(self, window):
        try:
            cmd, cls = window.get_wm_class()
        except:
            return "X"
        if cmd is not None:
            return cmd
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
    
            
