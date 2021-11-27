""" The main "executable" for datapanels

"""

import argparse
import numpy as np
from kivy.lang.builder import Builder
from kivy.uix.pagelayout import PageLayout
from kivy.app import App
from kivy.clock import Clock

from kwidgets.text.quotationdisplay import QuotationDisplay
from datapanels.stockpanel import StockPanel

__default_string = """
<DataBuilder>:
    QuotationDisplay:
        update_sec: 5
        quotations: "Quote 1", "Quote 2", "Quote 3"
    StockPanel:
        ticker: 'MSFT'
    StockPanel:
        ticker: 'PSEC'
    StockPanel:
        ticker: 'DOCN'
"""


class DataBuilder(PageLayout):

    def rotate(self, dt):
        self.page = np.random.choice(len(self.children))

class DataPanelsApp(App):

    def build(self):
        container = DataBuilder()
        Clock.schedule_interval(container.rotate, 10.0)
        return container


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start DataPanels")
    parser.add_argument('--builder_path', default=None, required=False, type=str, help='Path to file with builder string')
    parser.add_argument("--transition-sec", default=60*10, required=False, type=int, help='Time between transitions in seconds')
    args = parser.parse_args()
    Builder.load_string(__default_string if args.builder_path is None else args.builder_path)
    DataPanelsApp().run()