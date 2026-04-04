import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from tools.weather_tool import WeatherTool
wt = WeatherTool()
print(wt.get_weather("北京"))
