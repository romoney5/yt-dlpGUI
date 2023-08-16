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
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.settings import SettingsWithSpinner, Settings, SettingsWithSidebar
# from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
# from kivy.uix.widget import Widget
# from yt_dlp import YoutubeDL
Window.clearcolor = (0.05, 0.05, 0.07, 1)
Window.size = (900,600)
Config.set('kivy','exit_on_escape',0)
class ytdlpgui(App):
    def update_please(self,instance):
        # Download the file from the URL
        response = requests.get("https://github.com/romoney5/yt-dlpGUI/raw/master/yt-dlpGUI.py")
        if response.status_code == 200:
            with open("yt-dlpGUI.py", 'wb') as file:
                file.write(response.content)
            print(f"Downloaded a yt-dlpGUI update successfully")

            # Close the current script
            app.stopTouchApp()
        else:
            print("Failed to download the file")

    def build(self):
        self.layout = FloatLayout()
        # Navigation Bar
        nav_bar = FloatLayout()
        nav_button1 = Button(text='Update', pos_hint={'right': 0.5, 'top': .98}, size_hint=(.48, .05),on_release=self.update_please)
        nav_button2 = Button(text='Settings', pos_hint={'right': .98, 'top': .98}, size_hint=(.48, .05),on_release=self.open_settings)
        nav_bar.add_widget(nav_button1)
        nav_bar.add_widget(nav_button2)
        # nav_bar.add_widget(Widget())
        self.layout.add_widget(nav_bar)

        self.url_input = TextInput(hint_text='URL/Arguments', pos=(10, 70), size_hint=(.4, .05))
        download_button = Button(text='Download video', on_release=self.download, pos=(10, 20), size_hint=(.4, .08))
        self.progress_bar = ProgressBar(max=100, value=0, pos=(10, 0), size_hint=(.975, .05))
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

        self.layout.add_widget(self.url_input)
        self.layout.add_widget(download_button)
        self.layout.add_widget(self.progress_bar)
        self.layout.add_widget(self.consolelog)
        self.layout.add_widget(self.prlabel)
        return self.layout
    def open_settings(self, instance):
        settings_panel = CustomSettings()  # Create an instance of your custom settings panel
        settings_panel.bind(on_close=lambda dt: self.layout.remove_widget(settings_panel))
        self.layout.add_widget(settings_panel)
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
                    self.addtolog(f"Ugh, you got me!! lemme show you:\n{traceback.format_exc()}")
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
            self.prlabel.text = d['_percent_str']+" complete"
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
class CustomSettings(SettingsWithSidebar):
    def __init__(self, **kwargs):
        super(CustomSettings, self).__init__(**kwargs)
        self.config = ConfigParser()
        self.config.setdefaults('general', {
            'embed_thmb':False,'age':0})
        self.add_json_panel('General', self.config, 'custom_settings.json')
# class MainScreen(Screen):
#     pass
# class SecondScreen(Screen):
#     pass
if __name__ == '__main__':
    ytdlpgui().run()