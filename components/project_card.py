from components.extra_gui import RoundedButton

class ProjectCard(RoundedButton):
    def __init__(self, project_data, project_screen, **kwargs):
        super().__init__(**kwargs)

        self.project_data = project_data
        self.project_screen = project_screen

        self.color = (0.55, 0.55, 0.55, 1)
        self.text = project_data.name
        self.font_name = "BodyFont"
        self.font_size = 22
        self.set_text_color((1, 1, 1, 1))

        self.size_hint = (None, None)
        self.size = (300, 160)
        self.set_radius(24)

        self.bind(on_release=self.on_interact)


    def on_interact(self, instance):
        self.project_screen.project_selected(self)


    def set_delete_mode(self, enabled):
        if enabled:
            self.background_color = (0.6, 0.2, 0.2, 1)
        else:
            self.background_color = (0.55, 0.55, 0.55, 1)