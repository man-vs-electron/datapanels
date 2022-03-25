import os
from datetime import datetime
from pyowm import OWM
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang.builder import Builder
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, DictProperty
from kwidgets.text.simpletable import SimpleTable

Builder.load_string('''
<WeatherPanel>:
    orientation: 'vertical'
    BoxLayout:
        orientation: 'horizontal'
        Image:
            id: current_image
            source: root.current_image
        SimpleTable:
            id: current
            data: root.thedata
''')

class WeatherPanel(BoxLayout):
    data_update_rate_sec = NumericProperty(60*5)
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
            'As of': datetime.fromtimestamp(ans.current.reference_time()).strftime("%H:%M:%S"),
            'Sunrise': datetime.fromtimestamp(ans.current.sunrise_time()).strftime("%H:%M:%S"),
            'Sunset':  datetime.fromtimestamp(ans.current.sunset_time()).strftime("%H:%M:%S"),
            'Detailed status': ans.current.detailed_status,
            'Temperature': ans.current.temperature(self.temp_units)["temp"],
            'Feels like': ans.current.temperature(self.temp_units)["feels_like"],
            'Wind speed': ans.current.wind()["speed"],
            'Wind direction': ans.current.wind()["deg"]
        }
        self.thedata = data
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
        self.current_image = os.path.join(icon_path, ans.current.weather_icon_name+".png")

        
        

class WeatherPanelApp(App):
    def build(self):
        container = Builder.load_string('''
WeatherPanel:
''')

        container.update_initialize()
        return container

if __name__ == "__main__":
    WeatherPanelApp().run()