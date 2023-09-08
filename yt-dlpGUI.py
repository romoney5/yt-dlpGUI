# import gzip
# import shutil
import configparser
import json
import re
import subprocess
import sys
from datetime import timedelta, datetime
from tkinter import messagebox


try:
    import logging
    import random
    import threading
    import time
    import traceback
    import os

    import requests
    import yt_dlp.utils
    from kivy import Config, app
    from kivy.animation import Animation
    from kivy.app import App
    from kivy.clock import mainthread, Clock
    from kivy.config import ConfigParser
    from kivy.core.window import Window
    from kivy.lang import Builder
    # from kivy.graphics import Color, Rectangle
    # from kivy.uix.boxlayout import BoxLayout
    # from kivy.base import runTouchApp
    from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, BoxShadow
    from kivy.utils import get_color_from_hex
    from kivy.uix.button import Button
    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.boxlayout import BoxLayout
    from kivy.uix.label import Label
    from kivy.uix.popup import Popup
    from kivy.uix.progressbar import ProgressBar
    from kivy.uix.settings import SettingsWithSpinner, Settings, SettingsWithSidebar
    # from kivy.uix.screenmanager import Screen, ScreenManager
    from kivy.uix.textinput import TextInput
    # from kivy.uix.widget import Widget
    from kivy.uix.filechooser import FileChooserListView
    from kivy.uix.videoplayer import VideoPlayer
    from kivy.core.text import LabelBase
    # from yt_dlp import YoutubeDL
    import static_ffmpeg
    import ffpyplayer
    from static_ffmpeg import run
    import kivy_gradient
    import pyautogui
    import pyperclip
    import sys
except ImportError as e:
    print("Whoops! You have to put the CD in your computer")
    messagebox.showerror("yt-dlpGUI","There is a package not installed. Let me install it for you: "+e.msg)
    # if (e.msg=="No module named 'yt_dlp'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    # if (e.msg=="No module named 'kivy'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kivy"])
    # if (e.msg=="No module named 'static_ffmpeg'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "static-ffmpeg"])
    # if (e.msg=="No module named 'ffpyplayer'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ffpyplayer"])
    # if (e.msg=="No module named 'kivy_gradient'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "kivygradient"])
    # if (e.msg=="No module named 'pyautogui'"):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    # messagebox.showerror("yt-dlpGUI",e.msg)
    print(f"Restarting!")
    messagebox.showinfo("yt-dlpGUI","Restarting!")
    os.execv(sys.executable, ['python'] + sys.argv)
if sys.platform=="win32":
    import ctypes
    ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 0 )

Window.size = (900,600)
Config.set('kivy','exit_on_escape',0)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color=(0, 0, 0, 0)
        self.font_name="segoe"
        # self.col_def = [88 / 255, 88 / 255, 88 / 255, 1]
        self.col_sel = [50 / 255, 164 / 255, 206*2 / 255, 1]
        with self.canvas.before:
            self.col = Color(self.col_def[0],self.col_def[1],self.col_def[2],self.col_def[3])  # Set the color you want
            radius = 7
            self.sh = BoxShadow(pos=self.pos, size=self.size, offset=(0, -10), blur_radius=25, spread_radius=(-10, -10), border_radius=(radius, radius, radius, radius))
            self.button_bg = RoundedRectangle(pos=self.pos, size=self.size, radius=[(radius, radius), (radius, radius), (radius, radius), (radius, radius)], texture=kivy_gradient.Gradient.vertical(get_color_from_hex("FFFFFF"),get_color_from_hex("E0E0E0"),get_color_from_hex("E0E0E0"),get_color_from_hex("E0E0E0")))
            self.bind(pos=lambda instance, value: self.update_pos(value),
                                 size=lambda instance, value: self.update_size(value))
            #                      on_release=lambda instance: setattr(self, 'col', Color()))

    # def update_rect(self, instance, value):
    #     self.button_bg.pos = instance.pos
    #     self.button_bg.size = instance.size
    def update_pos(self, value):
        self.button_bg.pos = value
        self.sh.pos = value
    def update_size(self, value):
        self.button_bg.size = value
        self.sh.size = value

    def on_press(self):
        # Change button background color when clicked
        Animation(rgba = (self.col_sel[0],self.col_sel[1],self.col_sel[2],self.col_sel[3]), duration=.1).start(self.col)
        # self.col.  # Change to blue
    def on_release(self):
        # Change button background color when clicked
        Animation(rgba = (self.col_def[0],self.col_def[1],self.col_def[2],self.col_def[3]), duration=.1).start(self.col)
        # self.col.rgba = (88 / 255, 88 / 255, 88 / 255, 1)  # Change to blue
class CustomPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overlay_color=(0, 0, 0, 0)
        with Window.canvas:
            # Rectangle(size_hint=(1, 1),background_color = col)
            Color(0,0,0,.7)  # Set the color you want
            self.bg = Rectangle(size=Window.size)
            Window.bind(size=lambda instance, value: self.update_size(value))
            #                      on_release=lambda instance: setattr(self, 'col', Color()))

    # def update_rect(self, instance, value):
    #     self.button_bg.pos = instance.pos
    #     self.button_bg.size = instance.size
    def update_size(self, value):
        self.bg.size = (Window.size[0]*1.5,Window.size[1]*1.5)
        Clock.schedule_once(lambda dt: setattr(self.bg, 'size',Window.size),0)
    def on_pre_dismiss(self):
        Window.canvas.remove(self.bg)
class RootLayout(FloatLayout):
    def __init__(self, app, **kwargs):
        super().__init__(**kwargs)
        self.app = app  # Store the instance of the main app
    def on_touch_down(self, touch):
        if touch.button == 'right':
            # ydlpg = ytdlpgui()
            if self.app.download_button.collide_point(touch.pos[0],touch.pos[1]):
                fl = FloatLayout()
                popup = Popup(title='Download options',
                              content=fl,
                              size_hint=(None, None), size=(700, 500))
                button1 = CustomButton(text='Download', pos_hint={'right': .88, 'top': .98}, size_hint=(.76, .1), on_release=self.app.download)
                button1.bind(on_release=popup.dismiss)
                button4 = CustomButton(text='Download part of a video', pos_hint={'right': .88, 'top': .83}, size_hint=(.76, .1), on_release=self.app.dlp)
                button4.bind(on_release=popup.dismiss)
                button2 = CustomButton(text='Download from Clipboard', pos_hint={'right': .88, 'top': .68}, size_hint=(.76, .1), on_release=self.app.dlcl)
                button2.bind(on_release=popup.dismiss)
                button3 = CustomButton(text='Download from Browser Tab', pos_hint={'right': .88, 'top': .53}, size_hint=(.76, .1), on_release=self.app.dlbr)
                button3.bind(on_release=popup.dismiss)
                fl.add_widget(button1)
                fl.add_widget(button2)
                fl.add_widget(button3)
                fl.add_widget(button4)
                fl.add_widget(Label(size_hint=(.1, .08), pos_hint={'right': .08, 'top': .08},text="Ver. a2.2.0",halign='left',font_size=10,font_name="segoe"))
                popup.open()
            return True
        super().on_touch_down(touch)
class WrappedLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(
            width=lambda *x:
            self.setter('text_size')(self, (self.width, None)),
            texture_size=lambda *x: self.setter('height')(self, self.texture_size[1]))


def time_to_seconds(time_str):
    # regular expression to match (h)h:mm:ss or mm:ss format
    pattern = r'^(\d{1,2}:)?(\d{1,2}):(\d{2})$'
    match = re.match(pattern, time_str)

    if match:
        parts = match.groups()
        hours = int(parts[0][:-1]) if parts[0] else 0
        minutes = int(parts[1])
        seconds = int(parts[2])
        total_seconds = hours * 3600 + minutes * 60 + seconds
        return total_seconds
    else:
        return time_str  # return unchanged if not in the expected format

class ytdlpgui(App):
    download_button = None
    def update_please(self,instance):
        # Download the file from the URL
        response = requests.get("https://github.com/romoney5/yt-dlpGUI/raw/master/yt-dlpGUI.py")
        if response.status_code == 200:
            with open("yt-dlpGUI.py", 'wb') as file:
                file.write(response.content)
            print(f"Downloaded a yt-dlpGUI update successfully")
            print(f"Restarting!")
            messagebox.showinfo("yt-dlpGUI","Restarting!")
            os.execv(sys.executable, ['python'] + sys.argv)
        else:
            print("Failed to download the file")
    def dlcl(self,instance):
        self.url = pyperclip.paste()
        self.download()
    def dlbr(self,instance):
        Window.hide()
        pyautogui.hotkey('alt','tab')
        pyautogui.press('f6')
        # time.sleep(.1)
        pyautogui.hotkey('ctrl','c')
        # time.sleep(.1)
        self.url = pyperclip.paste()
        pyautogui.press('esc')
        Window.show()
        self.download()

    def dl(self,inp1,inp2,inp3):
        self.url = inp3.text
        i1 = time_to_seconds(inp1.text)
        i2 = time_to_seconds(inp2.text)
        # print(f"*{i1}-{i2}")
        self.download(None,[i1,i2])
    def dlp(self,instance):
        fl = FloatLayout()
        self.popup = Popup(title='Time selection',
                           content=fl,
                           size_hint=(None, None), size=(700, 500))
        inp1 = TextInput(hint_text='Start time',text='0:00', pos_hint={'right': .75, 'top': .76}, size_hint=(.5, .07),multiline=False)
        inp2 = TextInput(hint_text='End time',text='1:00', pos_hint={'right': .75, 'top': .68}, size_hint=(.5, .07),multiline=False)
        inp3 = TextInput(hint_text='URL',text=self.url_input.text, pos_hint={'right': .75, 'top': .51}, size_hint=(.5, .07),multiline=False)
        button1 = CustomButton(text='Download', pos_hint={'right': .88, 'top': .16}, size_hint=(.76, .1), on_release=lambda dt:self.dl(inp1,inp2,inp3))
        button1.bind(on_release=self.popup.dismiss)
        fl.add_widget(button1)
        fl.add_widget(inp1)
        fl.add_widget(inp2)
        fl.add_widget(inp3)
        self.popup.open()

    def build(self):
        self.config.read('ytdlp_settings.ini')
        try:
            self.theme = self.config.get('app','mode')
        except configparser.NoSectionError:
            self.theme = "Dark"
        if (self.theme == "Light"):
            Window.clearcolor = (222/255, 222/255, 229/255, 1)
            CustomButton.col_def = [88 / 155, 88 / 155, 88 / 155, 1]
        else:
            Window.clearcolor = (0.06, 0.06, 0.08, 1)
            CustomButton.col_def = [88 / 255, 88 / 255, 88 / 255, 1]

        self.layout = RootLayout(app=self)
        # Navigation Bar
        nav_bar = RootLayout(app=self)
        nav_button1 = CustomButton(text='Update', pos_hint={'right': 0.5, 'top': .98}, size_hint=(.46, .05),on_release=self.update_please)
        nav_button2 = CustomButton(text='Settings', pos_hint={'right': .98, 'top': .98}, size_hint=(.46, .05),on_release=self.open_settings)
        nav_button3 = CustomButton(text='Multimedia Player', pos=(10, 100), size_hint=(.16, .05),on_release=self.video)
        nav_bar.add_widget(nav_button1)
        nav_bar.add_widget(nav_button2)
        nav_bar.add_widget(nav_button3)
        # nav_bar.add_widget(Widget())
        self.layout.add_widget(nav_bar)
        LabelBase.register(name="segoe", fn_regular="Roboto-Bold.ttf")
        self.url_input = TextInput(hint_text='URL/Arguments', pos=(10, 70), size_hint=(.4, .05),multiline=False,font_name="segoe")
        self.download_button = CustomButton(text='Download video', on_release=self.download, pos=(10, 20), size_hint=(.4, .08))
        ytdlpgui.download_button = self.download_button
        self.progress_bar = ProgressBar(max=100, value=0, pos=(10, 0), size_hint=(.975, .05))
        self.consolelog = TextInput(size_hint=(.8, .74), pos_hint={'right': .98, 'top': .92},background_color=(0.1, 0.1, 0.16, 1),foreground_color=(1, 1, 1, 1),font_name="segoe")
        self.prlabel = Label(size_hint=(.4, .08), pos_hint={'right': .82, 'top': .12},text="0% complete",halign='left',font_size=34-6,font_name="segoe")
        self.prlabel.bind(size=self.prlabel.setter('text_size'))
        if (self.theme == "Light"):
            self.prlabel.color = (.2,.2,.2,1)
            self.consolelog.background_color = (1,1,1,1)
            self.consolelog.foreground_color = (.2,.2,.2,1)
        # else:
        #     Window.clearcolor = (0.06, 0.06, 0.08, 1)
        #     CustomButton.col_def = [88 / 255, 88 / 255, 88 / 255, 1]
        # time.sleep(0.1)
        self.consolelog.text = '''This documentation is a placeholder, it may be replaced later.\nUsage: [OPTIONS] URL [URL...]\n\nOptions:\n  General Options:\n    --version                       Print program version and exit\n    -U, --update                    Update this program to the latest version\n    --no-update                     Do not check for updates (default)\n    -i, --ignore-errors             Ignore download and postprocessing errors.\n                                    The download will be considered successful\n                                    even if the postprocessing fails\n    --no-abort-on-error             Continue with next video on download errors;\n                                    e.g. to skip unavailable videos in a\n                                    playlist (default)\n    --abort-on-error                Abort downloading of further videos if an\n                                    error occurs (Alias: --no-ignore-errors)\n    --dump-user-agent               Display the current user-agent and exit\n    --list-extractors               List all supported extractors and exit\n    --extractor-descriptions        Output descriptions of all supported\n                                    extractors and exit\n    --use-extractors NAMES          Extractor names to use separated by commas.\n                                    You can also use regexes, "all", "default"\n                                    and "end" (end URL matching); e.g. --ies\n                                    "holodex.*,end,youtube". Prefix the name\n                                    with a "-" to exclude it, e.g. --ies\n                                    default,-generic. Use --list-extractors for\n                                    a list of extractor names. (Alias: --ies)\n    --default-search PREFIX         Use this prefix for unqualified URLs. E.g.\n                                    "gvsearch2:python" downloads two videos from\n                                    google videos for the search term "python".\n                                    Use the value "auto" to let yt-dlp guess\n                                    ("auto_warning" to emit a warning when\n                                    guessing). "error" just throws an error. The\n                                    default value "fixup_error" repairs broken\n                                    URLs, but emits an error if this is not\n                                    possible instead of searching\n    --ignore-config                 Don't load any more configuration files\n                                    except those given by --config-locations.\n                                    For backward compatibility, if this option\n                                    is found inside the system configuration\n                                    file, the user configuration is not loaded.\n                                    (Alias: --no-config)\n    --no-config-locations           Do not load any custom configuration files\n                                    (default). When given inside a configuration\n                                    file, ignore all previous --config-locations\n                                    defined in the current file\n    --config-locations PATH         Location of the main configuration file;\n                                    either the path to the config or its\n                                    containing directory ("-" for stdin). Can be\n                                    used multiple times and inside other\n                                    configuration files\n    --flat-playlist                 Do not extract the videos of a playlist,\n                                    only list them\n    --no-flat-playlist              Extract the videos of a playlist\n    --live-from-start               Download livestreams from the start.\n                                    Currently only supported for YouTube\n                                    (Experimental)\n    --no-live-from-start            Download livestreams from the current time\n                                    (default)\n    --wait-for-video MIN[-MAX]      Wait for scheduled streams to become\n                                    available. Pass the minimum number of\n                                    seconds (or range) to wait between retries\n    --no-wait-for-video             Do not wait for scheduled streams (default)\n    --mark-watched                  Mark videos watched (even with --simulate)\n    --no-mark-watched               Do not mark videos watched (default)\n    --no-colors                     Do not emit color codes in output (Alias:\n                                    --no-colours)\n    --compat-options OPTS           Options that can help keep compatibility\n                                    with youtube-dl or youtube-dlc\n                                    configurations by reverting some of the\n                                    changes made in yt-dlp. See "Differences in\n                                    default behavior" for details\n    --alias ALIASES OPTIONS         Create aliases for an option string. Unless\n                                    an alias starts with a dash "-", it is\n                                    prefixed with "--". Arguments are parsed\n                                    according to the Python string formatting\n                                    mini-language. E.g. --alias get-audio,-X\n                                    "-S=aext:{0},abr -x --audio-format {0}"\n                                    creates options "--get-audio" and "-X" that\n                                    takes an argument (ARG0) and expands to\n                                    "-S=aext:ARG0,abr -x --audio-format ARG0".\n                                    All defined aliases are listed in the --help\n                                    output. Alias options can trigger more\n                                    aliases; so be careful to avoid defining\n                                    recursive options. As a safety measure, each\n                                    alias may be triggered a maximum of 100\n                                    times. This option can be used multiple\n                                    times\n\n  Network Options:\n    --proxy URL                     Use the specified HTTP/HTTPS/SOCKS proxy. To\n                                    enable SOCKS proxy, specify a proper scheme,\n                                    e.g. socks5://user:pass@127.0.0.1:1080/.\n                                    Pass in an empty string (--proxy "") for\n                                    direct connection\n    --socket-timeout SECONDS        Time to wait before giving up, in seconds\n    --source-address IP             Client-side IP address to bind to\n    -4, --force-ipv4                Make all connections via IPv4\n    -6, --force-ipv6                Make all connections via IPv6\n\n  Geo-restriction:\n    --geo-verification-proxy URL    Use this proxy to verify the IP address for\n                                    some geo-restricted sites. The default proxy\n                                    specified by --proxy (or none, if the option\n                                    is not present) is used for the actual\n                                    downloading\n    --geo-bypass                    Bypass geographic restriction via faking\n                                    X-Forwarded-For HTTP header (default)\n    --no-geo-bypass                 Do not bypass geographic restriction via\n                                    faking X-Forwarded-For HTTP header\n    --geo-bypass-country CODE       Force bypass geographic restriction with\n                                    explicitly provided two-letter ISO 3166-2\n                                    country code\n    --geo-bypass-ip-block IP_BLOCK  Force bypass geographic restriction with\n                                    explicitly provided IP block in CIDR\n                                    notation\n\n  Video Selection:\n    -I, --playlist-items ITEM_SPEC  Comma separated playlist_index of the videos\n                                    to download. You can specify a range using\n                                    "[START]:[STOP][:STEP]". For backward\n                                    compatibility, START-STOP is also supported.\n                                    Use negative indices to count from the right\n                                    and negative STEP to download in reverse\n                                    order. E.g. "-I 1:3,7,-5::2" used on a\n                                    playlist of size 15 will download the videos\n                                    at index 1,2,3,7,11,13,15\n    --min-filesize SIZE             Do not download any videos smaller than\n                                    SIZE, e.g. 50k or 44.6M\n    --max-filesize SIZE             Do not download any videos larger than SIZE,\n                                    e.g. 50k or 44.6M\n    --date DATE                     Download only videos uploaded on this date.\n                                    The date can be "YYYYMMDD" or in the format\n                                    [now|today|yesterday][-N[day|week|month|year\n                                    ]]. E.g. --date today-2weeks\n    --datebefore DATE               Download only videos uploaded on or before\n                                    this date. The date formats accepted is the\n                                    same as --date\n    --dateafter DATE                Download only videos uploaded on or after\n                                    this date. The date formats accepted is the\n                                    same as --date\n    --match-filters FILTER          Generic video filter. Any "OUTPUT TEMPLATE"\n                                    field can be compared with a number or a\n                                    string using the operators defined in\n                                    "Filtering Formats". You can also simply\n                                    specify a field to match if the field is\n                                    present, use "!field" to check if the field\n                                    is not present, and "&" to check multiple\n                                    conditions. Use a "\" to escape "&" or\n                                    quotes if needed. If used multiple times,\n                                    the filter matches if atleast one of the\n                                    conditions are met. E.g. --match-filter\n                                    !is_live --match-filter "like_count>?100 &\n                                    description~='(?i)\bcats \& dogs\b'" matches\n                                    only videos that are not live OR those that\n                                    have a like count more than 100 (or the like\n                                    field is not available) and also has a\n                                    description that contains the phrase "cats &\n                                    dogs" (caseless). Use "--match-filter -" to\n                                    interactively ask whether to download each\n                                    video\n    --no-match-filter               Do not use generic video filter (default)\n    --no-playlist                   Download only the video, if the URL refers\n                                    to a video and a playlist\n    --yes-playlist                  Download the playlist, if the URL refers to\n                                    a video and a playlist\n    --age-limit YEARS               Download only videos suitable for the given\n                                    age\n    --download-archive FILE         Download only videos not listed in the\n                                    archive file. Record the IDs of all\n                                    downloaded videos in it\n    --no-download-archive           Do not use archive file (default)\n    --max-downloads NUMBER          Abort after downloading NUMBER files\n    --break-on-existing             Stop the download process when encountering\n                                    a file that is in the archive\n    --break-on-reject               Stop the download process when encountering\n                                    a file that has been filtered out\n    --break-per-input               --break-on-existing, --break-on-reject,\n                                    --max-downloads, and autonumber resets per\n                                    input URL\n    --no-break-per-input            --break-on-existing and similar options\n                                    terminates the entire download queue\n    --skip-playlist-after-errors N  Number of allowed failures until the rest of\n                                    the playlist is skipped\n\n  Download Options:\n    -N, --concurrent-fragments N    Number of fragments of a dash/hlsnative\n                                    video that should be downloaded concurrently\n                                    (default is 1)\n    -r, --limit-rate RATE           Maximum download rate in bytes per second,\n                                    e.g. 50K or 4.2M\n    --throttled-rate RATE           Minimum download rate in bytes per second\n                                    below which throttling is assumed and the\n                                    video data is re-extracted, e.g. 100K\n    -R, --retries RETRIES           Number of retries (default is 10), or\n                                    "infinite"\n    --file-access-retries RETRIES   Number of times to retry on file access\n                                    error (default is 3), or "infinite"\n    --fragment-retries RETRIES      Number of retries for a fragment (default is\n                                    10), or "infinite" (DASH, hlsnative and ISM)\n    --retry-sleep [TYPE:]EXPR       Time to sleep between retries in seconds\n                                    (optionally) prefixed by the type of retry\n                                    (http (default), fragment, file_access,\n                                    extractor) to apply the sleep to. EXPR can\n                                    be a number, linear=START[:END[:STEP=1]] or\n                                    exp=START[:END[:BASE=2]]. This option can be\n                                    used multiple times to set the sleep for the\n                                    different retry types, e.g. --retry-sleep\n                                    linear=1::2 --retry-sleep fragment:exp=1:20\n    --skip-unavailable-fragments    Skip unavailable fragments for DASH,\n                                    hlsnative and ISM downloads (default)\n                                    (Alias: --no-abort-on-unavailable-fragment)\n    --abort-on-unavailable-fragment\n                                    Abort download if a fragment is unavailable\n                                    (Alias: --no-skip-unavailable-fragments)\n    --keep-fragments                Keep downloaded fragments on disk after\n                                    downloading is finished\n    --no-keep-fragments             Delete downloaded fragments after\n                                    downloading is finished (default)\n    --buffer-size SIZE              Size of download buffer, e.g. 1024 or 16K\n                                    (default is 1024)\n    --resize-buffer                 The buffer size is automatically resized\n                                    from an initial value of --buffer-size\n                                    (default)\n    --no-resize-buffer              Do not automatically adjust the buffer size\n    --http-chunk-size SIZE          Size of a chunk for chunk-based HTTP\n                                    downloading, e.g. 10485760 or 10M (default\n                                    is disabled). May be useful for bypassing\n                                    bandwidth throttling imposed by a webserver\n                                    (experimental)\n    --playlist-random               Download playlist videos in random order\n    --lazy-playlist                 Process entries in the playlist as they are\n                                    received. This disables n_entries,\n                                    --playlist-random and --playlist-reverse\n    --no-lazy-playlist              Process videos in the playlist only after\n                                    the entire playlist is parsed (default)\n    --xattr-set-filesize            Set file xattribute ytdl.filesize with\n                                    expected file size\n    --hls-use-mpegts                Use the mpegts container for HLS videos;\n                                    allowing some players to play the video\n                                    while downloading, and reducing the chance\n                                    of file corruption if download is\n                                    interrupted. This is enabled by default for\n                                    live streams\n    --no-hls-use-mpegts             Do not use the mpegts container for HLS\n                                    videos. This is default when not downloading\n                                    live streams\n    --download-sections REGEX       Download only chapters whose title matches\n                                    the given regular expression. Time ranges\n                                    prefixed by a "*" can also be used in place\n                                    of chapters to download the specified range.\n                                    Needs ffmpeg. This option can be used\n                                    multiple times to download multiple\n                                    sections, e.g. --download-sections\n                                    "*10:15-15:00" --download-sections "intro"\n    --downloader [PROTO:]NAME       Name or path of the external downloader to\n                                    use (optionally) prefixed by the protocols\n                                    (http, ftp, m3u8, dash, rstp, rtmp, mms) to\n                                    use it for. Currently supports native,\n                                    aria2c, avconv, axel, curl, ffmpeg, httpie,\n                                    wget. You can use this option multiple times\n                                    to set different downloaders for different\n                                    protocols. E.g. --downloader aria2c\n                                    --downloader "dash,m3u8:native" will use\n                                    aria2c for http/ftp downloads, and the\n                                    native downloader for dash/m3u8 downloads\n                                    (Alias: --external-downloader)\n    --downloader-args NAME:ARGS     Give these arguments to the external\n                                    downloader. Specify the downloader name and\n                                    the arguments separated by a colon ":". For\n                                    ffmpeg, arguments can be passed to different\n                                    positions using the same syntax as\n                                    --postprocessor-args. You can use this\n                                    option multiple times to give different\n                                    arguments to different downloaders (Alias:\n                                    --external-downloader-args)\n\n  Filesystem Options:\n    -a, --batch-file FILE           File containing URLs to download ("-" for\n                                    stdin), one URL per line. Lines starting\n                                    with "#", ";" or "]" are considered as\n                                    comments and ignored\n    --no-batch-file                 Do not read URLs from batch file (default)\n    -P, --paths [TYPES:]PATH        The paths where the files should be\n                                    downloaded. Specify the type of file and the\n                                    path separated by a colon ":". All the same\n                                    TYPES as --output are supported.\n                                    Additionally, you can also provide "home"\n                                    (default) and "temp" paths. All intermediary\n                                    files are first downloaded to the temp path\n                                    and then the final files are moved over to\n                                    the home path after download is finished.\n                                    This option is ignored if --output is an\n                                    absolute path\n    -o, --output [TYPES:]TEMPLATE   Output filename template; see "OUTPUT\n                                    TEMPLATE" for details\n    --output-na-placeholder TEXT    Placeholder for unavailable fields in\n                                    "OUTPUT TEMPLATE" (default: "NA")\n    --restrict-filenames            Restrict filenames to only ASCII characters,\n                                    and avoid "&" and spaces in filenames\n    --no-restrict-filenames         Allow Unicode characters, "&" and spaces in\n                                    filenames (default)\n    --windows-filenames             Force filenames to be Windows-compatible\n    --no-windows-filenames          Make filenames Windows-compatible only if\n                                    using Windows (default)\n    --trim-filenames LENGTH         Limit the filename length (excluding\n                                    extension) to the specified number of\n                                    characters\n    -w, --no-overwrites             Do not overwrite any files\n    --force-overwrites              Overwrite all video and metadata files. This\n                                    option includes --no-continue\n    --no-force-overwrites           Do not overwrite the video, but overwrite\n                                    related files (default)\n    -c, --continue                  Resume partially downloaded files/fragments\n                                    (default)\n    --no-continue                   Do not resume partially downloaded\n                                    fragments. If the file is not fragmented,\n                                    restart download of the entire file\n    --part                          Use .part files instead of writing directly\n                                    into output file (default)\n    --no-part                       Do not use .part files - write directly into\n                                    output file\n    --mtime                         Use the Last-modified header to set the file\n                                    modification time (default)\n    --no-mtime                      Do not use the Last-modified header to set\n                                    the file modification time\n    --write-description             Write video description to a .description\n                                    file\n    --no-write-description          Do not write video description (default)\n    --write-info-json               Write video metadata to a .info.json file\n                                    (this may contain personal information)\n    --no-write-info-json            Do not write video metadata (default)\n    --write-playlist-metafiles      Write playlist metadata in addition to the\n                                    video metadata when using --write-info-json,\n                                    --write-description etc. (default)\n    --no-write-playlist-metafiles   Do not write playlist metadata when using\n                                    --write-info-json, --write-description etc.\n    --clean-info-json               Remove some private fields such as filenames\n                                    from the infojson. Note that it could still\n                                    contain some personal information (default)\n    --no-clean-info-json            Write all fields to the infojson\n    --write-comments                Retrieve video comments to be placed in the\n                                    infojson. The comments are fetched even\n                                    without this option if the extraction is\n                                    known to be quick (Alias: --get-comments)\n    --no-write-comments             Do not retrieve video comments unless the\n                                    extraction is known to be quick (Alias:\n                                    --no-get-comments)\n    --load-info-json FILE           JSON file containing the video information\n                                    (created with the "--write-info-json"\n                                    option)\n    --cookies FILE                  Netscape formatted file to read cookies from\n                                    and dump cookie jar in\n    --no-cookies                    Do not read/dump cookies from/to file\n                                    (default)\n    --cookies-from-browser BROWSER[+KEYRING][:PROFILE][::CONTAINER]\n                                    The name of the browser to load cookies\n                                    from. Currently supported browsers are:\n                                    brave, chrome, chromium, edge, firefox,\n                                    opera, safari, vivaldi. Optionally, the\n                                    KEYRING used for decrypting Chromium cookies\n                                    on Linux, the name/path of the PROFILE to\n                                    load cookies from, and the CONTAINER name\n                                    (if Firefox) ("none" for no container) can\n                                    be given with their respective seperators.\n                                    By default, all containers of the most\n                                    recently accessed profile are used.\n                                    Currently supported keyrings are: basictext,\n                                    gnomekeyring, kwallet\n    --no-cookies-from-browser       Do not load cookies from browser (default)\n    --cache-dir DIR                 Location in the filesystem where youtube-dl\n                                    can store some downloaded information (such\n                                    as client ids and signatures) permanently.\n                                    By default $XDG_CACHE_HOME/yt-dlp or\n                                    ~/.cache/yt-dlp\n    --no-cache-dir                  Disable filesystem caching\n    --rm-cache-dir                  Delete all filesystem cache files\n\n  Thumbnail Options:\n    --write-thumbnail               Write thumbnail image to disk\n    --no-write-thumbnail            Do not write thumbnail image to disk\n                                    (default)\n    --write-all-thumbnails          Write all thumbnail image formats to disk\n    --list-thumbnails               List available thumbnails of each video.\n                                    Simulate unless --no-simulate is used\n\n  Internet Shortcut Options:\n    --write-link                    Write an internet shortcut file, depending\n                                    on the current platform (.url, .webloc or\n                                    .desktop). The URL may be cached by the OS\n    --write-url-link                Write a .url Windows internet shortcut. The\n                                    OS caches the URL based on the file path\n    --write-webloc-link             Write a .webloc macOS internet shortcut\n    --write-desktop-link            Write a .desktop Linux internet shortcut\n\n  Verbosity and Simulation Options:\n    -q, --quiet                     Activate quiet mode. If used with --verbose,\n                                    print the log to stderr\n    --no-warnings                   Ignore warnings\n    -s, --simulate                  Do not download the video and do not write\n                                    anything to disk\n    --no-simulate                   Download the video even if printing/listing\n                                    options are used\n    --ignore-no-formats-error       Ignore "No video formats" error. Useful for\n                                    extracting metadata even if the videos are\n                                    not actually available for download\n                                    (experimental)\n    --no-ignore-no-formats-error    Throw error when no downloadable video\n                                    formats are found (default)\n    --skip-download                 Do not download the video but write all\n                                    related files (Alias: --no-download)\n    -O, --print [WHEN:]TEMPLATE     Field name or output template to print to\n                                    screen, optionally prefixed with when to\n                                    print it, separated by a ":". Supported\n                                    values of "WHEN" are the same as that of\n                                    --use-postprocessor, and "video" (default).\n                                    Implies --quiet. Implies --simulate unless\n                                    --no-simulate or later stages of WHEN are\n                                    used. This option can be used multiple times\n    --print-to-file [WHEN:]TEMPLATE FILE\n                                    Append given template to the file. The\n                                    values of WHEN and TEMPLATE are same as that\n                                    of --print. FILE uses the same syntax as the\n                                    output template. This option can be used\n                                    multiple times\n    -j, --dump-json                 Quiet, but print JSON information for each\n                                    video. Simulate unless --no-simulate is\n                                    used. See "OUTPUT TEMPLATE" for a\n                                    description of available keys\n    -J, --dump-single-json          Quiet, but print JSON information for each\n                                    url or infojson passed. Simulate unless\n                                    --no-simulate is used. If the URL refers to\n                                    a playlist, the whole playlist information\n                                    is dumped in a single line\n    --force-write-archive           Force download archive entries to be written\n                                    as far as no errors occur, even if -s or\n                                    another simulation option is used (Alias:\n                                    --force-download-archive)\n    --newline                       Output progress bar as new lines\n    --no-progress                   Do not print progress bar\n    --progress                      Show progress bar, even if in quiet mode\n    --console-title                 Display progress in console titlebar\n    --progress-template [TYPES:]TEMPLATE\n                                    Template for progress outputs, optionally\n                                    prefixed with one of "download:" (default),\n                                    "download-title:" (the console title),\n                                    "postprocess:",  or "postprocess-title:".\n                                    The video's fields are accessible under the\n                                    "info" key and the progress attributes are\n                                    accessible under "progress" key. E.g.\n                                    --console-title --progress-template\n                                    "download-\n                                    title:%(info.id)s-%(progress.eta)s"\n    -v, --verbose                   Print various debugging information\n    --dump-pages                    Print downloaded pages encoded using base64\n                                    to debug problems (very verbose)\n    --write-pages                   Write downloaded intermediary pages to files\n                                    in the current directory to debug problems\n    --print-traffic                 Display sent and read HTTP traffic\n\n  Workarounds:\n    --encoding ENCODING             Force the specified encoding (experimental)\n    --legacy-server-connect         Explicitly allow HTTPS connection to servers\n                                    that do not support RFC 5746 secure\n                                    renegotiation\n    --no-check-certificates         Suppress HTTPS certificate validation\n    --prefer-insecure               Use an unencrypted connection to retrieve\n                                    information about the video (Currently\n                                    supported only for YouTube)\n    --add-header FIELD:VALUE        Specify a custom HTTP header and its value,\n                                    separated by a colon ":". You can use this\n                                    option multiple times\n    --bidi-workaround               Work around terminals that lack\n                                    bidirectional text support. Requires bidiv\n                                    or fribidi executable in PATH\n    --sleep-requests SECONDS        Number of seconds to sleep between requests\n                                    during data extraction\n    --sleep-interval SECONDS        Number of seconds to sleep before each\n                                    download. This is the minimum time to sleep\n                                    when used along with --max-sleep-interval\n                                    (Alias: --min-sleep-interval)\n    --max-sleep-interval SECONDS    Maximum number of seconds to sleep. Can only\n                                    be used along with --min-sleep-interval\n    --sleep-subtitles SECONDS       Number of seconds to sleep before each\n                                    subtitle download\n\n  Video Format Options:\n    -f, --format FORMAT             Video format code, see "FORMAT SELECTION"\n                                    for more details\n    -S, --format-sort SORTORDER     Sort the formats by the fields given, see\n                                    "Sorting Formats" for more details\n    --format-sort-force             Force user specified sort order to have\n                                    precedence over all fields, see "Sorting\n                                    Formats" for more details (Alias: --S-force)\n    --no-format-sort-force          Some fields have precedence over the user\n                                    specified sort order (default)\n    --video-multistreams            Allow multiple video streams to be merged\n                                    into a single file\n    --no-video-multistreams         Only one video stream is downloaded for each\n                                    output file (default)\n    --audio-multistreams            Allow multiple audio streams to be merged\n                                    into a single file\n    --no-audio-multistreams         Only one audio stream is downloaded for each\n                                    output file (default)\n    --prefer-free-formats           Prefer video formats with free containers\n                                    over non-free ones of same quality. Use with\n                                    "-S ext" to strictly prefer free containers\n                                    irrespective of quality\n    --no-prefer-free-formats        Don't give any special preference to free\n                                    containers (default)\n    --check-formats                 Make sure formats are selected only from\n                                    those that are actually downloadable\n    --check-all-formats             Check all formats for whether they are\n                                    actually downloadable\n    --no-check-formats              Do not check that the formats are actually\n                                    downloadable\n    -F, --list-formats              List available formats of each video.\n                                    Simulate unless --no-simulate is used\n    --merge-output-format FORMAT    Containers that may be used when merging\n                                    formats, separated by "/", e.g. "mp4/mkv".\n                                    Ignored if no merge is required. (currently\n                                    supported: avi, flv, mkv, mov, mp4, webm)\n\n  Subtitle Options:\n    --write-subs                    Write subtitle file\n    --no-write-subs                 Do not write subtitle file (default)\n    --write-auto-subs               Write automatically generated subtitle file\n                                    (Alias: --write-automatic-subs)\n    --no-write-auto-subs            Do not write auto-generated subtitles\n                                    (default) (Alias: --no-write-automatic-subs)\n    --list-subs                     List available subtitles of each video.\n                                    Simulate unless --no-simulate is used\n    --sub-format FORMAT             Subtitle format; accepts formats preference,\n                                    e.g. "srt" or "ass/srt/best"\n    --sub-langs LANGS               Languages of the subtitles to download (can\n                                    be regex) or "all" separated by commas, e.g.\n                                    --sub-langs "en.*,ja". You can prefix the\n                                    language code with a "-" to exclude it from\n                                    the requested languages, e.g. --sub-langs\n                                    all,-live_chat. Use --list-subs for a list\n                                    of available language tags\n\n  Authentication Options:\n    -u, --username USERNAME         Login with this account ID\n    -p, --password PASSWORD         Account password. If this option is left\n                                    out, yt-dlp will ask interactively\n    -2, --twofactor TWOFACTOR       Two-factor authentication code\n    -n, --netrc                     Use .netrc authentication data\n    --netrc-location PATH           Location of .netrc authentication data;\n                                    either the path or its containing directory.\n                                    Defaults to ~/.netrc\n    --video-password PASSWORD       Video password (vimeo, youku)\n    --ap-mso MSO                    Adobe Pass multiple-system operator (TV\n                                    provider) identifier, use --ap-list-mso for\n                                    a list of available MSOs\n    --ap-username USERNAME          Multiple-system operator account login\n    --ap-password PASSWORD          Multiple-system operator account password.\n                                    If this option is left out, yt-dlp will ask\n                                    interactively\n    --ap-list-mso                   List all supported multiple-system operators\n    --client-certificate CERTFILE   Path to client certificate file in PEM\n                                    format. May include the private key\n    --client-certificate-key KEYFILE\n                                    Path to private key file for client\n                                    certificate\n    --client-certificate-password PASSWORD\n                                    Password for client certificate private key,\n                                    if encrypted. If not provided, and the key\n                                    is encrypted, yt-dlp will ask interactively\n\n  Post-Processing Options:\n    -x, --extract-audio             Convert video files to audio-only files\n                                    (requires ffmpeg and ffprobe)\n    --audio-format FORMAT           Format to convert the audio to when -x is\n                                    used. (currently supported: best (default),\n                                    aac, alac, flac, m4a, mp3, opus, vorbis,\n                                    wav). You can specify multiple rules using\n                                    similar syntax as --remux-video\n    --audio-quality QUALITY         Specify ffmpeg audio quality to use when\n                                    converting the audio with -x. Insert a value\n                                    between 0 (best) and 10 (worst) for VBR or a\n                                    specific bitrate like 128K (default 5)\n    --remux-video FORMAT            Remux the video into another container if\n                                    necessary (currently supported: avi, flv,\n                                    mkv, mov, mp4, webm, aac, aiff, alac, flac,\n                                    m4a, mka, mp3, ogg, opus, vorbis, wav). If\n                                    target container does not support the\n                                    video/audio codec, remuxing will fail. You\n                                    can specify multiple rules; e.g.\n                                    "aac>m4a/mov>mp4/mkv" will remux aac to m4a,\n                                    mov to mp4 and anything else to mkv\n    --recode-video FORMAT           Re-encode the video into another format if\n                                    necessary. The syntax and supported formats\n                                    are the same as --remux-video\n    --postprocessor-args NAME:ARGS  Give these arguments to the postprocessors.\n                                    Specify the postprocessor/executable name\n                                    and the arguments separated by a colon ":"\n                                    to give the argument to the specified\n                                    postprocessor/executable. Supported PP are:\n                                    Merger, ModifyChapters, SplitChapters,\n                                    ExtractAudio, VideoRemuxer, VideoConvertor,\n                                    Metadata, EmbedSubtitle, EmbedThumbnail,\n                                    SubtitlesConvertor, ThumbnailsConvertor,\n                                    FixupStretched, FixupM4a, FixupM3u8,\n                                    FixupTimestamp and FixupDuration. The\n                                    supported executables are: AtomicParsley,\n                                    FFmpeg and FFprobe. You can also specify\n                                    "PP+EXE:ARGS" to give the arguments to the\n                                    specified executable only when being used by\n                                    the specified postprocessor. Additionally,\n                                    for ffmpeg/ffprobe, "_i"/"_o" can be\n                                    appended to the prefix optionally followed\n                                    by a number to pass the argument before the\n                                    specified input/output file, e.g. --ppa\n                                    "Merger+ffmpeg_i1:-v quiet". You can use\n                                    this option multiple times to give different\n                                    arguments to different postprocessors.\n                                    (Alias: --ppa)\n    -k, --keep-video                Keep the intermediate video file on disk\n                                    after post-processing\n    --no-keep-video                 Delete the intermediate video file after\n                                    post-processing (default)\n    --post-overwrites               Overwrite post-processed files (default)\n    --no-post-overwrites            Do not overwrite post-processed files\n    --embed-subs                    Embed subtitles in the video (only for mp4,\n                                    webm and mkv videos)\n    --no-embed-subs                 Do not embed subtitles (default)\n    --embed-thumbnail               Embed thumbnail in the video as cover art\n    --no-embed-thumbnail            Do not embed thumbnail (default)\n    --embed-metadata                Embed metadata to the video file. Also\n                                    embeds chapters/infojson if present unless\n                                    --no-embed-chapters/--no-embed-info-json are\n                                    used (Alias: --add-metadata)\n    --no-embed-metadata             Do not add metadata to file (default)\n                                    (Alias: --no-add-metadata)\n    --embed-chapters                Add chapter markers to the video file\n                                    (Alias: --add-chapters)\n    --no-embed-chapters             Do not add chapter markers (default) (Alias:\n                                    --no-add-chapters)\n    --embed-info-json               Embed the infojson as an attachment to\n                                    mkv/mka video files\n    --no-embed-info-json            Do not embed the infojson as an attachment\n                                    to the video file\n    --parse-metadata FROM:TO        Parse additional metadata like title/artist\n                                    from other fields; see "MODIFYING METADATA"\n                                    for details\n    --replace-in-metadata FIELDS REGEX REPLACE\n                                    Replace text in a metadata field using the\n                                    given regex. This option can be used\n                                    multiple times\n    --xattrs                        Write metadata to the video file's xattrs\n                                    (using dublin core and xdg standards)\n    --concat-playlist POLICY        Concatenate videos in a playlist. One of\n                                    "never", "always", or "multi_video"\n                                    (default; only when the videos form a single\n                                    show). All the video files must have same\n                                    codecs and number of streams to be\n                                    concatable. The "pl_video:" prefix can be\n                                    used with "--paths" and "--output" to set\n                                    the output filename for the concatenated\n                                    files. See "OUTPUT TEMPLATE" for details\n    --fixup POLICY                  Automatically correct known faults of the\n                                    file. One of never (do nothing), warn (only\n                                    emit a warning), detect_or_warn (the\n                                    default; fix file if we can, warn\n                                    otherwise), force (try fixing even if file\n                                    already exists)\n    --ffmpeg-location PATH          Location of the ffmpeg binary; either the\n                                    path to the binary or its containing\n                                    directory\n    --exec [WHEN:]CMD               Execute a command, optionally prefixed with\n                                    when to execute it (after_move if\n                                    unspecified), separated by a ":". Supported\n                                    values of "WHEN" are the same as that of\n                                    --use-postprocessor. Same syntax as the\n                                    output template can be used to pass any\n                                    field as arguments to the command. After\n                                    download, an additional field "filepath"\n                                    that contains the final path of the\n                                    downloaded file is also available, and if no\n                                    fields are passed, %(filepath)q is appended\n                                    to the end of the command. This option can\n                                    be used multiple times\n    --no-exec                       Remove any previously defined --exec\n    --convert-subs FORMAT           Convert the subtitles to another format\n                                    (currently supported: ass, lrc, srt, vtt)\n                                    (Alias: --convert-subtitles)\n    --convert-thumbnails FORMAT     Convert the thumbnails to another format\n                                    (currently supported: jpg, png, webp). You\n                                    can specify multiple rules using similar\n                                    syntax as --remux-video\n    --split-chapters                Split video into multiple files based on\n                                    internal chapters. The "chapter:" prefix can\n                                    be used with "--paths" and "--output" to set\n                                    the output filename for the split files. See\n                                    "OUTPUT TEMPLATE" for details\n    --no-split-chapters             Do not split video based on chapters\n                                    (default)\n    --remove-chapters REGEX         Remove chapters whose title matches the\n                                    given regular expression. The syntax is the\n                                    same as --download-sections. This option can\n                                    be used multiple times\n    --no-remove-chapters            Do not remove any chapters from the file\n                                    (default)\n    --force-keyframes-at-cuts       Force keyframes at cuts when\n                                    downloading/splitting/removing sections.\n                                    This is slow due to needing a re-encode, but\n                                    the resulting video may have fewer artifacts\n                                    around the cuts\n    --no-force-keyframes-at-cuts    Do not force keyframes around the chapters\n                                    when cutting/splitting (default)\n    --use-postprocessor NAME[:ARGS]\n                                    The (case sensitive) name of plugin\n                                    postprocessors to be enabled, and\n                                    (optionally) arguments to be passed to it,\n                                    separated by a colon ":". ARGS are a\n                                    semicolon ";" delimited list of NAME=VALUE.\n                                    The "when" argument determines when the\n                                    postprocessor is invoked. It can be one of\n                                    "pre_process" (after video extraction),\n                                    "after_filter" (after video passes filter),\n                                    "before_dl" (before each video download),\n                                    "post_process" (after each video download;\n                                    default), "after_move" (after moving video\n                                    file to it's final locations), "after_video"\n                                    (after downloading and processing all\n                                    formats of a video), or "playlist" (at end\n                                    of playlist). This option can be used\n                                    multiple times to add different\n                                    postprocessors\n\n  SponsorBlock Options:\n    Make chapter entries for, or remove various segments (sponsor,\n    introductions, etc.) from downloaded YouTube videos using the\n    SponsorBlock API (https://sponsor.ajay.app)\n\n    --sponsorblock-mark CATS        SponsorBlock categories to create chapters\n                                    for, separated by commas. Available\n                                    categories are sponsor, intro, outro,\n                                    selfpromo, preview, filler, interaction,\n                                    music_offtopic, poi_highlight, all and\n                                    default (=all). You can prefix the category\n                                    with a "-" to exclude it. See [1] for\n                                    description of the categories. E.g.\n                                    --sponsorblock-mark all,-preview [1] https:/\n                                    /wiki.sponsor.ajay.app/w/Segment_Categories\n    --sponsorblock-remove CATS      SponsorBlock categories to be removed from\n                                    the video file, separated by commas. If a\n                                    category is present in both mark and remove,\n                                    remove takes precedence. The syntax and\n                                    available categories are the same as for\n                                    --sponsorblock-mark except that "default"\n                                    refers to "all,-filler" and poi_highlight is\n                                    not available\n    --sponsorblock-chapter-title TEMPLATE\n                                    An output template for the title of the\n                                    SponsorBlock chapters created by\n                                    --sponsorblock-mark. The only available\n                                    fields are start_time, end_time, category,\n                                    categories, name, category_names. Defaults\n                                    to "[SponsorBlock]: %(category_names)l"\n    --no-sponsorblock               Disable both --sponsorblock-mark and\n                                    --sponsorblock-remove\n    --sponsorblock-api URL          SponsorBlock API location, defaults to\n                                    https://sponsor.ajay.app\n\n  Extractor Options:\n    --extractor-retries RETRIES     Number of retries for known extractor errors\n                                    (default is 3), or "infinite"\n    --allow-dynamic-mpd             Process dynamic DASH manifests (default)\n                                    (Alias: --no-ignore-dynamic-mpd)\n    --ignore-dynamic-mpd            Do not process dynamic DASH manifests\n                                    (Alias: --no-allow-dynamic-mpd)\n    --hls-split-discontinuity       Split HLS playlists to different formats at\n                                    discontinuities such as ad breaks\n    --no-hls-split-discontinuity    Do not split HLS playlists to different\n                                    formats at discontinuities such as ad breaks\n                                    (default)\n    --extractor-args KEY:ARGS       Pass these arguments to the extractor. See\n                                    "EXTRACTOR ARGUMENTS" for details. You can\n                                    use this option multiple times to give\n                                    arguments for different extractors\n\nSee full documentation at  https://github.com/yt-dlp/yt-dlp#readme'''+"\n"
        self.consolelog.cursor = (0,0)
        Clock.schedule_once(lambda dt: setattr(self.consolelog, 'cursor', (0, 0)),.5)
        self.playeropen = False
        self.lastpos = 0
        self.playerposlock = False
        self.config = ConfigParser()
        self.url = None
        Window.bind(on_keyboard=self._on_keyboard)
        self.unlock_trigger = Clock.create_trigger(lambda dt: setattr(self,'playerposlock', False),.3)
        self.layout.add_widget(self.url_input)
        self.layout.add_widget(self.download_button)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.consolelog)
        self.layout.add_widget(self.prlabel)
        return self.layout
    def open_settings(self, instance):
        settings_panel = CustomSettings()  # Create an instance of your custom settings panel
        settings_panel.bind(on_close=lambda dt: (settings_panel.config.write(),self.layout.remove_widget(settings_panel)))
        self.layout.add_widget(settings_panel)
    def video(self, instance):
        # Create a FileChooserListView widget
        self.file_chooser = FileChooserListView()

        # Set the path to the user's home directory as the initial path
        self.file_chooser.path = os.curdir

        # Filter video files based on extensions
        self.file_chooser.filters = [lambda folder, filename: filename.endswith((".mp4", ".avi", ".mkv", ".mov",".webm",".mp3",".wav",".ogg"))]
        self.popup = Popup(title='Open',
                           content=self.file_chooser,
                           size_hint=(None, None), size=(700, 500))
        if self.theme == "Light":
            self.popup.background = ""
            self.popup.background_color = (.3,.3,.3,1)
        self.popup.open()
        # Bind the on_selection event to a callback function
        self.file_chooser.bind(on_submit=self.openvideo)

        # # Add the FileChooser to the layout
        # self.add_widget(self.file_chooser)
    def detailspanel(self,instance):
        if self.dta.text == ">":
            self.dta.text = "<"
            Window.size = (1200,600)
            self.floa.size_hint = (.4, 1)
            self.floa.add_widget(self.dta_title)
            self.floa.add_widget(self.dta_desc)
            self.dta.size_hint=(.15, .1)
            self.dta.pos_hint={'right': .15, 'top': .5}
            # Window._set_size([1200,600])
        elif self.dta.text == "<":
            self.dta.text = ">"
            Window.size = (900,600)
            self.floa.size_hint = (.08, 1)
            self.floa.remove_widget(self.dta_title)
            self.floa.remove_widget(self.dta_desc)
            self.dta.size_hint=(.75, .1)
            self.dta.pos_hint={'right': .75, 'top': .5}
            # self.popup._align_center()
    def openvideo(self, chooser, selection, *args):
        self.playeropen = True
        title = "No video name"
        url = "No URL"
        channel = "No channel"
        date = "20000101"
        desc = "No description"
        # create the path to the corresponding info JSON file
        try:
            base_name = os.path.splitext(selection[0])[0]
            json_file_path = f"{base_name}.info.json"

            # now json_file_path contains the path to the info JSON file
            print(json_file_path)
            # open and read the JSON file
            with open(json_file_path, "r", encoding="utf8") as json_file:
                video_details = json.load(json_file)

            # now, you can access the video details like this:
            print(video_details["channel"])
            title = video_details["title"]
            url = video_details["webpage_url"]
            channel = video_details["uploader"]
            date = video_details["upload_date"]
            desc = video_details["description"]
        except FileNotFoundError:
            print("Could not get details")
        desc_f = '\n'.join([line[0:] if i == 0 else line[22:] for i, line in enumerate(desc.split('\n'))])
        box = BoxLayout()
        self.floa = FloatLayout(size_hint=(.08, 1))
        self.dta = CustomButton(size_hint=(.75, .1),pos_hint={'right': .75, 'top': .5},text=">",on_release=self.detailspanel)
        self.dta_title = WrappedLabel(size_hint=(.9, .1),pos_hint={'right': .9, 'top': .95},text=title,bold=True)
        # print(desc_f)
        self.dta_desc = TextInput(size_hint=(.9, .3),pos_hint={'right': .9, 'top': .85},text=desc)
        self.floa.add_widget(self.dta)
        self.player = VideoPlayer(source=selection[0], state='pause',
                                  options={'fit_mode': 'contain','eos':'stop'},allow_fullscreen=False,size_hint=(.9,1))
        self.popup.dismiss()
        box.add_widget(self.player)
        self.config.read('ytdlp_settings.ini')
        if self.config.getboolean('app', 'vinfo'):
            box.add_widget(self.floa)
        self.popup = CustomPopup(title='Multimedia Player',content=box,
                           size_hint=(.9, .8), size=(0, 0))
        if self.theme == "Light":
            self.popup.background = ""
            self.popup.background_color = (.3,.3,.3,1)
        self.popup.open()
        # popup.open()
        self.popup.bind(on_dismiss=lambda dt: (setattr(self.player,"state",'stop'),setattr(self,"playeropen",False),self.popup._real_remove_widget()))
        # self.player.bind(state=self._set_state)
        # self.player.bind(on_touch_move=self.on_seek)
        self.config = ConfigParser()
        self.config.read('ytdlp_settings.ini')
        self.tupdelay = round(self.config.getint('media','titleint'))
        # if self.tupdelay < 0:
        #     self
        self.player.bind(position=self.on_position_change)
    def on_position_change(self, instance, value):
        # print("Position changed:", value)
        if self.playeropen and not self.playerposlock:
            if self.tupdelay==0 or Clock.frames%self.tupdelay==0:
                self.popup.title=f"Multimedia Player ({round(value*60)}/{timedelta(seconds=(round(value)))})"
            self.lastpos = value
        else:
            self.popup.title=f"Multimedia Player ({round(self.lastpos*60)}/{timedelta(seconds=(round(self.lastpos)))})"
    # def _set_state(self, instance, value):
    #     # print(value)
    #     if value=="stop"or value=="pause":
    #         # self.lastpos = self.player.position
    #         pass
    #the first time you unpause, the video restarts
    # def on_seek(self, instance, touch):
    #     if instance.state == 'play' and instance. .collide_point(*touch.pos):
    #         # Check if the player is in play state and the touch is within the progress bar
    #         print("Player is seeking through the progress bar")
    def _on_keyboard(self,instance, key, scancode, codepoint, modifiers):
        # print(key)
        self.playerposlock = True
        if self.playeropen and key==46:
            # print("H")
            frame_rate = 60  # Frames per second
            # Assuming you have self.player.duration defined
            frame_duration = 1 / frame_rate  # Duration of one frame in seconds

            # Calculate the percentage for seeking one frame forward
            seek_percent = frame_duration / self.player.duration
            self.lastpos = round(self.lastpos*60)/60
            self.lastpos += frame_duration
            # Perform the seek operation with the calculated percentage
            self.player.seek((self.lastpos / self.player.duration))
        if self.playeropen and key==44:
            # print("H")
            frame_rate = 60  # Frames per second
            # Assuming you have self.player.duration defined
            frame_duration = 1 / frame_rate  # Duration of one frame in seconds

            # Calculate the percentage for seeking one frame forward
            seek_percent = frame_duration / self.player.duration
            self.lastpos = round(self.lastpos*60)/60
            self.lastpos -= frame_duration
            # Perform the seek operation with the calculated percentage
            self.player.seek((self.lastpos / self.player.duration))
        if self.playeropen and key==276:
            # print("H")
            frame_rate = 60  # Frames per second
            # Assuming you have self.player.duration defined
            frame_duration = 1 / frame_rate  # Duration of one frame in seconds

            # Calculate the percentage for seeking one frame forward
            seek_percent = frame_duration / self.player.duration
            self.lastpos -= frame_duration*(frame_rate*5)
            # Perform the seek operation with the calculated percentage
            self.player.seek((self.lastpos / self.player.duration))
        if self.playeropen and key==275:
            # print("H")
            frame_rate = 60  # Frames per second
            # Assuming you have self.player.duration defined
            frame_duration = 1 / frame_rate  # Duration of one frame in seconds

            # Calculate the percentage for seeking one frame forward
            seek_percent = frame_duration / self.player.duration
            self.lastpos += frame_duration*(frame_rate*5)
            # Perform the seek operation with the calculated percentage
            self.player.seek((self.lastpos / self.player.duration))
        if self.playeropen and key==32:
            # print("H")
            if self.player.state=="play":
                self.player.state="pause"
            else:
                self.player.state="play"
        if self.playeropen and self.player.state=="pause":
            self.popup.title=f"Multimedia Player ({round(self.lastpos*60)}/{timedelta(seconds=(round(self.lastpos)))})"
            if self.unlock_trigger.is_triggered:
                self.unlock_trigger.cancel()
            self.unlock_trigger()
        # print(self.lastpos)
    # def setup_logger(self):
    #     log_handler = self.LogHandler(self.consolelog)
    #     ydl_logger = logging.getLogger('yt_dlp')
    #     ydl_logger.addHandler(log_handler)
    #     ydl_logger.setLevel(logging.DEBUG)
    # def build(self):
    #     sm = ScreenManager()
    #     sm.add_widget(MainScreen(name='main'))
    #     sm.add_widget(SecondScreen(name='second'))
    #     return sm

    def download(self,instance=None,dltime=None):
        Animation(value=0,duration=.36).start(self.progress_bar)
        text_input = self.url_input # Access the TextInput widget by its ID
        url = text_input.text
        if self.url != None:
            url = self.url
            self.url = None
        if (url=='ffm'):
            os.system("static_ffmpeg -version")
            os.system("static_ffprobe -version")
            self.addtolog('Installing/Installed ffmpeg and ffprobe')
            return None
        if (url==''):
            self.addtolog('Don\'t try fooling me like that. At least provide a URL!')
            return None
        print("Now downloading ", url)
        self.consolelog.text=''
        ffmpeg, ffprobe = run.get_or_fetch_platform_executables_else_raise()
        # print(ffmpeg)
        # print(ffprobe)
        def dlthread():
            self.config.read('ytdlp_settings.ini')
            extension = self.config.get('format','videof')
            if extension.startswith("List formats"):
                extension = "List formats"
            ydl_opts = {
                'logger': self.LogHandler(self.consolelog, url),
                'progress_hooks': [self.progress_hook],
                'writesubtitles': self.config.getboolean('general', 'subtitle'),
                'getcomments': self.config.getboolean('arc', 'dlcom'),
                'writeinfojson': self.config.getboolean('arc', 'ijson'),
                # 'embed_thumbnail':config.getboolean('general', 'embed_thmb'),
                'format':f'bestvideo[ext={extension}][height<={self.config.getint("format","hei")}][filesize<{self.config.get("format","maxsize")}]+bestaudio',
                # 'sponsorblock_remove':'sponsor',
                'postprocessors': [
                    {
                        'key': 'FFmpegMetadata',
                        'add_metadata': True,
                    },
                    #     'key': 'EmbedThumbnail',
                    #     'already_have_thumbnail':
                    # }
                ],
                # 'quiet':True,
            }
            if self.config.getboolean('general', 'ffm'):
                ydl_opts['ffmpeg_location'] = ffmpeg
            if self.config.getboolean('general', 'embed_thmb'):
                ydl_opts['postprocessors'].append({
                    'key': 'EmbedThumbnail',
                })
            if self.config.getboolean('general', 'subtitle'):
                ydl_opts['postprocessors'].append({'key': 'FFmpegEmbedSubtitle', 'already_have_subtitle': False})
            if ((self.config.get('format', 'videof')== "List formats/Use format ID")and(self.config.get('format', 'videofid')!= "")):
                ydl_opts['format'] = self.config.get('format', 'videofid')
            if ((self.config.get('logins', 'browserc')== "None/Custom")and(self.config.get('logins', 'browsercc')!= "")):
                ydl_opts['cookiesfrombrowser'] = [self.config.get('logins', 'browsercc')]
            if self.config.get('logins', 'browserc')!= "None/Custom":
                ydl_opts['cookiesfrombrowser'] = [self.config.get('logins', 'browserc')]
            if dltime is not None:
                print(dltime[0],dltime[1])
                ydl_opts['download_ranges'] = yt_dlp.download_range_func(None,[(dltime[0],dltime[1])])
                ydl_opts['force_keyframes_at_cuts'] = True
            # print(self.config.get('logins', 'browserc'))
            # ydl_opts = {
            #     'writesubtitles': 'true',
            #     'subtitleslangs': 'en',
            #     'merge_output_format': 'mkv',
            #     'writethumbnail': 'true',
            #     'postprocessors': [
            #         {
            #             'key': 'FFmpegMetadata',
            #             'add_metadata': True,
            #         }, {
            #             'key': 'EmbedThumbnail',
            #             'already_have_thumbnail': False,
            #         }
            #     ],
            # }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    info_dict = yt_dlp.YoutubeDL().extract_info(url, download=False)
                    if info_dict:
                        print("The URL is valid ", url)
                        ydl.download([url])
                    else:
                        print("Invalid URL ", url)
                        return False
                except Exception as e:
                    print("Invalid URL ", url)
                    self.config.read('ytdlp_settings.ini')
                    if self.config.getboolean('debug','stt'):
                        self.addtolog(f"Ugh, you got me!! lemme show you:\n{traceback.format_exc()}")
                    else:
                        self.addtolog("An error occured but stacktraces are off. For debugging purposes, it is recommended to enable it")
                    return False
        threading.Thread(target=dlthread).start()

    # ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
    @mainthread
    def progress_hook(self, d):
        # self.addtolog('h')
        # app.stopTouchApp()
        if d['status'] == 'downloading':
            # progress_text = f"Downloading {d['filename']}: {d['_percent_str']} complete\n"
            # self.addtolog(progress_text)
            Animation(value=int(round(float(d['_percent_str'].rstrip("%")))),duration=.36).start(self.progress_bar)
            self.prlabel.text = d['_percent_str']+" complete"
        elif d['status'] == 'finished' and d['info_dict']["__real_download"]:#I figured this out the hard way
            completed_text = f"The download of \"{d['filename']}\" has been completed\n"
            self.addtolog(completed_text)
            # if self.config.getboolean('format','gz'):
            #     self.addtolog('Compressing with GZIP..')
            #     with open(d['filename'], 'rb') as f_in:
            #         with gzip.open(d['filename']+'.gz', 'wb') as f_out:
            #             shutil.copyfileobj(f_in, f_out)
            #     self.addtolog('Compressed to GZIP, removing original..')
            #     os.remove(d['filename'])
            #     self.addtolog('Compressed to GZIP and removed original file')
    class LogHandler(logging.Handler):
        def __init__(self, label,url):
            super().__init__()
            self.label = label
            self.url = url
        @mainthread
        def emit(self, record):
            msg = self.format(record)
            self.label.text += f"{msg}\n"
        @mainthread
        def debug(self, msg):
            # For compatibility with youtube-dl, both debug and info are passed into debug
            # You can distinguish them by the prefix '[debug] '
            if msg.startswith('[debug] '):
                pass
            else:
                # if msg.startswith("[Metadata] "):
                #     thread = threading.Thread(target=self.process_metadata_with_delay, args=(msg,))
                #     thread.start()
                self.label.text += f"{msg}\n"
        @mainthread
        def info(self, msg):
            self.label.text += f"{msg}\n"
        @mainthread
        def warning(self, msg):
            self.label.text += f"{msg}\n"
        @mainthread
        def error(self, msg):
            self.label.text += f"{msg}\n"
            print("For the bois that are looking at the log: " + msg)
            if "--list-formats" in msg:
                self.label.text += "Oh wait we could list the formats!\n"

                # Assume self.url is defined and contains the video URL
                with yt_dlp.YoutubeDL() as ydl:
                    info_dict = ydl.extract_info(self.url, download=False)
                    if 'formats' in info_dict:
                        self.label.text += "Available formats:\n"
                    for format in info_dict['formats']:
                        format_id = format['format_id']
                        ext = format['ext']
                        resolution = format.get('resolution', 'N/A')

                        fps = format.get('fps')
                        if isinstance(fps, (float, int)):
                            if (isinstance(fps, int)|(str(f"{fps:.3f}")).endswith("000")):
                                fps = int(fps)
                            else:
                                fps = f"{fps:.3f}"
                        else:
                            fps = "0"

                        self.label.text += f"ID: {format_id}, EXT: {ext}, RESOLUTION: {resolution}, FPS: {fps}\n"
            Clock.schedule_once(lambda dt: setattr(self.label, 'cursor', (0, 0)),.2)
        # def process_metadata_with_delay(self,line):
        #     time.sleep(1)  # Introducing a 1-second delay
        #     def process_metadata_line(line2):
        #         metadata_text = line2[len("[Metadata] Adding metadata to "):]
        #         return metadata_text.strip('"')
        #     @mainthread
        #     def add(text):
        #         self.label.text+=text
        #     metadata = process_metadata_line(line)
        #     if metadata:
        #         # print(metadata)
        #         if self.gz:
        #             add('Compressing with GZIP..\n')
        #             with open(metadata, 'rb') as f_in:
        #                 with gzip.open(metadata+'.gz', 'wb') as f_out:
        #                     shutil.copyfileobj(f_in, f_out)
        #             add('Compressed to GZIP, removing original..\n')
        #             os.remove(metadata)
        #             add(f'Compressed to GZIP and removed original file {metadata}\n')
        #         return metadata
    @mainthread
    def addtolog(self,msg):
        self.consolelog.text += f"{msg}\n"

class CustomSettings(SettingsWithSidebar):
    def __init__(self, **kwargs):
        super(CustomSettings, self).__init__(**kwargs)
        self.config = ConfigParser()
        self.config.read('ytdlp_settings.ini')  # Specify the correct file path
        self.config.setdefaults('general', {
            'embed_thmb':False,'subtitle':True,'ffm':False})
        self.config.setdefaults('format',{'videof':"mp4",'videofid':"",'hei':1080,'maxsize':"1000M"})
        self.config.setdefaults('arc',{"dlcom":False,"ijson":True})
        self.config.setdefaults('media',{'titleint':8})
        self.config.setdefaults('logins',{'browserc':"None/Custom",'browsercc':""})
        self.config.setdefaults('app',{'mode':"Dark",'vinfo':True})
        self.config.setdefaults('debug',{'stt':True})
        self.add_json_panel('General', self.config, data="""[
          {
            "type": "bool",
            "title": "Embed Thumbnail",
            "desc": "Adds the thumbnail. Note this may force the video to be in .mkv",
            "section": "general",
            "key": "embed_thmb"
          },
          {
            "type": "bool",
            "title": "Embed Subtitles",
            "desc": "Embeds subtitles into the video",
            "section": "general",
            "key": "subtitle"
          },
          {
            "type": "bool",
            "title": "Use FFmpeg",
            "desc": "Enables use of FFmpeg and FFprobe in yt-dlp. Download ffm to get the required binaries",
            "section": "general",
            "key": "ffm"
          },
          {
            "type": "options",
            "title": "Video Format",
            "desc": "The file type of the video",
            "section": "format",
            "key": "videof",
            "options": ["avi", "flv", "mkv", "mov", "mp4", "webm", "List formats/Use format ID"]
          },
          {
            "type": "string",
            "title": "Video Format ID",
            "desc": "The specific format ID of the video from the List formats option. I won't blame you if you pick 3gp",
            "section": "format",
            "key": "videofid"
          },
          {
            "type": "numeric",
            "title": "Output height",
            "desc": "The height of the video (1920x<1080>)",
            "section": "format",
            "key": "hei"
          },
          {
            "type": "string",
            "title": "Max filesize",
            "desc": "The maximum file size ending with M (MB) or k (KB)",
            "section": "format",
            "key": "maxsize"
          }
        ]""")
        self.add_json_panel('Archival', self.config, data="""[
          {
            "type": "bool",
            "title": "Download comments",
            "desc": "Downloads all the comments for the most archival! This requires the info JSON",
            "section": "arc",
            "key": "dlcom"
          },
          {
            "type": "bool",
            "title": "Download info JSON",
            "desc": "This is highly recommended. This saves all the video info into a JSON for faster player loading. Be sure to include it in archives",
            "section": "arc",
            "key": "ijson"
          }
        ]""")
        self.add_json_panel('Multimedia', self.config, data="""[
          {
            "type": "numeric",
            "title": "Title Update Interval",
            "desc": "How long in frames it takes for the title to update. -1 disables the feature",
            "section": "media",
            "key": "titleint"
          }
        ]""")
        self.add_json_panel('Logins', self.config, data="""[
          {
            "type": "options",
            "title": "Browser Cookies",
            "desc": "Selecting a browser can get the video based on your cookies, useful for age-locked or sign-in only stuff. Won't work for Chromium browsers if open",
            "section": "logins",
            "key": "browserc",
            "options": ["chrome", "chromium", "brave", "firefox", "opera", "vivaldi", "None/Custom"]
          },
          {
            "type": "string",
            "title": "Browser Cookies path",
            "desc": "In case you don't have any of the browsers above. Chromium-based browsers are on /User Data, Firefox on /Profiles",
            "section": "logins",
            "key": "browsercc"
          }
        ]""")
        self.add_json_panel('Appearance', self.config, data="""[
          {
            "type": "options",
            "title": "Theme",
            "desc": "Choose dark (default) or light theme, needs a restart",
            "section": "app",
            "key": "mode",
            "options": ["Dark","Light"]
          },
          {
            "type": "bool",
            "title": "Show Video Details button",
            "desc": "If the multimedia player's details button is visible",
            "section": "app",
            "key": "vinfo"
          }
        ]""")
        self.add_json_panel('Debug', self.config, data="""[
          {
            "type": "bool",
            "title": "Error stacktraces",
            "desc": "If enabled, stacktraces will appear when an error occurs",
            "section": "debug",
            "key": "stt"
          }
        ]""")
# class MainScreen(Screen):
#     pass
# class SecondScreen(Screen):
#     pass
if __name__ == '__main__':
    ytdlpgui().run()
    # runTouchApp()
