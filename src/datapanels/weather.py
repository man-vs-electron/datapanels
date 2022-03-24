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
<Weather>:
    orientation: 'vertical'
    SimpleTable:
        size_hint_x: 1
        size_hint_y: 1
        id: current
        keys: 'sunrise', 'sunset'
        data: root.thedata
''')

class WeatherPanel(BoxLayout):
    data_update_rate_sec = NumericProperty(60*5)
    owm_key = StringProperty(None)
    lat = NumericProperty(51.4778)
    lon = NumericProperty(-0.0014)
    thedata = DictProperty({"sunrise": "Unknown", "sunset": "Unknown"})
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
            'sunrise': datetime.fromtimestamp(ans.current.sunrise_time()).strftime("%H:%M:%S"),
            'sunset':  datetime.fromtimestamp(ans.current.sunset_time()).strftime("%H:%M:%S")
        }
        self.thedata = data

        
        

class WeatherPanelApp(App):
    def build(self):
        container = Builder.load_string('''
WeatherPanel:
''')

        container.update_initialize()
        return container

if __name__ == "__main__":
    WeatherPanelApp().run()