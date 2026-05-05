from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

from components.extra_gui import RoundedBoxLayout
from components.task_card import TaskCard
from models.task_data import TaskData

class TaskColumn(RoundedBoxLayout):
    def __init__(self, title, color, parent_screen, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=10, **kwargs)

        self.title = title
        self.title_size = 28
        self.task_data_list = None
        self.parent_screen = parent_screen

        self.set_background_color(color)
        self.set_radius(20)

        self.title_label = Label(
            text=title,
            font_name="TitleFont",
            font_size=self.title_size,
            size_hint_y=None,
            height=40
        )

        self.task_container = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            spacing=10
        )
        self.task_container.bind(minimum_height=self.task_container.setter('height'))

        scroll = ScrollView()
        scroll.add_widget(self.task_container)

        add_btn = Button(
            text="+",
            size_hint_y=None,
            height=40,
            font_name="TitleFont"
        )
        add_btn.bind(on_press=self.add_task_popup)

        self.add_widget(self.title_label)
        self.add_widget(scroll)
        self.add_widget(add_btn)


    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


    def bind_to_task_data_list(self, task_data_list):
        self.task_data_list = task_data_list


    def add_task(self, task_data, save=True):
        card = TaskCard(task_data, self)
        self.task_container.add_widget(card)

        if save and self.task_data_list is not None:
            self.task_data_list.append(task_data)


    def remove_task(self, task_card):
        # Remove from UI
        if task_card in self.task_container.children:
            self.task_container.remove_widget(task_card)
        # Remove from data
        if self.task_data_list and task_card.task_data in self.task_data_list:
            self.task_data_list.remove(task_card.task_data)


    def add_task_popup(self, instance):
        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        input_box = TextInput(hint_text="Task description", font_name="BodyFont")
        confirm = Button(text="Add Task", font_name="TitleFont", size_hint_y=None, height=40)

        layout.add_widget(input_box)
        layout.add_widget(confirm)

        popup = Popup(title="New Task", content=layout, size_hint=(None, None), size=(400, 200))

        def submit(instance):
            text = input_box.text.strip()
            if text:
                task_data = TaskData(name=text)
                self.add_task(task_data, save=True)
                popup.dismiss()

        confirm.bind(on_press=submit)
        popup.open()


    def clear(self):
        self.task_container.clear_widgets()


    def move_task(self, task_card, direction):
        screen = self.parent_screen
        columns = [screen.backlog_column, screen.active_column, screen.finished_column]

        current_index = columns.index(self)
        new_index = current_index + direction

        # Prevent out-of-bounds
        if new_index < 0 or new_index >= len(columns):
            return

        target_column = columns[new_index]

        self.remove_task(task_card)

        # Add to new column
        target_column.add_task(task_card.task_data, save=True)

        # Refresh UI
        screen.refresh_ui()
        