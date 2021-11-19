import argparse
from kivy.lang.builder import Builder
from kivy.uix.pagelayout import PageLayout
from kivy.app import App
from kivy.clock import Clock

from kwidgets.text.quotationdisplay import QuotationDisplay

__default_string = """
<DataBuilder>:
    QuotationDisplay:
        update_sec: 1
        quotations: "Quote 1", "Quote 2", "Quote 3"
    Button:
        text: 'page2'
    Button:
        text: 'page3'
"""


class DataBuilder(PageLayout):

    def rotate(self, dt):
        self.page = (self.page+1) % 3

class DataPanelsApp(App):

    def build(self):
        container = DataBuilder()
        Clock.schedule_interval(container.rotate, 1.0)
        return container


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start DataPanels")
    parser.add_argument('--builder_path', default=None, required=False, type=str, help='Path to file with builder string')
    args = parser.parse_args()
    if args.builder_path is None:
        Builder.load_string(__default_string)
    else:
        with open(__default_string) as f:
            Builder.load_string(f.read())

    DataPanelsApp().run()