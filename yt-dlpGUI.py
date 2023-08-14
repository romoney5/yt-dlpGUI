import yt_dlp.utils
from kivy.app import App
from kivy.core.window import Window
# from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.button import Button
# from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
# from kivy.uix.textinput import TextInput
from yt_dlp import YoutubeDL
Window.clearcolor = (0.05, 0.05, 0.07, 1)
Window.size = (900,600)
class ytdlpgui(App):
    # def build(self):
    #     layout = BoxLayout(orientation='vertical', padding=10)
    #
    #     label = Label(text='Hello, Kivy!')
    #     text_input = TextInput(hint_text='Enter something...')
    #     button = Button(text='Click Me')
    #
    #     layout.add_widget(label)
    #     layout.add_widget(text_input)
    #     layout.add_widget(button)
    #
    #     return layout
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(SecondScreen(name='second'))
        return sm
    def print_text(self):
        text_input = self.root.get_screen('main').ids.url  # Access the TextInput widget by its ID
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
class MainScreen(Screen):
    pass
class SecondScreen(Screen):
    pass
if __name__ == '__main__':
    ytdlpgui().run()