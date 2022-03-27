from typing import Optional, Tuple
import os
from datetime import datetime
from tokenize import String
from pyowm import OWM
from pyowm.weatherapi25.one_call import OneCall
from kivy_garden.graph import Graph, MeshLinePlot, ScatterPlot
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.utils import get_color_from_hex as rgb
from kivy.properties import NumericProperty, StringProperty, DictProperty, ListProperty
from kwidgets.text.simpletable import SimpleTable

Builder.load_string('''
<WeatherPanel>:
    orientation: 'vertical'
    canvas.before:
        Color: 
            rgba: root.bg_color
        Rectangle:
            pos: self.pos
            size: self.size
    BoxLayout:
        orientation: 'horizontal'
        size_hint_y: None
        size: 0,275
        BoxLayout:
            orientation: 'vertical'
            Spinner:
                id: selected_location
                size_hint: 1, None
                height: 50
                text: 'Loading'
                markup: True
                values: []
                on_text:
                    root.update_panel()
            Image:
                id: current_image
                source: root.current_image
        SimpleTable:
            id: current
            key_size_hint_x: .4
            data: root.table_data
            key_color: root.text_color
            value_color: root.text_color
    Graph:
        id: graph
        y_ticks_major: 5
        y_grid_label: True
        x_ticks_major: 60*60
        x_grid_label: True
        padding: 5
        precision: '%0.2f'
        tick_color: root.text_color
        border_color: root.text_color
        label_options: {'color': root.text_color}
''')

class WeatherResponse:
    lat_lon: Tuple[float, float]
    location_name: str = None
    last_update: Optional[datetime] = None
    response: Optional[OneCall] = None

    def __init__(self, lat_lon: Tuple[float, float], location_name: Optional[datetime]) -> None:
        self.lat_lon = lat_lon
        self.location_name = location_name if location_name is not None else str(lat_lon)

class WeatherPanel(BoxLayout):
    data_update_rate_sec = NumericProperty(60*5)

    responses = ListProperty([WeatherResponse((51.4778, -0.0014), "Royal Observatory")])

    owm_key = StringProperty(None)
    temp_units = StringProperty("fahrenheit")
    text_color = ListProperty([0,0,0,1])
    bg_color = ListProperty([.5, .5, .5, 1])
    table_data = DictProperty({"sunrise": "Unknown", "sunset": "Unknown"})
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
        
        for wr in self.responses:
            if wr.location_name not in self.ids.selected_location.values:
                self.ids.selected_location.values = self.ids.selected_location.values + [wr.location_name]
            owm = OWM(self.owm_key)
            mgr = owm.weather_manager()
            ans = mgr.one_call(lat=wr.lat_lon[0], lon=wr.lat_lon[1])
            wr.response = ans
            wr.last_update = datetime.now()

    
    def update_panel(self, *args):
        ans = [r for r in self.responses if r.location_name==self.ids.selected_location.text][0].response
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
        self.table_data = data
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        self.current_image = os.path.join(icon_path, ans.current.weather_icon_name+".png")

        temps = [(m.reference_time(), m.temperature(self.temp_units)["temp"]) for m in ans.forecast_hourly]
        max_temp = max([x[1] for x in temps])
        min_temp = min([x[1] for x in temps])

        for p in list(self.ids.graph.plots):
            self.ids.graph.remove_plot(p)

        self.ids.graph.xmin=temps[0][0]-60*60
        self.ids.graph.xmax=temps[-1][0]+60*60
        self.ids.graph.ymin=min_temp - (max_temp-min_temp)*.05
        self.ids.graph.ymax=max_temp + (max_temp-min_temp)*.05
        plot = MeshLinePlot(color=self.text_color)
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