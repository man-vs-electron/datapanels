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
from kwidgets.uix.radiobuttons import RadioButtons
from kivy_garden.graph import Graph, MeshLinePlot



Builder.load_string('''
<StockPanel>:
    _boxplot: boxplot
    _graph: graph
    _timeframe: timeframe
    orientation: 'horizontal'
    BoxLayout:
        id: leftbox
        orientation: 'vertical'
        spacing: 10
        Label:
            size_hint_y: .25
            halign: 'left'
            valign: 'top'
            text_size: self.width-20, self.height-20
            text: '[b][size=20]'+root._ticker+'[/size][/b]'
            markup: True
        Label:
            size_hint_y: .25
            halign: 'left'
            text: root._ask
        RadioButtons:
            id: timeframe
            size: leftbox.width, 30
            size_hint: None, None
            options: ["Month", "Year", "All"]
            on_selected_value: root._timeframe_clicked(args[1])
        Graph:
            size_hint_y: .5
            id: graph
            xlabel: 'time'
            ylabel: 'close'
            
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: .2
        BoxPlot:
            id: boxplot
            markercolor: 1, 0, 0, 1
        Label:
            size_hint_y: .25
            halign: 'left'
            text: root._max
''')


class StockPanel(BoxLayout):
    _period = StringProperty("1y")
    _ticker = StringProperty("Loading...")
    _ask = StringProperty("N/A")
    _max = StringProperty("")
    _3Q = StringProperty("")
    _med = StringProperty("")
    _1Q = StringProperty("")
    _min = StringProperty("")
    _timer: Thread = None
    _running = True
    _update_rate_sec = NumericProperty(60*10)
    _boxplot = ObjectProperty(None)
    _graph = ObjectProperty(None)
    _timeframe = ObjectProperty(None)

    def update_data(self):
        #try:
        t = yf.Ticker(self._ticker)
        info = t.info
        self._ask = str(info["ask"])
        df = t.history(period=self._period)
        closes = list(df.Close)
        self._boxplot.data = closes
        self._max = "Max: %0.2f\n3Q: %0.2f\nMed: %0.2f\n1Q: %0.2f\nMin: %0.2f" % \
                    (self._boxplot._bpd.max,
                     self._boxplot._bpd.q3,
                     self._boxplot._bpd.median,
                     self._boxplot._bpd.q1,
                     self._boxplot._bpd.min)
        self._boxplot.markervalue = self._ask

        for p in list(self._graph.plots):
            self._graph.remove_plot(p)
        self._graph.xmin=0
        self._graph.xmax=len(closes)
        self._graph.ymin=min(closes)
        self._graph.ymax=max(closes)
        plot = MeshLinePlot(color=[0, 1, 0, 1])
        plot.points = [(i,c) for i,c in enumerate(closes)]
        self._graph.add_plot(plot)

        return True
        #except:
        #    print("Error updating %s..." % self._ticker)
        #    return False


    def _update_now(self):
        Thread(target=self.update_data, daemon=True).start()

    def _update_data_loop(self):
        while self._running:
            while not self.update_data():
                sleep(10)
            sleep(self._update_rate_sec)

    def _timeframe_clicked(self, newperiod):
        print(newperiod)

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
    size_hint_y: 1
    ticker: 'PSEC'
    update_rate_sec: 60*10
''')
        return container

if __name__ == "__main__":
    StockPanelApp().run()