from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

from components.extra_gui import ColoredBoxLayout, GradientBoxLayout, RoundedButton


class ProjectBoardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        root = ColoredBoxLayout(
            orientation='vertical', 
            padding=0, 
            spacing=0, 
            color=(0.1, 0.08, 0.08, 1)
        )

        header = GradientBoxLayout(
            orientation='vertical',
            size_hint_y=None,
            height=240,
            spacing=5,
            color_top=(0.1, 0.1, 0.1, 1),
            color_bottom=(0.24, 0.22, 0.22, 1),
            center_x=0.5
        )

        title = Label(
            text="DEV PROJECT MANAGER", 
            font_name="TitleFont", 
            font_size=42
        )
        
        subtitle = Label(
            text="PROJECT BOARD", 
            font_name="TitleFont", 
            font_size=32, 
            size_hint_y=None, 
            height=40
        )

        tagline = Label(
            text="Creating Project Boards allows you to group tasks and documentation by each project you work on.\n"
                 "This helps you to stay organized and group your tasks, documentation, and other PM elements into distinct workspaces.\n"
                 "Deleting Projects is done by clicking Delete Project, then selecting the project to delete.",
            font_name="BodyFont",
            font_size=14,
            halign="center",
            valign="middle"
        )
        tagline.bind(size=tagline.setter('text_size'))

        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(tagline)

        main_content = FloatLayout()

        root.add_widget(header)
        root.add_widget(main_content)

        self.add_widget(root)

        testbutton = RoundedButton(
            text="GO TO TASK BOARD",
            font_name="TitleFont",
            font_size=20,
            color=(0.2, 0.6, 0.8, 1),
            hover_color=(1, 0.5, 0.5, 1),
            pressed_color=(1, 0.3, 0.3, 1),
            radius=20,
            size_hint=(None, None),
            size=(200, 46),
            pos_hint={"center_x": 0.5, "center_y": 0.5}
        )
        testbutton.bind(on_press=self.open_project)
        main_content.add_widget(testbutton)
    

    def open_project(self, instance):
        self.manager.transition.direction = 'up'
        self.manager.current = 'task_board'