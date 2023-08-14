import random

import yt_dlp.utils
from kivy import Config
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.uix.textinput import TextInput
from yt_dlp import YoutubeDL
Window.clearcolor = (0.05, 0.05, 0.07, 1)
Window.size = (900,600)
Config.set('kivy','exit_on_escape',0)
class ytdlpgui(App):
    def build(self):
        layout = FloatLayout()

        self.url_input = TextInput(hint_text='URL/Arguments', pos=(10, 70), size_hint=(.4, .05))
        download_button = Button(text='Download video', on_release=self.download, pos=(10, 20), size_hint=(.4, .08))
        self.progress_bar = ProgressBar(max=100, value=0, pos=(10, 0), size_hint=(1, .05))
        # YoutubeDL().get
        self.consolelog = TextInput(hint_text='URL/Arguments', size_hint=(.8, .8),pos_hint={'right': .98, 'top': .98}, disabled=True)

        layout.add_widget(self.url_input)
        layout.add_widget(download_button)
        layout.add_widget(self.progress_bar)
        layout.add_widget(self.consolelog)

        return layout
    # def build(self):
    #     sm = ScreenManager()
    #     sm.add_widget(MainScreen(name='main'))
    #     sm.add_widget(SecondScreen(name='second'))
    #     return sm
    def download(self,instance=None):
        self.progress_bar.value = random.randint(1,100)
        text_input = self.url_input # Access the TextInput widget by its ID
        url = text_input.text
        print("Now downloading ", url)
        with yt_dlp.YoutubeDL() as ydl:
            try:
                info_dict = ydl.extract_info(url, download=False)
                if info_dict:
                    print("The URL is valid ", url)
                    YoutubeDL().download([url])
                else:
                    print("Invalid URL ", url)
                    return False
            except Exception:
                print("Invalid URL ", url)
                return False
# class MainScreen(Screen):
#     pass
# class SecondScreen(Screen):
#     pass
if __name__ == '__main__':
    ytdlpgui().run()