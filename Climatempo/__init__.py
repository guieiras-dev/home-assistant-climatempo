import requests
from datetime import (datetime, timedelta)
from logging import getLogger
from homeassistant.util import Throttle
from homeassistant.components.weather import (
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_WIND_SPEED,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_FORECAST,
    ATTR_FORECAST_TIME,
    ATTR_FORECAST_TEMP,
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_WIND_BEARING,
    ATTR_FORECAST_WIND_SPEED
)

from homeassistant.const import HTTP_OK

_LOGGER = getLogger(__name__)

CONF_ATTRIBUTION = 'Dados de Climatempo'
CONF_API_KEY = 'api_key'
CONF_LOCALE = 'locale'

class Climatempo:
    """Fetch data from Climatempo API"""
    WEATHER_API_URL = 'http://apiadvisor.climatempo.com.br/api/v1/weather/locale/{}/current'
    FORECAST_API_URL = 'http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{}/days/15'

    def __init__(self, api_key, locale):
        """Initialize the data object."""
        self._token = api_key
        self._locale = locale
        self.data = {}
        self._last_updated_at = datetime(2000, 1, 1, 0, 0)

    @Throttle(timedelta(minutes=20))
    def update(self):
        """Fetch data for sensor and weather"""
        params = {'token': self._token}
        response = requests.get(self.WEATHER_API_URL.format(self._locale), params=params)
        forecast_response = None

        if response.status_code != HTTP_OK:
            _LOGGER.error("Invalid response: %s", response.status_code)
            return

        if (datetime.now() - self._last_updated_at).days > 0:
            forecast_response = requests.get(self.FORECAST_API_URL.format(self._locale), params=params)
            if forecast_response.status_code == HTTP_OK:
                self._last_updated_at = datetime.now()

        self.set_data(response.json()["data"], None if forecast_response is None else forecast_response.json()["data"])

    def set_data(self, weather, forecast):
        """Set data using the last record from API."""
        self.data = {
            ATTR_FORECAST_CONDITION: self._get_condition(weather["icon"]),
            ATTR_WEATHER_TEMPERATURE: weather["temperature"],
            ATTR_WEATHER_PRESSURE: weather["pressure"],
            ATTR_WEATHER_HUMIDITY: weather["humidity"],
            ATTR_WEATHER_WIND_SPEED: weather["wind_velocity"],
            ATTR_WEATHER_WIND_BEARING: weather["wind_direction"],
            ATTR_FORECAST: self.data[ATTR_FORECAST] if forecast is None else list(map(self.serialize_forecast, forecast))
        }

    def get_data(self, variable):
        """Get the data."""
        return self.data.get(variable)

    def serialize_forecast(self, forecast):
        return {
            ATTR_FORECAST_TIME: forecast["date"] + "T00:00:00-03:00",
            ATTR_FORECAST_TEMP: forecast["temperature"]["max"],
            ATTR_FORECAST_CONDITION: self._get_condition(forecast["text_icon"]["icon"]["day"]),
            ATTR_FORECAST_TEMP_LOW: forecast["temperature"]["min"],
            ATTR_FORECAST_PRECIPITATION: forecast["rain"]["precipitation"],
            ATTR_FORECAST_PRECIPITATION_PROBABILITY: forecast["rain"]["precipitation"],
            ATTR_FORECAST_WIND_BEARING: forecast["wind"]["direction"],
            ATTR_FORECAST_WIND_SPEED: forecast["wind"]["velocity_avg"],
        }

    def _get_condition(self, condition):
        return {
            '1': 'sunny',
            '1n': 'clear-night',
            '2': 'partlycloudy',
            '2n': 'partlycloudy',
            '2r': 'cloudy',
            '2rn': 'cloudy',
            '3': 'rainy',
            '3n': 'rainy',
            '3tm': 'cloudy',
            '4': 'rainy',
            '4n': 'rainy',
            '4r': 'pouring',
            '4rn': 'pouring',
            '4t': 'lightning-rainy',
            '4tn': 'lightning-rainy',
            '5': 'pouring',
            '5n': 'pouring',
            '6': 'lightning-rainy',
            '6n': 'lightning-rainy',
            '7': 'snowy',
            '7n': 'snowy',
            '8': 'snowy-rainy',
            '8n': 'snowy-rainy',
            '9': 'windy-variant',
            '9n': 'windy-variant'
        }[condition]
