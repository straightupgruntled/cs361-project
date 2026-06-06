import zmq

from kivy.core.window import Window
from kivy.app import App
from kivy.graphics import Color, Line, Rectangle
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.image import Image as CoreImage
from kivy.uix.image import Image

from microservices.clients import (
    ImageMicroClient,
    FileImporterMicroClient,
    UndoRedoClient,
)


class BrushCursor(Widget):
    def __init__(self, tool, **kwargs):
        super().__init__(**kwargs)

        self.tool = tool
        self.radius = 10

        self.visible = False
        self.cursor_pos = (0, 0)

        self.bind(pos=self.update_draw, size=self.update_draw)

        with self.canvas:
            self.color = Color(1, 1, 1, 0.6)
            self.circle = Line(circle=(0, 0, 10), width=1.2)

    def update(self, pos, radius, tool):
        self.cursor_pos = pos
        self.radius = radius
        self.visible = tool.state in (Tool.STATE_PEN, Tool.STATE_ERASE)
        self.update_draw()

    def update_draw(self, *args):
        self.canvas.clear()
        if not self.visible:
            return
        with self.canvas:
            Color(1, 1, 1, 0.5)
            x, y = self.cursor_pos
            r = self.radius
            Line(circle=(x, y, r), width=1.2)


class Tool:
    STATE_PEN = "pen"
    STATE_ERASE = "erase"
    STATE_GRAB = "grab"

    def __init__(self):
        self.state = Tool.STATE_PEN
        self.color = (1, 1, 1)
        self.brush_width = 2

    def set_state(self, state):
        self.state = state

    def set_color(self, color):
        self.color = color

    def set_brush_width(self, width):
        self.brush_width = width


class BlackboardBackground(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas:
            Color(0.08, 0.15, 0.08)
            self.rect = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self._update, size=self._update)

    def _update(self, *_):
        self.rect.pos = self.pos
        self.rect.size = self.size


class ImageLayer(FloatLayout):
    # ZMQ IMAGE CLIENT
    def __init__(self, tool, **kwargs):
        super().__init__(**kwargs)
        self.tool = tool


class DraggableImage(Image):
    def __init__(self, tool, **kwargs):
        super().__init__(**kwargs)
        self.tool = tool
        self.drag_touch = None

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        if self.tool.state != Tool.STATE_GRAB:
            return False
        self.drag_touch = touch
        self._offset = (touch.x - self.x, touch.y - self.y)
        return True

    def on_touch_move(self, touch):
        if not touch is self.drag_touch:
            return False
        self.pos = (touch.x - self._offset[0], touch.y - self._offset[1])
        return True

    def on_touch_up(self, touch):
        if touch is self.drag_touch:
            self.drag_touch = None
            return True
        return False


class DrawingLayer(Widget):
    def __init__(self, tool, **kwargs):
        super().__init__(**kwargs)
        self.tool = tool
        self.strokes = []
        self.current_stroke = None

    def clear(self):
        self.canvas.clear()
        self.strokes = []
        self.current_stroke = None
        self.parent.parent.undo_client.record(self.parent.parent.get_state())

    def redraw(self):
        self.canvas.clear()

        with self.canvas:
            for stroke in self.strokes:
                Color(*stroke["color"])
                Line(points=stroke["points"], width=stroke["width"])

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        tool = self.tool

        if tool.state == Tool.STATE_GRAB:
            return False  # let DraggableImage handle it

        elif tool.state == Tool.STATE_ERASE:
            self.erase_at_point(touch.pos)
            return True

        elif tool.state == Tool.STATE_PEN:
            self.current_stroke = {
                "color": tool.color,
                "width": tool.brush_width,
                "points": [touch.x, touch.y],
            }
            self.strokes.append(self.current_stroke)
            self.redraw()
        return True

    def on_touch_up(self, touch):
        if self.tool.state == Tool.STATE_GRAB:
            return

        self.current_stroke = None
        if not self.collide_point(*touch.pos):
            return False

        self.parent.parent.undo_client.record(self.parent.parent.get_state())
        return True

    def on_touch_move(self, touch):
        if not self.collide_point(*touch.pos):
            return False

        tool_type = self.tool.state

        if tool_type == Tool.STATE_GRAB:
            return False  # let DraggableImage handle it
        elif tool_type == Tool.STATE_ERASE:
            self.erase_at_point(touch.pos)
            return True
        elif tool_type == Tool.STATE_PEN and self.current_stroke:
            self.current_stroke["points"].extend([touch.x, touch.y])
            self.redraw()
        return True

    def erase_at_point(self, pos, radius=20):
        px, py = pos
        new_strokes = []

        for stroke in self.strokes:
            points = stroke["points"]
            # check if any segment is near erase point
            keep = True
            for i in range(0, len(points), 2):
                x, y = points[i], points[i + 1]
                if (abs(x - px) ** 2 + abs(y - py) ** 2) ** 0.5 < radius:
                    keep = False
                    break
            if keep:
                new_strokes.append(stroke)

        self.strokes = new_strokes
        self.redraw()


# MAIN WIDGET
class DrawingBoard(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        Window.bind(mouse_pos=self.on_mouse_pos)

        # LAYERED WORKSPACE
        self.workspace = RelativeLayout(size_hint=(1, 1))

        self.tool = Tool()

        self.background = BlackboardBackground()
        self.images = ImageLayer(self.tool)
        self.drawing = DrawingLayer(self.tool)
        for layer in (self.background, self.images, self.drawing):
            layer.size_hint = (1, 1)
            self.workspace.add_widget(layer)

        self.cursor = BrushCursor(self.tool)
        self.workspace.add_widget(self.cursor)  # IMPORTANT: above workspace

        # TOOLBAR
        self.toolbar = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=60, spacing=5, padding=5
        )

        set_pen = lambda *_: self.tool.set_state(Tool.STATE_PEN)
        self.toolbar.add_widget(Button(text="Pen", on_release=set_pen))

        set_erase = lambda *_: self.tool.set_state(Tool.STATE_ERASE)
        self.toolbar.add_widget(Button(text="Erase", on_release=set_erase))

        set_grab = lambda *_: self.tool.set_state(Tool.STATE_GRAB)
        self.toolbar.add_widget(Button(text="Grab", on_release=set_grab))

        colors = [
            (1, 1, 1),  # WHITE
            (1, 0, 0),  # RED
            (0, 1, 0),  # GREEN
            (0, 0, 1),  # BLUE
            (1, 1, 0),  # YELLOW
        ]

        def make_color_handler(tool, col):
            def _set_color(instance):
                tool.color = col
                tool.set_state(Tool.STATE_PEN)

            return _set_color

        for color in colors:
            btn = Button(
                text="",
                size_hint=(None, 1),
                width=42,
                background_normal="",
                background_color=(*color, 1),
            )

            btn.bind(on_release=make_color_handler(self.tool, color))
            self.toolbar.add_widget(btn)

        brush_size_slider = Slider(min=1, max=30, value=2, width=300)
        set_brush_size = lambda *_: self.tool.set_brush_width(brush_size_slider.value)
        brush_size_slider.bind(value=set_brush_size)
        self.toolbar.add_widget(brush_size_slider)

        self.toolbar.add_widget(
            Button(
                text="Clear",
                size_hint_x=None,
                width=100,
                on_release=lambda *_: self.drawing.clear(),
            )
        )

        self.toolbar.add_widget(
            Button(
                text="Web\nImage",
                size_hint_x=None,
                width=100,
                on_release=lambda *_: self.open_image_popup(),
            )
        )

        self.toolbar.add_widget(
            Button(
                text="File\nImage",
                size_hint_x=None,
                width=100,
                on_release=lambda *_: self.open_file_image_popup(),
            )
        )

        undo_button = Button(text="Undo", on_release=lambda *_: self.undo())
        redo_button = Button(text="Redo", on_release=lambda *_: self.redo())

        self.toolbar.add_widget(undo_button)
        self.toolbar.add_widget(redo_button)

        # FINAL LAYOUT
        self.add_widget(self.toolbar)
        self.add_widget(self.workspace)

        # MICROSERVICE CLIENTS SETUP
        self.image_client = ImageMicroClient()
        self.file_client = FileImporterMicroClient()
        self.undo_client = UndoRedoClient(self.get_state())

    def get_state(self):
        return {"strokes": self.drawing.strokes}

    def set_state(self, state):
        # restore strokes
        self.drawing.strokes = state.get("strokes", [])
        self.drawing.redraw()

    def undo(self):
        response = self.undo_client.undo()

        if response["status"] == "success":
            print(response)
            self.set_state(response["state"])

    def redo(self):
        response = self.undo_client.redo()

        if response["status"] == "success":
            print(response)
            self.set_state(response["state"])

    def on_mouse_pos(self, window, pos):
        local_x, local_y = self.workspace.to_widget(*pos)

        self.cursor.update((local_x, local_y), self.tool.brush_width, self.tool)

    # IMAGE POPUP
    def open_image_popup(self):
        layout = BoxLayout(orientation="vertical", padding=10, spacing=10)

        url_input = TextInput(hint_text="Image URL")
        layout.add_widget(url_input)

        btn = Button(text="Add Image", size_hint_y=None, height=40)
        layout.add_widget(btn)

        popup = Popup(title="Import Image", content=layout, size_hint=(0.8, 0.4))

        def submit(*_):
            try:
                texture = self.image_client.fetch(url_input.text.strip())
                print("Requesting image from URL:", url_input.text.strip())

                img = DraggableImage(
                    tool=self.tool,
                    texture=texture,
                    size_hint=(None, None),
                    size=(200, 200),
                    pos=(100, 100),
                )

                self.images.add_widget(img)
                popup.dismiss()

            except Exception as e:
                print("Image error:", e)

        btn.bind(on_release=submit)
        popup.open()

    # FILE IMAGE POPUP
    def open_file_image_popup(self):
        try:
            file_path = self.file_client.open_file_dialog(
                file_types=["png", "jpg", "jpeg", "gif", "bmp", "all"]
            )

            if file_path:
                try:
                    # Load image from file path
                    texture = CoreImage(file_path).texture

                    img = DraggableImage(
                        tool=self.tool,
                        texture=texture,
                        size_hint=(None, None),
                        size=(200, 200),
                        pos=(100, 100),
                    )

                    self.images.add_widget(img)
                    print(f"Image loaded from file: {file_path}")

                except Exception as e:
                    print(f"Error loading image from file: {e}")

        except Exception as e:
            print(f"Error opening file dialog: {e}")


class BlackboardApp(App):
    def build(self):
        return DrawingBoard()


if __name__ == "__main__":
    BlackboardApp().run()
