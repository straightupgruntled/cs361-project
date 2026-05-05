from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup

from components.extra_gui import ColoredBoxLayout, GradientBoxLayout


class TaskEditPanel(ColoredBoxLayout):
    def __init__(self, **kwargs):
        super().__init__(
            orientation='vertical',
            size_hint=(0.5, 1),
            pos_hint={"right": 1},
            padding=20,
            spacing=15,
            disabled=False,
            **kwargs
        )
        
        self.current_task = None
        self.task_board_screen = None

        self.set_color((0.05, 0.05, 0.06, 0.95))

        header = BoxLayout(
            size_hint_y=None,
            height=80,
            pos_hint = {"hcenter_x": 0.5, "top": 1}
        )

        # Close (TOP LEFT)
        close_btn = Button(
            text="<",
            font_name="TitleFont",
            font_size=28,
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={"x": 0, "center_y": 0.5}
        )
        close_btn.bind(on_release=self.hide)

        # Title (CENTER)
        self.title = Label(
            text="VIEW & EDIT TASK",
            font_name="TitleFont",
            font_size=28,
            size_hint_y=None,
            height=40
        )

        # Delete (TOP RIGHT)
        delete_btn = Button(
            text="X",
            font_name="TitleFont",
            size_hint=(None, None),
            size=(40, 40),
            pos_hint={"right": 1, "center_y": 0.5},
            background_color=(0.8, 0.2, 0.2, 1)
        )
        delete_btn.bind(on_release=self.confirm_delete)

        header.add_widget(close_btn)
        header.add_widget(self.title)
        header.add_widget(delete_btn)

        

        name_label = Label(text="Task Name", font_name="BodyFont", size_hint_y=None, height=20)

        self.name_input = TextInput(
            multiline=False,
            font_name="BodyFont",
            size_hint_y=None,
            height=40
        )

        desc_label = Label(text="Task Description", font_name="BodyFont", size_hint_y=None, height=20)

        self.desc_input = TextInput(
            multiline=True,
            font_name="BodyFont"
        )

        self.add_widget(header)
        self.add_widget(name_label)
        self.add_widget(self.name_input)
        self.add_widget(desc_label)
        self.add_widget(self.desc_input)

        self.name_input.bind(text=self.on_name_change)
        self.desc_input.bind(text=self.on_desc_change)


    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size


    def open_task(self, task_data):
        self.current_task = task_data
        self.name_input.text = task_data.name
        self.desc_input.text = task_data.description


    def hide(self, *args):
        if self.current_task:
            self.current_task.name = self.name_input.text
            self.current_task.description = self.desc_input.text
        if self.task_board_screen:
            self.task_board_screen.close_task_editor()
        self.current_task = None


    def on_name_change(self, instance, value):
        if self.current_task:
            self.current_task.name = value

            if self.current_task.ui_card:
                self.current_task.ui_card.refresh()


    def on_desc_change(self, instance, value):
        if self.current_task:
            self.current_task.description = value


    def confirm_delete(self, instance):
        if not self.current_task:
            return

        layout = BoxLayout(orientation='vertical', spacing=10, padding=10)

        label = Label(
            text=f"Delete task:\n\n'{self.current_task.name}'?",
            halign="center"
        )
        label.bind(size=label.setter('text_size'))

        btn_row = BoxLayout(size_hint_y=None, height=40, spacing=10)

        confirm_btn = Button(text="Confirm", background_color=(0.7, 0.2, 0.2, 1))
        cancel_btn = Button(text="Cancel")

        btn_row.add_widget(confirm_btn)
        btn_row.add_widget(cancel_btn)

        layout.add_widget(label)
        layout.add_widget(btn_row)

        popup = Popup(
            title="Confirm Deletion",
            content=layout,
            size_hint=(None, None),
            size=(350, 200)
        )

        def do_delete(instance):
            if self.current_task.ui_card:
                self.current_task.ui_card.parent_column.remove_task(
                    self.current_task.ui_card
                )

            popup.dismiss()
            self.hide()

        confirm_btn.bind(on_press=do_delete)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()