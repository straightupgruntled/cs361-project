from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from components.extra_gui import RoundedBoxLayout


class TaskCard(RoundedBoxLayout):
    def __init__(self, task_data, parent_column, **kwargs):
        super().__init__(orientation='vertical', size_hint_y=None, height=120, padding=10, **kwargs)
    
        self.task_data = task_data
        self.task_data.ui_card = self
        self.parent_column = parent_column

        self.set_background_color((0.35, 0.35, 0.35, 1))
        self.set_radius(15)

        layout = FloatLayout()
        content = BoxLayout(orientation='horizontal', size_hint=(1, 0.8), pos_hint={"center_x": 0.5, "center_y": 0.5})

        left_btn = Button(
            text="<",
            size_hint_x=None,
            size_hint_y=0.5,
            width=40,
            height = 25,
            font_name="TitleFont"
        )
        left_btn.bind(on_press=self.move_left)

        self.label = Label(
            text=task_data.name,
            font_name="BodyFont",
            halign="center",
            valign="middle",
            width = 400,
            size_hint_x=1,
        )
        self.label.bind(size=self.label.setter('text_size'))

        right_btn = Button(
            text=">",
            size_hint_x=None,
            size_hint_y=0.5,
            width=40,
            height = 25,
            font_name="TitleFont"
        )
        right_btn.bind(on_press=self.move_right)

        content.add_widget(left_btn)
        content.add_widget(self.label)
        content.add_widget(right_btn)

        delete_btn = Button(
            text="X",
            size_hint=(None, None),
            size=(20, 20),
            pos_hint={"right": 1, "top": 1},
            font_name="TitleFont",
            background_color=(0.9, 0.1, 0.1, 1)
        )
        delete_btn.bind(on_press=self.delete_task)

        edit_btn = Button(
            text="E",
            size_hint=(None, None),
            size=(20, 20),
            pos_hint={"x": 0, "top": 1},
            font_name="TitleFont"
        )
        edit_btn.bind(on_press=self.edit_task)

        layout.add_widget(content)
        layout.add_widget(delete_btn)
        layout.add_widget(edit_btn)

        self.add_widget(layout)

        if self.parent_column.title == "BACKLOG TASKS":
            left_btn.disabled = True

        if self.parent_column.title == "FINISHED TASKS":
            right_btn.disabled = True


    def edit_task(self, instance):
        print("EDIT TASK TRIGGERED!")
        self.parent_column.parent_screen.open_task_editor(self.task_data)

    
    def delete_task(self, instance):
        content = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(
            text=f"Delete task:\n\n'{self.task_data.name}'?",
            font_name="BodyFont",
            halign="center"
        )
        label.bind(size=label.setter('text_size'))

        button_row = BoxLayout(size_hint_y=None, height=40, spacing=10)

        confirm_btn = Button(
            text="Confirm",
            font_name="TitleFont",
            background_color=(0.7, 0.2, 0.2, 1)
        )

        cancel_btn = Button(
            text="Cancel",
            font_name="TitleFont"
        )

        button_row.add_widget(confirm_btn)
        button_row.add_widget(cancel_btn)

        content.add_widget(label)
        content.add_widget(button_row)

        popup = Popup(
            title="Confirm Task Deletion",
            title_font="TitleFont",
            content=content,
            size_hint=(None, None),
            size=(350, 200),
            auto_dismiss=False
        )

        def confirm(instance):
            self.parent_column.remove_task(self)
            popup.dismiss()

        def cancel(instance):
            popup.dismiss()

        confirm_btn.bind(on_press=confirm)
        cancel_btn.bind(on_press=cancel)

        popup.open()


    def move_left(self, instance):
        self.parent_column.move_task(self, direction=-1)


    def move_right(self, instance):
        self.parent_column.move_task(self, direction=1)


    def refresh(self):
        self.label.text = self.task_data.name