from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager

from screens.black_board_screen import BlackBoardScreen
from screens.project_board_screen import ProjectBoardScreen
from screens.task_board_screen import TaskBoardScreen

from microservices.micro_manager import MicroserviceManager

Window.size = (1280, 720)

LabelBase.register(name="TitleFont", fn_regular="fonts/BUILT_TILTING.otf")
LabelBase.register(name="BodyFont", fn_regular="fonts/BAHNSCHRIFT.TTF")


class ProjectApp(App):
    def build(self):
        # Microservice Process Setup
        self.microservices = MicroserviceManager("microservices/services")
        self.microservices.start_all()

        # Screen Scene Setup
        sm = ScreenManager()
        sm.transition.duration = 0.225
        sm.add_widget(ProjectBoardScreen(name="project_board"))
        sm.add_widget(TaskBoardScreen(name="task_board"))
        sm.add_widget(BlackBoardScreen(name="black_board"))
        return sm

    def on_stop(self):
        self.microservices.stop_all()
        return super().on_stop()


if __name__ == "__main__":
    ProjectApp().run()
