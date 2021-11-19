from typing import List, Union
from threading import Thread
import yfinance as yf
from time import sleep
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kwidgets.dataviz.boxplot import BoxPlot


Builder.load_string('''
<StockPanel>:
    _boxplot: boxplot
    orientation: 'horizontal'
    BoxLayout:
        orientation: 'vertical'
        Label:
            halign: 'left'
            text: root._ticker
        Label:
            halign: 'left'
            text: root._ask
        Button:
            text: 'bottom'
    BoxPlot:
        id: boxplot
        size_hint_x: .2
        markercolor: 1, 0, 0, 1
''')

class StockPanel(BoxLayout):
    _period = StringProperty("5cd y")
    _ticker = StringProperty("Loading...")
    _ask = StringProperty("N/A")
    _timer: Thread = None
    _running = True
    _update_rate_sec = NumericProperty(60*10)
    _boxplot = ObjectProperty(None)

    def update_data(self):
        try:
            t = yf.Ticker(self._ticker)
            info = t.info
            self._ask = str(info["ask"])
            df = t.history(period=self._period)
            closes = list(df.Close)
            self._boxplot.data = closes
            self._boxplot.markervalue = self._ask
            return True
        except:
            print("Error updating %s..." % self._ticker)
            return False


    def _update_data_loop(self):
        while self._running:
            while not self.update_data():
                sleep(10)
            sleep(self._update_rate_sec)

    @property
    def ticker(self):
        return self._ticker

    @ticker.setter
    def ticker(self, ticker: str):
        self._ticker = ticker
        self._timer = Thread(target=self._update_data_loop, daemon=True)
        self._timer.start()

    @property
    def update_rate_sec(self):
        return self._update_rate_sec

    @update_rate_sec.setter
    def update_rate_sec(self, rate: int):
        self._update_rate_sec = rate

class StockPanelApp(App):

    def build(self):
        container = Builder.load_string('''
StockPanel:
    ticker: 'LUV'
    update_rate_sec: 60*10
''')
        return container

if __name__ == "__main__":
    StockPanelApp().run()