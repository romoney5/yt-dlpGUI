# import gzip
# import shutil
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
    if (e.msg=="No module named 'yt_dlp'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
    if (e.msg=="No module named 'kivy'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kivy"])
    if (e.msg=="No module named 'static_ffmpeg'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "static-ffmpeg"])
    if (e.msg=="No module named 'ffpyplayer'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ffpyplayer"])
    if (e.msg=="No module named 'kivy_gradient'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "kivygradient"])
    if (e.msg=="No module named 'pyautogui'"):
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyautogui"])
    # messagebox.showerror("yt-dlpGUI",e.msg)
    print(f"Restarting!")
    messagebox.showinfo("yt-dlpGUI","Restarting!")
    os.execv(sys.executable, ['python'] + sys.argv)
if sys.platform=="win32":
    import ctypes
    ctypes.windll.user32.ShowWindow( ctypes.windll.kernel32.GetConsoleWindow(), 0 )

Window.clearcolor = (0.06, 0.06, 0.08, 1)
Window.size = (900,600)
Config.set('kivy','exit_on_escape',0)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
class CustomButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color=(0, 0, 0, 0)
        self.font_name="segoe"
        self.col_def = [88 / 255, 88 / 255, 88 / 255, 1]
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
                button2 = CustomButton(text='Download from Clipboard', pos_hint={'right': .88, 'top': .83}, size_hint=(.76, .1), on_release=self.app.dlcl)
                button2.bind(on_release=popup.dismiss)
                button3 = CustomButton(text='Download from Browser Tab', pos_hint={'right': .88, 'top': .68}, size_hint=(.76, .1), on_release=self.app.dlbr)
                button3.bind(on_release=popup.dismiss)
                fl.add_widget(button1)
                fl.add_widget(button2)
                fl.add_widget(button3)
                fl.add_widget(Label(size_hint=(.1, .08), pos_hint={'right': .08, 'top': .08},text="Ver. a2.0.0",halign='left',font_size=10,font_name="segoe"))
                popup.open()
            return True
        super().on_touch_down(touch)
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

    def build(self):
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
        LabelBase.register(name="segoe", fn_regular="segoeui.ttf")
        self.url_input = TextInput(hint_text='URL/Arguments', pos=(10, 70), size_hint=(.4, .05),multiline=False,font_name="segoe")
        self.download_button = CustomButton(text='Download video', on_release=self.download, pos=(10, 20), size_hint=(.4, .08))
        ytdlpgui.download_button = self.download_button
        self.progress_bar = ProgressBar(max=100, value=0, pos=(10, 0), size_hint=(.975, .05))
        self.consolelog = TextInput(size_hint=(.8, .74), pos_hint={'right': .98, 'top': .92},background_color=(0.1, 0.1, 0.16, 1),foreground_color=(1, 1, 1, 1),font_name="segoe")
        self.prlabel = Label(size_hint=(.4, .08), pos_hint={'right': .82, 'top': .12},text="0% complete",halign='left',font_size=34-6,font_name="segoe")
        self.prlabel.bind(size=self.prlabel.setter('text_size'))
        # time.sleep(0.1)
        self.consolelog.text = open("help.txt", "r").read()+"\n"
        self.consolelog.cursor = (0,0)
        Clock.schedule_once(lambda dt: setattr(self.consolelog, 'cursor', (0, 0)),.5)
        # print("It happens")
        # help(YoutubeDL)
        # self.setup_logger()
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
        self.popup.open()
        # Bind the on_selection event to a callback function
        self.file_chooser.bind(on_submit=self.openvideo)

        # # Add the FileChooser to the layout
        # self.add_widget(self.file_chooser)

    def openvideo(self, chooser, selection, *args):
        self.playeropen = True
        floa = FloatLayout()
        box = BoxLayout()
        self.player = VideoPlayer(source=selection[0], state='pause',
                                  options={'fit_mode': 'contain','eos':'stop'},allow_fullscreen=False,size_hint=(.9, .8))
        self.popup.dismiss()
        box.add_widget(floa)
        box.add_widget(self.player)
        self.popup = Popup(title='Multimedia Player',content=box,
                           size_hint=(.9, .8), size=(0, 0))
        self.popup.open()
        # popup.open()
        self.popup.bind(on_dismiss=lambda dt: (setattr(self.player,"state",'stop'),setattr(self,"playeropen",False),self.popup._real_remove_widget()))
        try:
            o = subprocess.check_output(["static_ffprobe", selection[0]], stderr=subprocess.STDOUT, shell=True, text=True)
            print(o)
            # Define a pattern to match metadata lines
            metadata_pattern = re.compile(r'\s+(\w+)\s+: (.+?)(?=\n\s+\w+\s+:|\Z)', re.DOTALL)

            # Create a dictionary to store metadata
            metadata = {}

            # Extract metadata using regular expression
            for match in metadata_pattern.finditer(o):
                key = match.group(1)
                value = match.group(2)
                if key not in metadata:
                    metadata[key] = value.strip()
            title = "No video name"
            url = "No URL"
            channel = "No channel"
            date = "20000101"
            desc = "No description"
            # Print extracted metadata
            for key, value in metadata.items():
                key = str.upper(key)
                if key == "TITLE":
                    title = value
                if key == "PURL":
                    url = value
                if key == "ARTIST":
                    channel = value
                if key == "DATE":
                    date = value
                if key == "DESCRIPTION":
                    desc = value
                # print(key, ":", value)
                # self.addtolog(key+","+value)
            self.addtolog(title)
            self.addtolog(url)
            self.addtolog(channel)
            self.addtolog(datetime.strptime(date, "%Y%m%d").strftime("%b %d, %Y"))
            self.addtolog('\n'.join([line[0:] if i == 0 else line[22:] for i, line in enumerate(desc.split('\n'))]))
            # print('\n'.join([line.strip()[2:] for line in desc.split('\n') if line.strip()]))
        except Exception as e:
            self.addtolog("Could not decode video metadata")
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

    def download(self,instance=None):
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
        print(ffmpeg)
        print(ffprobe)
        def dlthread():
            self.config.read('ytdlp_settings.ini')
            extension = self.config.get('format','videof')
            if extension.startswith("List formats"):
                extension = "List formats"
            ydl_opts = {
                'logger': self.LogHandler(self.consolelog, url),
                'progress_hooks': [self.progress_hook],
                'writesubtitles': self.config.getboolean('general', 'subtitle'),
                'getcomments': self.config.getboolean('format', 'dlcom'),
                'writeinfojson': self.config.getboolean('format', 'dlcom'),
                # 'embed_thumbnail':config.getboolean('general', 'embed_thmb'),
                'format':f'bestvideo[ext={extension}][height<={self.config.getint("format","hei")}][filesize<{self.config.get("format","maxsize")}]+bestaudio',
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
                    info_dict = ydl.extract_info(url, download=False)
                    if info_dict:
                        print("The URL is valid ", url)
                        ydl.download([url])
                    else:
                        print("Invalid URL ", url)
                        return False
                except Exception as e:
                    print("Invalid URL ", url)
                    self.addtolog(f"Ugh, you got me!! lemme show you:\n{traceback.format_exc()}")
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
        self.config.setdefaults('format',{'videof':"mp4",'videofid':"",'hei':1080,'maxsize':"1000M","dlcom":False})
        self.config.setdefaults('media',{'titleint':8})
        self.config.setdefaults('logins',{'browserc':"None/Custom",'browsercc':""})
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
            "desc": "The maximum file size ending with M (MB) or K (KB)",
            "section": "format",
            "key": "maxsize"
          },
          {
            "type": "bool",
            "title": "Download comments",
            "desc": "Downloads all the comments for the most archival!",
            "section": "format",
            "key": "dlcom"
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
            "desc": "Selecting a browser can get the video based on your cookies, useful for age-locked or sign-in only stuff",
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
# class MainScreen(Screen):
#     pass
# class SecondScreen(Screen):
#     pass
if __name__ == '__main__':
    ytdlpgui().run()
    # runTouchApp()