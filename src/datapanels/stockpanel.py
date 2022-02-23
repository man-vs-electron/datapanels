""" Stock panel

Displays and updates information about various stocks with some interactive ability for a user to choose the stock
being displayed and to change the timeframe over which information is displayed.

Note that this panel is not intended to be used for professional investing.

"""
from typing import Iterable
from threading import Thread
from datetime import datetime
import numpy as np
import pandas as pd
import yfinance as yf
from time import sleep
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock, mainthread
from kivy.properties import StringProperty, NumericProperty, DictProperty
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.logger import Logger
from kwidgets.dataviz.boxplot import BoxPlot
from kwidgets.uix.radiobuttons import RadioButtons
from kwidgets.text.simpletable import SimpleTable
from kwidgets.text.labeledvalue import LabeledValue


Builder.load_string('''
<FullLabel@Label>:
    text_size: self.width-10, self.height-10
    halign: 'left'
    markup: True

<StockPanel>:
    orientation: 'vertical'
    canvas.before:
        Color: 
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'horizontal'
        BoxLayout:
            id: leftbox
            orientation: 'vertical'
            spacing: 10
            BoxLayout:
                size_hint: 1, None
                size: 0, 50
                orientation: 'horizontal'
                Spinner:
                    id: selected_ticker
                    size_hint: None, 1
                    size: 150, 0
                    text: 'Loading'
                    markup: True
                    values: []
                    on_text:
                        root.update_panel()
                Label:
                    id: shortName
                    halign: 'left'
                    valign: 'center'
                    text_size: self.width-20, self.height-20
                    text: "Loading"
                    markup: True
                Label:
                    id: last_update
                    halign: 'right'
                    valign: 'center'
                    text_size: self.width-20, self.height-20
                    text: ""
            BoxLayout:
                size_hint: 1, None
                size: 0, 180
                orientation: 'horizontal'
                SimpleTable:
                    size_hint_x: None
                    size: 300, 0
                    key_size_hint_x: .65
                    id: detailtable
                    itemformat: "%0.2f"
                    keys: "diff", "regularMarketPrice", "regularMarketPreviousClose", "regularMarketDayHigh", "regularMarketDayLow", "regularMarketVolume", "averageDailyVolume10Day"
                    displaykeys: "Change", "Market Price", "Previous Close", "Day High", "Day Low", "Volume", "Avg 10 Day Volume"
                Label:
                    id: company_description
                    halign: 'left'
                    valign: 'top'
                    text: "loading"
                    text_size: self.width-20, self.height-20
            Graph:
                id: graph
                #xlabel: 'time'
                #ylabel: 'close'
            
        BoxLayout:
            orientation: 'vertical'
            size_hint: None, 1
            size: 150, root.height
            BoxPlot:
                id: boxplot
                markercolor: 1, 0, 0, 1
            SimpleTable:
                size_hint: 1, None
                size: 150, 150
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
        on_selected_value: root.draw_graph()
''')

_pandas_offsets = {
    "1 Month": pd.DateOffset(months=1),
    "3 Months": pd.DateOffset(months=3),
    "1 Year": pd.DateOffset(months=12),
    "5 Years": pd.DateOffset(months=50)
}

class StockPanel(BoxLayout):
    """ The panel that displays stock information.

    Multiple stocks can be selected.  The panel will periodically change the stock being displayed.  The user can also
    click a dropdown menu and choose a stock of interest.  Uses yfinance for pulling stock info.

    Note that this panel is not intended to be used for professional investing.

    Key Properties:
    * data_update_rate_sec: how many seconds between updating the stock info
    * proxserver: if not None, a proxy server to use for talking to yfinance
    * ticker_change_rate_sec: how many seconds between changing the stock being shown
    * tickers: list of security ticker symbols to track

    """
    # Configuration Properties
    data_update_rate_sec = NumericProperty(60 * 10)
    proxyserver = StringProperty(None)
    ticker_change_rate_sec = NumericProperty(60)


    # Data Properties
    _tickersinfo = DictProperty({"MSFT":None})
    _timer: Thread = None
    _running = True

    # Panel Display Properties
    _history_df = None

    def draw_graph(self):
        """ Draws the linegraph and the boxplot for the specified security

        :return:
        """
        if self._history_df is None:
            Logger.info("Graph not yet loaded.")
        else:
            now = pd.to_datetime("now")
            earliest = now-_pandas_offsets[self.ids.timeframe.selected_value]
            df = self._history_df.query("@now>=index>=@earliest")
            closes = list(df.Close)
            for p in list(self.ids.graph.plots):
                self.ids.graph.remove_plot(p)
            self.ids.graph.xmin=0
            self.ids.graph.xmax=len(closes)
            self.ids.graph.ymin=min(closes)
            self.ids.graph.ymax=max(closes)
            plot = MeshLinePlot(color=[0, 1, 0, 1])
            plot.points = [(i,c) for i,c in enumerate(closes)]
            self.ids.graph.add_plot(plot)

            self.ids.boxplot.data = closes
            self.ids.boxplotdata.data = {
                "Max": self.ids.boxplot._bpd.max,
                "Q3": self.ids.boxplot._bpd.q3,
                "Median": self.ids.boxplot._bpd.median,
                "Q1": self.ids.boxplot._bpd.q1,
                "Min": self.ids.boxplot._bpd.min
            }

    @mainthread
    def _threadsafe_data_update(self, aticker, ticker_packet):
        """ Update some retrieved information

        Required because properties should only be changed on the main thread.
        :param aticker: a ticker symbol
        :param ticker_packet: Thge data associated with that ticker symbol
        :return:
        """
        self._tickersinfo[aticker] = ticker_packet
        if aticker not in self.ids.selected_ticker.values:
            self.ids.selected_ticker.values = self.ids.selected_ticker.values + [aticker]

    def update_data(self):
        """  For every ticker symbol being tracked, pull the latest data using yfinance.

        If an exception is thrown, sleep for ten seconds and try again.

        :return:
        """
        for aticker in self._tickersinfo.keys():
            succeeded = False
            while not succeeded:
                try:
                    Logger.info("StockPanel: Updating %s" % aticker)
                    t = yf.Ticker(aticker)
                    info = t.get_info(proxy=self.proxyserver)
                    if "regularMarketPrice" in info and "regularMarketPreviousClose" in info:
                        info["diff"] = info["regularMarketPrice"] - info["regularMarketPreviousClose"]
                    history_df = t.history(period="5y", proxy=self.proxyserver)
                    last_update = datetime.now()
                    self._threadsafe_data_update(aticker, [info, history_df, last_update])
                    succeeded = True
                    sleep(10)
                except Exception as e:
                    Logger.warning("StockPanel: Error updating %s... %s" % (aticker, str(e)))
                    sleep(10)

    def choose_new_ticker(self, *args):
        """ Randomly chooses a ticker symbol to display

        :param args:
        :return:
        """
        ready_keys = [k for k,v in self._tickersinfo.items() if v is not None]
        if len(ready_keys)>0:
            aticker = np.random.choice(ready_keys)
            Logger.info("StockPanel: Randomly chose %s" % aticker)
            self.ids.selected_ticker.text = aticker
            return True
        else:
            return False

    def update_panel(self, *args):
        """ Update the data shown on the panel.

        :param args: Unused
        :return:
        """
        aticker = self.ids.selected_ticker.text
        info, self._history_df, last_update = self._tickersinfo[aticker]
        self.ids.company_description.text = info["longBusinessSummary"] if "longBusinessSummary" in info else "No description"
        self.ids.shortName.text = info["shortName"]
        self.ids.detailtable.data = info
        self.draw_graph()
        self.ids.boxplot.markervalue = info.get("regularMarketPrice", np.nan)
        self.ids.last_update.text = last_update.strftime("Last Update: %m/%d/%Y %H:%M:%S")

    def _update_data_loop(self):
        """ Update loop.  This is run on a separate thread.

        The data_udpate_rate_sec is the number of seconds after the last successful update that the next update takes
        place.

        :return:
        """
        while self._running:
            self.update_data()
            Logger.info("StockPanel: Data Updated. Refreshing in %d seconds." % self.data_update_rate_sec)
            sleep(self.data_update_rate_sec)

    def _display_update_boot(self, *args):
        """ Start the ticker update loop.

        It issues a series of one-time checks (10 seconds apart) until some ticker is available.

        :param args:
        :return:
        """
        if not self.choose_new_ticker():
            Clock.schedule_once(self._display_update_boot, 10)
        else:
            Clock.schedule_interval(self.choose_new_ticker, self.ticker_change_rate_sec)

    @property
    def tickers(self):
        """ The tickers to display

        :return:
        """
        return list(self._tickersinfo.keys())

    @tickers.setter
    def tickers(self, tickers: Iterable[str]):
        """ The tickers to display

        :param tickers: List of ticker symbols.
        :return:
        """
        self._tickersinfo = {t:None for t in tickers}
        self._timer = Thread(target=self._update_data_loop, daemon=True)
        self._timer.start()
        Clock.schedule_once(self._display_update_boot, 10)


class StockPanelApp(App):

    def build(self):
        container = Builder.load_string('''
StockPanel:
    ticker_change_rate_sec: 10
    data_update_rate_sec: 60*20
    tickers: 'VTI', 'MSFT', 'PSEC', 'DOCN'
''')
        return container

if __name__ == "__main__":
    StockPanelApp().run()
