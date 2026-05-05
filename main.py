from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout

from components.extra_gui import RoundedBoxLayout, RoundedButton

Window.size = (1280, 720)

LabelBase.register(name="TitleFont", fn_regular="fonts/BUILT_TILTING.otf")
LabelBase.register(name="BodyFont", fn_regular="fonts/BAHNSCHRIFT.TTF")

class ProjectApp(App):
    def build(self):
        sm = ScreenManager()
        testscreen = Screen(name="test")
        
        testbox = RoundedBoxLayout(
            color=(1, 0.9, 0.9, 1),
            radius=30,
            size_hint=(None, None),
            size=(600, 600),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )

        testbox_contents = FloatLayout()

        testbutton = RoundedButton(
            text="Test Button",
            font_name="TitleFont",
            font_size=24,
            color=(0.2, 0.6, 0.8, 1),
            hover_color=(1, 0.5, 0.5, 1),
            pressed_color=(1, 0.3, 0.3, 1),
            radius=20,
            size_hint=(None, None),
            size=(200, 46),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        testbutton.bind(on_press=self.test_press)

        testbox_contents.add_widget(testbutton)
        testbox.add_widget(testbox_contents)
        testscreen.add_widget(testbox)
        sm.add_widget(testscreen)

        return sm

    def test_press(self, instance):
        print("Button was pressed!")

if __name__ == "__main__":
    ProjectApp().run()