import kivy

kivy.require('1.11.1')
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.anchorlayout import AnchorLayout


class MainApp(App):
    def build(self):
        self.root = root = MainLayout()
        return root


#########################################################
#              Layout of the application                #
#########################################################

class MainLayout(AnchorLayout):
    def __init__(self, **kwargs):
        # do not override any important functionality of kivy
        super(MainLayout, self).__init__(**kwargs)
        self.add_widget(Label(text='Main Layout Label'))


class PanelControlLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(PanelControlLayout, self).__init__(**kwargs)
        pass


class VisualizationPanelLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(VisualizationPanelLayout, self).__init__(**kwargs)
        pass


if __name__ == '__main__':
    app = MainApp()
    app.run()
    print(kivy.__version__)
