from typing import List, Union
from threading import Thread

import numpy as np
import pandas as pd
import yfinance as yf
from time import sleep
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kwidgets.dataviz.boxplot import BoxPlot
from kwidgets.uix.radiobuttons import RadioButtons
from kwidgets.uix.simpletable import SimpleTable
from kivy_garden.graph import Graph, MeshLinePlot



Builder.load_string('''
<FullLabel@Label>:
    text_size: self.width-10, self.height-10
    halign: 'left'
    markup: True

<StockPanel>:
    _boxplot: boxplot
    _graph: graph
    _timeframe: timeframe
    _boxplotdata: boxplotdata
    _detailtable: detailtable
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            id: leftbox
            orientation: 'vertical'
            spacing: 10
            Label:
                size_hint_y: .1
                halign: 'left'
                valign: 'top'
                text_size: self.width-20, self.height-20
                text: '[b][size=25]'+root._ticker+'[/size][/b]  '+root._shortName
                markup: True
            BoxLayout:
                size_hint_y: .4
                orientation: 'horizontal'
                SimpleTable:
                    size_hint_x: None
                    size: 300, 0
                    key_size_hint_x: .75
                    id: detailtable
                    itemformat: "%0.2f"
                    keys: "currentPrice", "revenuePerShare", "yield", "dividendRate", "priceToSalesTrailing12Months", "beta3Year", "grossMargins", "profitMargins"
                    displaykeys: "Current Price", "Revenue Per Share", "Yield", "Dividend Rate", "12 Month Price to Sales", "3 Year Beta", "Gross Margins", "Profit Margins"
                Label:
                    halign: 'left'
                    valign: 'top'
                    text: root._description
                    text_size: self.width-20, self.height-20
            Graph:
                size_hint_y: .5
                id: graph
                #xlabel: 'time'
                #ylabel: 'close'
            
        BoxLayout:
            orientation: 'vertical'
            size_hint: None, 1
            size: 200, root.height
            BoxPlot:
                id: boxplot
                markercolor: 1, 0, 0, 1
            SimpleTable:
                size_hint_y: .3
                id: boxplotdata
                itemformat: "%0.2f"
                box_color: 0, 1, 0, 1
    RadioButtons:
        id: timeframe
        size: root.width, 30
        size_hint: None, None
        options: "1 Month", "3 Months", "1 Year", "5 Years"
        selected_value: '1 Month'
        selected_color: .1, .5, .1, 1
        on_selected_value: root._timeframe_clicked(args[1])

''')

_pandas_offsets = {
    "1mo": pd.DateOffset(months=1),
    "3mo": pd.DateOffset(months=3),
    "1y": pd.DateOffset(months=12),
    "5y": pd.DateOffset(months=50)
}

class StockPanel(BoxLayout):
    _period = StringProperty("1mo")
    _ticker = StringProperty("Loading...")
    _description = StringProperty("")
    _shortName = StringProperty("")
    _timer: Thread = None
    _running = True
    _update_rate_sec = NumericProperty(60*10)
    _boxplot = ObjectProperty(None)
    _boxplotdata = ObjectProperty(None)
    _graph = ObjectProperty(None)
    _timeframe = ObjectProperty(None)
    _detailtable = ObjectProperty(None)
    _history_df = None

    def draw_graph(self):
        now = pd.to_datetime("now")
        earliest = now-_pandas_offsets[self._period]
        df = self._history_df.query("@now>=index>=@earliest")
        closes = list(df.Close)
        for p in list(self._graph.plots):
            self._graph.remove_plot(p)
        self._graph.xmin=0
        self._graph.xmax=len(closes)
        self._graph.ymin=min(closes)
        self._graph.ymax=max(closes)
        plot = MeshLinePlot(color=[0, 1, 0, 1])
        plot.points = [(i,c) for i,c in enumerate(closes)]
        self._graph.add_plot(plot)

        self._boxplot.data = closes
        self._boxplotdata.data = {
            "Max": self._boxplot._bpd.max,
            "Q3": self._boxplot._bpd.q3,
            "Median": self._boxplot._bpd.median,
            "Q1": self._boxplot._bpd.q1,
            "Min": self._boxplot._bpd.min
        }

    def update_data(self):
        try:
            t = yf.Ticker(self._ticker)
            info = t.info
            self._description = info["longBusinessSummary"] if "longBusinessSummary" in info else "No description"
            self._shortName = info["shortName"]
            self._history_df = t.history(period="5y")
            self._detailtable.data = info
            self.draw_graph()
            self._boxplot.markervalue = info.get("ask", np.nan)
            return True
        except:
            print("Error updating %s..." % self._ticker)
            return False


    def _update_now(self):
        Thread(target=self.update_data, daemon=True).start()

    def _update_data_loop(self):
        while self._running:
            while not self.update_data():
                sleep(10)
            sleep(self._update_rate_sec)

    def _timeframe_clicked(self, newperiod):
        if newperiod=="1 Month":
            self._period = "1mo"
        if newperiod=="3 Months":
            self._period = "3mo"
        if newperiod=="1 Year":
            self._period = "1y"
        if newperiod=="5 Years":
            self._period = "5y"
        self.draw_graph()

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