from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

from components.extra_gui import GradientBoxLayout, ColoredBoxLayout


class TaskBoardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = ColoredBoxLayout(
            orientation='vertical', 
            padding=0, 
            spacing=0, 
            color=(0.1, 0.08, 0.08, 1)
        )

        header = GradientBoxLayout(
            size_hint_y=None,
            height=80,
            color_top=(0.1, 0.1, 0.1, 1),
            color_bottom=(0.24, 0.22, 0.22, 1)
        )

        back_btn = Button(
            text="^\nProject\nBoard", 
            font_name="TitleFont",
            font_size=16,
            halign='center', 
            height=100, 
            width=100, 
            size_hint=(None, None), 
            background_color=(0.3, 0.3, 0.35, 1)
        )
        back_btn.bind(on_release=self.back_to_project_board)

        self.title = Label(text="TASK BOARD", font_name="TitleFont", font_size=32)

        help_btn = Button(
            text="?",
            font_name="TitleFont",
            font_size=32,
            size_hint=(None, None),
            size=(80, 80),
            pos_hint={"right": 0.99, "center_y": 0.5},
            background_color=(0.25, 0.25, 0.3, 1)
        )
        
        header.add_widget(back_btn)
        header.add_widget(self.title)
        header.add_widget(help_btn)

        body = BoxLayout()

        nav_sidebar = ColoredBoxLayout(orientation='vertical', size_hint_x=None, width=100, color=(0.3, 0.3, 0.3, 1))

        body.add_widget(nav_sidebar)

        root.add_widget(header)
        root.add_widget(body)

        self.add_widget(root)


    def back_to_project_board(self, instance):
        self.manager.transition.direction = 'down'
        self.manager.current = 'project_board'