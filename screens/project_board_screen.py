from kivy.core.window import Window
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex

from components.extra_gui import ColoredBoxLayout, GradientBoxLayout
from components.project_card import ProjectCard

from models.project_data import ProjectData


class ProjectBoardScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.project_cards: list[ProjectCard] = []
        self.delete_mode = False

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

        button_row = BoxLayout(
            size_hint_y=None, 
            size_hint_x=0.35, 
            pos_hint={'center_x': 0.5}, 
            height=50, 
            spacing=10,
            padding=4
        )

        self.create_btn = Button(
            text="+ CREATE PROJECT", 
            font_name="TitleFont", 
            font_size=24,
            background_color=get_color_from_hex("#779777")
        )
        self.create_btn.bind(on_press=self.open_create_popup)

        self.delete_btn = Button(
            text="x DELETE PROJECT", 
            font_name="TitleFont", 
            font_size=24,
            background_color=get_color_from_hex("#A37D7D")
        )
        self.delete_btn.bind(on_press=self.toggle_delete_mode)

        button_row.add_widget(self.create_btn)
        button_row.add_widget(self.delete_btn)

        header.add_widget(title)
        header.add_widget(subtitle)
        header.add_widget(tagline)
        header.add_widget(button_row)

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


    def update_layout(self, *args):
        width = Window.width
        card_width = 300
        spacing = 20
        cols = max(1, width // (card_width + spacing))
        self.grid.cols = cols
        self.grid.width = cols * (card_width + spacing)


    def open_create_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        input_box = TextInput(hint_text="Project Name", font_name="BodyFont")
        confirm_btn = Button(text="Create", font_name="TitleFont", font_size=24, size_hint_y=None, height=40, background_color=(0, 1, 0, 1))

        layout.add_widget(input_box)
        layout.add_widget(confirm_btn)

        popup = Popup(title="Create Project", title_font="TitleFont", title_size=24,
                      content=layout, size_hint=(None, None), size=(400, 200))

        def confirm(instance):
            name = input_box.text.strip()
            if name:
                new_project_data = ProjectData(name)
                self.create_project_card(new_project_data)
                popup.dismiss()

        confirm_btn.bind(on_press=confirm)
        popup.open()


    def toggle_delete_mode(self, instance):
        self.delete_mode = not self.delete_mode
        self.create_btn.disabled = self.delete_mode

        for card in self.project_cards:
            card.set_delete_mode(self.delete_mode)

        self.delete_btn.text = "CANCEL DELETE" if self.delete_mode else "DELETE PROJECT"


    def create_project_card(self, project_data):
        project_card = ProjectCard(project_data, self)
        self.project_cards.append(project_card)
        self.grid.add_widget(project_card)
        self.update_layout()
    

    def project_selected(self, project_card):
        if self.delete_mode:
            self.delete_project(project_card)
        else:
            self.open_project(project_card.project_data)


    def open_project(self, project_data):
        self.manager.transition.direction = 'up'
        self.manager.current = 'task_board'
        
        task_board = self.manager.get_screen('task_board')
        task_board.load_project_data(project_data)


    def delete_project(self, project_card):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(
            text=f"Delete project '{project_card.project_data.name}'?\n\n"
                   "Removing the project will permanantly delete it.",
            halign="center",
            font_name="BodyFont")

        buttons = BoxLayout(size_hint_y=None, height=40, spacing=10)
        confirm_btn = Button(text="Confirm", font_name="TitleFont", font_size=24, background_color=(0.7, 0.2, 0.2, 1))
        cancel_btn = Button(text="Cancel", font_name="TitleFont", font_size=24)

        buttons.add_widget(confirm_btn)
        buttons.add_widget(cancel_btn)

        content.add_widget(label)
        content.add_widget(buttons)

        popup = Popup(title="Confirm Deletion", title_font="TitleFont", title_size=24,
                      content=content, size_hint=(None, None), size=(400, 240))

        def confirm(instance):
            self.grid.remove_widget(project_card)
            self.project_cards.remove(project_card)

            popup.dismiss()
            self.toggle_delete_mode(self.delete_btn)
            self.update_layout()

        def cancel(instance):
            popup.dismiss()

        confirm_btn.bind(on_press=confirm)
        cancel_btn.bind(on_press=cancel)

        popup.open()