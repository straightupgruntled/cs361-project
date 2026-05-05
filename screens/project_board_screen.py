from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView

from components.extra_gui import ColoredBoxLayout, GradientBoxLayout, RoundedButton
from components.project_card import ProjectCard

from models.project_data import ProjectData


class ProjectBoardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.project_cards: list[ProjectCard] = []

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

        self.grid = GridLayout(cols=1, spacing=15, size_hint=(None, None), padding=15)
        self.grid.bind(minimum_height=self.grid.setter('height'))

        wrapper = BoxLayout(size_hint=(1, None))
        wrapper.bind(minimum_height=wrapper.setter('height'))
        wrapper.add_widget(self.grid)

        self.scroll = ScrollView()
        self.scroll.add_widget(wrapper)

        main_content.add_widget(self.scroll)

        root.add_widget(header)
        root.add_widget(main_content)

        self.add_widget(root)

        project_data = ProjectData("Test Project")
        self.create_project_card(project_data)


    def update_layout(self, *args):
        width = Window.width
        card_width = 300
        spacing = 20
        cols = max(1, width // (card_width + spacing))
        self.grid.cols = cols
        self.grid.width = cols * (card_width + spacing)


    def project_selected(self, project_card):
        self.open_project(self)


    def create_project_card(self, project_data):
        project_card = ProjectCard(project_data, self)
        self.project_cards.append(project_card)
        self.grid.add_widget(project_card)
        self.update_layout()


    def open_project(self, instance):
        self.manager.transition.direction = 'up'
        self.manager.current = 'task_board'