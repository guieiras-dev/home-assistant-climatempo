import requests
from datetime import (datetime, timedelta)
from logging import getLogger
from homeassistant.util import Throttle
from homeassistant.const import HTTP_OK

_LOGGER = getLogger(__name__)

CONF_ATTRIBUTION = 'Dados de Climatempo'
CONF_API_KEY = 'api_key'
CONF_LOCALE = 'locale'

class Climatempo:
    """Fetch data from Climatempo API"""
    WEATHER_API_URL = 'http://apiadvisor.climatempo.com.br/api/v1/weather/locale/{}/current'
    FORECAST_API_URL = 'http://apiadvisor.climatempo.com.br/api/v1/forecast/locale/{}/days/15'

    def __init__(self, token, locale):
        """Initialize the data object."""
        self._token = token
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
            "temperature": weather["temperature"],
            "pressure": weather["pressure"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_velocity"],
            "wind_bearing": weather["wind_direction"],
            "forecast": list(map(self.serialize_forecast, forecast))
        }

    def get_data(self, variable):
        """Get the data."""
        return self.data.get(variable)

    def serialize_forecast(self, forecast):
        return {
            "datetime": forecast["date"],
            "temperature": forecast["temperature"]["max"],
            "condition": '',
            "templow": forecast["temperature"]["min"],
            "precipitation": forecast["rain"]["precipitation"],
            "precipitation_probability": forecast["rain"]["precipitation"],
            "wind_bearing": forecast["wind"]["direction"],
            "wind_speed": forecast["wind"]["velocity_avg"],
        }
