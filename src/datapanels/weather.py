import os
from datetime import datetime
from tokenize import String
from pyowm import OWM
from kivy_garden.graph import Graph, MeshLinePlot, ScatterPlot
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as rgb
from kivy.properties import NumericProperty, StringProperty, DictProperty
from kwidgets.text.simpletable import SimpleTable

Builder.load_string('''
<WeatherPanel>:
    orientation: 'vertical'
    canvas.before:
        Color: 
            rgba: 0, 0, 0, 1
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        size: 0,275
        Image:
            id: current_image
            source: root.current_image
        SimpleTable:
            id: current
            key_size_hint_x: .4
            data: root.thedata
    Graph:
        id: graph
        y_ticks_major: 5
        y_grid_label: True
        x_ticks_major: 60*60
        x_grid_label: True
        padding: 5
        precision: '%0.2f'
''')

class WeatherPanel(BoxLayout):
    data_update_rate_sec = NumericProperty(60*5)
    location_name = StringProperty(None)
    owm_key = StringProperty(None)
    lat = NumericProperty(51.4778)
    lon = NumericProperty(-0.0014)
    temp_units = StringProperty("fahrenheit")
    thedata = DictProperty({"sunrise": "Unknown", "sunset": "Unknown"})
    current_image = StringProperty(None)
    started = False

    def update_initialize(self):
        self.update_data()
        if not self.started:
            self.started=True
            Clock.schedule_interval(self.update_data, self.data_update_rate_sec)


    def dp_start(self):
        self.update_initialize()

    def update_data(self, *args):
        
        if self.owm_key is None:
            self.owm_key = os.environ.get("OWM_KEY")
        if self.owm_key is None:
            raise RuntimeError("OpenWeathermap Key not set")
        owm = OWM(self.owm_key)
        mgr = owm.weather_manager()
        ans = mgr.one_call(lat=self.lat, lon=self.lon)
        data = {
            'Location': self.location_name if self.location_name else ("Lat: %f, Lon: %f" % (self.lat, self.lon)),
            'As of': datetime.fromtimestamp(ans.current.reference_time()).strftime("%H:%M:%S"),
            'Sunrise': datetime.fromtimestamp(ans.current.sunrise_time()).strftime("%H:%M:%S"),
            'Sunset':  datetime.fromtimestamp(ans.current.sunset_time()).strftime("%H:%M:%S"),
            'Detailed status': ans.current.detailed_status,
            'Temperature': ans.current.temperature(self.temp_units)["temp"],
            'Feels like': ans.current.temperature(self.temp_units)["feels_like"],
            'Wind speed': ans.current.wind()["speed"],
            'Wind direction': ans.current.wind()["deg"],
            'UVI': ans.current.uvi
        }
        self.thedata = data
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        self.current_image = os.path.join(icon_path, ans.current.weather_icon_name+".png")

        temps = [(m.reference_time(), m.temperature(self.temp_units)["temp"]) for m in ans.forecast_hourly]
        max_temp = max([x[1] for x in temps])
        min_temp = min([x[1] for x in temps])

        self.ids.graph.xmin=temps[0][0]-60*60
        self.ids.graph.xmax=temps[-1][0]+60*60
        self.ids.graph.ymin=min_temp - (max_temp-min_temp)*.05
        self.ids.graph.ymax=max_temp + (max_temp-min_temp)*.05
        plot = MeshLinePlot(color=[0.7, 0.7, 0.7, 1])
        plot.points = [(i,c) for i,c in temps]
        self.ids.graph.add_plot(plot)

        mean_temp = (min_temp+max_temp)/2.
        hasrain = [(m.reference_time(), ('1h' in m.rain) or ('1h' in m.snow)) for m in ans.forecast_hourly]
        rainpoints = [(i,mean_temp) for i,r in hasrain if r]
        if len(rainpoints)>0:
            rainplot = ScatterPlot(color=[0.2, 0.2, 1, 1], point_size=5)
            rainplot.points = rainpoints
            self.ids.graph.add_plot(rainplot)

        
        

class WeatherPanelApp(App):
    def build(self):
        container = Builder.load_string('''
WeatherPanel:
    lat: 51.4778
    lon: -0.0014
    location_name: 'Royal Observatory'
''')

        container.update_initialize()
        return container

if __name__ == "__main__":
    WeatherPanelApp().run()