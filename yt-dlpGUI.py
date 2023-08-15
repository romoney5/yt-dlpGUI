import logging
import random
import threading
import time
import traceback

import yt_dlp.utils
from kivy import Config, app
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from yt_dlp import YoutubeDL
Window.clearcolor = (0.05, 0.05, 0.07, 1)
Window.size = (900,600)
Config.set('kivy','exit_on_escape',0)
class ytdlpgui(App):
    def build(self):
        layout = FloatLayout()

        # Navigation Bar
        nav_bar = FloatLayout()
        nav_button1 = Button(text='Home', pos_hint={'right': 0.5, 'top': .98}, size_hint=(.48, .05))
        nav_button2 = Button(text='Settings', pos_hint={'right': .98, 'top': .98}, size_hint=(.48, .05))
        nav_bar.add_widget(nav_button1)
        nav_bar.add_widget(nav_button2)
        # nav_bar.add_widget(Widget())
        layout.add_widget(nav_bar)

        self.url_input = TextInput(hint_text='URL/Arguments', pos=(10, 70), size_hint=(.4, .05))
        download_button = Button(text='Download video', on_release=self.download, pos=(10, 20), size_hint=(.4, .08))
        self.progress_bar = ProgressBar(max=100, value=0, pos=(10, 0), size_hint=(1, .05))
        self.consolelog = TextInput(size_hint=(.8, .74), pos_hint={'right': .98, 'top': .92})
        self.prlabel = Label(size_hint=(.4, .08), pos_hint={'right': .82, 'top': .12},text="0% complete",halign='left',font_size=34-6)
        self.prlabel.bind(size=self.prlabel.setter('text_size'))
        # time.sleep(0.1)
        self.consolelog.text = open("help.txt", "r").read()+"\n"
        self.consolelog.cursor = (0,0)
        Clock.schedule_once(lambda dt: setattr(self.consolelog, 'cursor', (0, 0)),.5)
        # print("It happens")
        # help(YoutubeDL)
        # self.setup_logger()

        layout.add_widget(self.url_input)
        layout.add_widget(download_button)
        layout.add_widget(self.progress_bar)
        layout.add_widget(self.consolelog)
        layout.add_widget(self.prlabel)

        return layout
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
        if (url==''):
            self.addtolog('Don\'t try fooling me like that. At least provide a URL!')
            return None
        print("Now downloading ", url)
        self.consolelog.text=''
        def dlthread():
            ydl_opts = {
                'logger': self.LogHandler(self.consolelog),
                'progress_hooks': [self.progress_hook],
                # 'quiet':True,
            }
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
                    self.addtolog(f"Ugh you got me!! lemme show you:\n{traceback.format_exc()}")
                    return False
        threading.Thread(target=dlthread).start()

# ℹ️ See "progress_hooks" in help(yt_dlp.YoutubeDL)
    @mainthread
    def progress_hook(self, d):
        # app.stopTouchApp()
        if d['status'] == 'downloading':
            # progress_text = f"Downloading {d['filename']}: {d['_percent_str']} complete\n"
            # self.addtolog(progress_text)
            Animation(value=int(round(float(d['_percent_str'].rstrip("%")))),duration=.36).start(self.progress_bar)
            self.prlabel.text = d['percent_str']+" complete"
        elif d['status'] == 'finished':
            completed_text = f"The download of \"{d['filename']}\" has been completed\n"
            self.addtolog(completed_text)
    class LogHandler(logging.Handler):
        def __init__(self, label):
            super().__init__()
            self.label = label
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
            print("For the bois that are looking at the log: "+msg)
            Clock.schedule_once(lambda dt: setattr(self.label, 'cursor', (0, 0)),.2)
    @mainthread
    def addtolog(self,msg):
        self.consolelog.text += f"{msg}\n"
# class MainScreen(Screen):
#     pass
# class SecondScreen(Screen):
#     pass
if __name__ == '__main__':
    ytdlpgui().run()