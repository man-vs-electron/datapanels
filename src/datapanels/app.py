""" The main "executable" for datapanels

"""

import argparse
from datetime import datetime
import numpy as np
from kivy.lang.builder import Builder
from kivy.uix.pagelayout import PageLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import ObjectProperty
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.core.window import Window
from datapanels.globals import ui_lock

from kwidgets.text.quotationdisplay import QuotationDisplay
from datapanels.stockpanel import StockPanel

__default_string = """
<DataBuilder>:
    border: 0
    QuotationDisplay:
        update_sec: 5
        quotations: "See https://github.com/man-vs-electron/datapanels for info on how to configure this application.", "Where you go, that's where you'll be", "Thanks for trying this application."
    StockPanel:
        tickers: 'MSFT', 'PSEC'
        data_update_rate_sec: 60*20
        panel_change_rate_sec: 20
"""

class DataBuilder(PageLayout):

    def rotate(self, dt):
        with ui_lock:
            self.page = np.random.choice(len(self.children))

    def prev_page(self):
        with ui_lock:
            self.page = (self.page - 1) % len(self.children)

    def next_page(self):
        with ui_lock:
            self.page = (self.page + 1) % len(self.children)

Builder.load_string("""
#:import exit sys.exit
<DataPanels>:
    _databuilder: databuilder
    _currenttime: currenttime
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        size_hint: 1, None
        size: 0, 30
        Label:
            id: currenttime
            halign: 'left'
            text_size: self.width-10, self.height
            text: "currenttime"
        Button:
            size_hint: None, 1
            size: 90, 0
            canvas:
                Color:
                    rgba: 0, 1, 0, 1
                Line:
                    width: 2
                    points: self.x+40, self.y+self.height/2, self.x+self.width-40, self.y+self.height-10
                Line:
                    width: 2
                    points: self.x+40, self.y+self.height/2, self.x+self.width-40, self.y+10
            on_press: databuilder.prev_page()
        Button:
            size_hint: None, 1
            size: 90, 0
            canvas:
                Color:
                    rgba: 0, 1, 0, 1
                Line:
                    width: 2
                    points: self.x+40, self.y+10, self.x+self.width-40, self.y+self.height/2
                Line:
                    width: 2
                    points: self.x+40, self.y+self.height-10, self.x+self.width-40, self.y+self.height/2
            on_press: databuilder.next_page()
        Button:
            size_hint: None, 1
            size: 30, 0
            canvas:
                Color:
                    rgba: 1, 0, 0, 1
                Line:
                    width: 2
                    points: self.x+10, self.y+10, self.x+self.width-10, self.y+self.height-10
                Line:
                    width: 2
                    points: self.x+10, self.y+self.height-10, self.x+self.width-10, self.y+10
            on_press: exit()
    DataBuilder:
        id: databuilder
""")

class DataPanels(BoxLayout):
    _databuilder: ObjectProperty(None)
    _currenttime: ObjectProperty("datetime")

    def update_datetime(self, dt):
        self._currenttime.text = datetime.now().strftime("%b %d, %Y %H:%M")

class DataPanelsApp(App):
    transition_sec: int = 60*10
    full_screen: bool = False

    def __init__(self, transition_sec = 60*10, full_screen=False, **kwargs):
        super(DataPanelsApp, self).__init__(**kwargs)
        self.transition_sec = transition_sec
        self.full_screen = full_screen

    def build(self):
        container = DataPanels()
        Logger.info("DataPanelsApp: Setting panel transition to %d seconds" % self.transition_sec)
        Clock.schedule_interval(container._databuilder.rotate, self.transition_sec)
        Clock.schedule_interval(container.update_datetime, 60)
        container.update_datetime(None)
        if self.full_screen:
            Window.fullscreen=True
        return container


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start DataPanels")
    parser.add_argument('--builder_path', default=None, required=False, type=str, help='Path to file with builder string')
    parser.add_argument("--transition_sec", default=30, required=False, type=int, help='Time between transitions in seconds')
    parser.add_argument("--full_screen", default=False, required=False, type=bool, help="Whether to make the application full screen")
    args = parser.parse_args()
    if args.builder_path is None:
        string_to_load = __default_string
    else:
        with open(args.builder_path, 'r') as f:
            string_to_load = f.read()
    Builder.load_string(string_to_load)
    DataPanelsApp(transition_sec=args.transition_sec, full_screen=args.full_screen).run()
