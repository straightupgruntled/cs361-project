from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import (
    Color, Rectangle, RoundedRectangle,
    StencilPush, StencilUse, StencilUnUse, StencilPop
)
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.uix.button import Button
from kivy.core.window import Window


class ColoredBoxLayout(BoxLayout):
    def __init__(self, color=(1, 1, 1, 1), **kwargs):
        super().__init__(**kwargs)
        self.color_value = color

        self._init_canvas()
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _init_canvas(self):
        with self.canvas.before:
            self._color = Color(*self.color_value)
            self._rect = Rectangle(pos=self.pos, size=self.size)

    def _update_canvas(self, *args):
        self._rect.pos = self.pos
        self._rect.size = self.size

    def set_color(self, color):
        self.color_value = color
        self._color.rgba = color


class GradientBoxLayout(BoxLayout):
    def __init__(self, color_top=(1,1,1,1), color_bottom=(0,0,0,1), steps=40, **kwargs):
        super().__init__(**kwargs)

        self.color_top = color_top
        self.color_bottom = color_bottom
        self.steps = steps

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()

        r1, g1, b1, a1 = self.color_top
        r2, g2, b2, a2 = self.color_bottom

        step_height = self.height / float(self.steps) if self.steps else self.height

        with self.canvas.before:
            for i in range(self.steps):
                t = i / float(self.steps - 1)

                r = r1 * (1 - t) + r2 * t
                g = g1 * (1 - t) + g2 * t
                b = b1 * (1 - t) + b2 * t
                a = a1 * (1 - t) + a2 * t

                Color(r, g, b, a)
                Rectangle(
                    pos=(self.x, self.y + i * step_height),
                    size=(self.width, step_height + 1)
                )

    def set_gradient(self, top=None, bottom=None):
        if top:
            self.color_top = top
        if bottom:
            self.color_bottom = bottom
        self._update_canvas()


class RoundedBoxLayout(BoxLayout):
    def __init__(self, color=(1,1,1,1), radius=15, **kwargs):
        super().__init__(**kwargs)

        self._bg_color_value = color
        self._radius_value = radius

        self._init_canvas()
        self.bind(pos=self._update_canvas, size=self._update_canvas)

    def _init_canvas(self):
        with self.canvas.before:
            self._bg_color = Color(*self._bg_color_value)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius_value]
            )

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self._radius_value]

    def set_background_color(self, color):
        self._bg_color_value = color
        self._bg_color.rgba = color

    def set_radius(self, radius):
        self._radius_value = radius
        self._bg_rect.radius = [radius]


class RoundedGradientBoxLayout(BoxLayout):
    def __init__(self, color_top=(1,1,1,1), color_bottom=(0,0,0,1), radius=15, **kwargs):
        super().__init__(**kwargs)

        self.color_top = color_top
        self.color_bottom = color_bottom
        self.radius = radius
        self.steps = self.height

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()

        r1, g1, b1, a1 = self.color_top
        r2, g2, b2, a2 = self.color_bottom

        step_height = self.height / float(self.steps) if self.steps else self.height

        with self.canvas.before:
            StencilPush()
            RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radius]
            )
            StencilUse()

            for i in range(self.steps):
                t = i / float(self.steps - 1)

                r = r1 * (1 - t) + r2 * t
                g = g1 * (1 - t) + g2 * t
                b = b1 * (1 - t) + b2 * t
                a = a1 * (1 - t) + a2 * t

                Color(r, g, b, a)
                Rectangle(
                    pos=(self.x, self.y + i * step_height),
                    size=(self.width, step_height + 1)
                )

            StencilUnUse()
            StencilPop()

    def set_gradient(self, top=None, bottom=None):
        if top:
            self.color_top = top
        if bottom:
            self.color_bottom = bottom
        self._update_canvas()

    def set_radius(self, radius):
        self.radius = radius
        self._update_canvas()


# Creating a custom GUI element like a Rounded Button was a bit complex for this Sprint.
# For now I am not using the RoundedButton class, but I plan to get this working in a future sprint!
class RoundedButton(Button):
    def __init__(
        self,
        color=(0.2, 0.6, 1, 1),
        hover_color=None,
        pressed_color=None,
        text_color=(1, 1, 1, 1),
        hover_text_color=None,
        pressed_text_color=None,
        radius=15,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Disable default background
        self.background_normal = ""
        self.background_down = ""
        self.background_color = (0, 0, 0, 0)
        self.border = (0, 0, 0, 0)

        # Background colors
        self._normal_color = color
        self._hover_color = hover_color or self._darken(color, 0.8)
        self._pressed_color = pressed_color or self._darken(color, 0.6)

        # Text colors
        self._text_normal = text_color
        self._text_hover = hover_text_color or text_color
        self._text_pressed = pressed_text_color or text_color

        self._radius_value = radius
        self._is_hovered = False

        self._init_canvas()

        self.bind(pos=self._update_canvas, size=self._update_canvas)
        self.bind(state=self._update_visual_state)

        # Hover tracking
        Window.bind(mouse_pos=self._on_mouse_pos)

        # Initialize visual state
        self._update_visual_state()

    def _init_canvas(self):
        with self.canvas.before:
            self._bg_color = Color(*self._normal_color)
            self._bg_rect = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self._radius_value]
            )

    def _update_canvas(self, *args):
        self._bg_rect.pos = self.pos
        self._bg_rect.size = self.size
        self._bg_rect.radius = [self._radius_value]

    def _on_mouse_pos(self, window, pos):
        if not self.get_root_window():
            return

        inside = self.collide_point(*self.to_widget(*pos))
        if inside != self._is_hovered:
            self._is_hovered = inside
            self._update_visual_state()

    def _update_visual_state(self, *args):
        if self.state == "down":
            self._bg_color.rgba = self._pressed_color
            self.color = self._text_pressed
        elif self._is_hovered:
            self._bg_color.rgba = self._hover_color
            self.color = self._text_hover
        else:
            self._bg_color.rgba = self._normal_color
            self.color = self._text_normal

    def _darken(self, color, factor):
        return [c * factor for c in color[:3]] + [color[3]]

    def set_color(self, color, _update_hovers=False):
        self._normal_color = color
        if _update_hovers:
            self._hover_color = self._darken(color, 0.8)
            self._pressed_color = self._darken(color, 0.6)
        self._update_visual_state()

    def set_hover_color(self, color):
        self._hover_color = color
        self._update_visual_state()

    def set_pressed_color(self, color):
        self._pressed_color = color
        self._update_visual_state()

    def set_text_color(self, color):
        self._text_normal = color
        self._text_hover = self._text_hover or color
        self._text_pressed = self._text_pressed or color
        self._update_visual_state()

    def set_hover_text_color(self, color):
        self._text_hover = color
        self._update_visual_state()

    def set_pressed_text_color(self, color):
        self._text_pressed = color
        self._update_visual_state()

    def set_radius(self, radius):
        self._radius_value = radius
        self._bg_rect.radius = [radius]