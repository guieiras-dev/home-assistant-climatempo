"""
Weather support for Climatempo data service.
"""

DOMAIN='climatempo'

from logging import getLogger
import voluptuous as vol

_LOGGER = getLogger(__name__)

from homeassistant.components.weather import (
    ATTR_FORECAST,
    ATTR_FORECAST_CONDITION,
    ATTR_WEATHER_TEMPERATURE,
    ATTR_WEATHER_HUMIDITY,
    ATTR_WEATHER_PRESSURE,
    ATTR_WEATHER_WIND_BEARING,
    ATTR_WEATHER_WIND_SPEED,
    PLATFORM_SCHEMA,
    WeatherEntity
)

from homeassistant.const import (CONF_API_KEY, CONF_NAME, TEMP_CELSIUS)

import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity

from .Climatempo import (
    Climatempo,
    CONF_API_KEY,
    CONF_ATTRIBUTION,
    CONF_LOCALE
)

DEFAULT_NAME = 'weather'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_API_KEY): cv.string,
    vol.Required(CONF_LOCALE): cv.string,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the weather platform."""
    name = config.get(CONF_NAME)
    api_key = config.get(CONF_API_KEY)
    locale = config.get(CONF_LOCALE)

    climatempo = Climatempo(api_key=api_key, locale=locale)
    try:
        climatempo.update()
    except (ValueError, TypeError) as err:
        _LOGGER.error("Error fetching Climatempo API: %s", err)
        return False

    add_entities([ClimatempoWeather(climatempo, name)], True)


class ClimatempoWeather(WeatherEntity):
    """Weather condition representation"""

    def __init__(self, climatempo, name):
        """Initialize"""
        self._climatempo = climatempo
        self.entity_name = name

    @property
    def available(self):
        """Return if weather data is available."""
        return True

    @property
    def attribution(self):
        """Return the attribution."""
        return CONF_ATTRIBUTION

    @property
    def name(self):
        """Return entity name."""
        return self.entity_name

    @property
    def temperature(self):
        """Return temperature."""
        return self._climatempo.get_data(ATTR_WEATHER_TEMPERATURE)

    @property
    def temperature_unit(self):
        """Return tempearature measurement unit"""
        return TEMP_CELSIUS

    @property
    def humidity(self):
        """Return humidity"""
        return self._climatempo.get_data(ATTR_WEATHER_HUMIDITY)

    @property
    def wind_speed(self):
        """Return wind speed"""
        return self._climatempo.get_data(ATTR_WEATHER_WIND_SPEED)

    @property
    def wind_bearing(self):
        """Return wind bearing"""
        return self._climatempo.get_data(ATTR_WEATHER_WIND_BEARING)

    @property
    def ozone(self):
        """Return ozone level"""
        return None

    @property
    def pressure(self):
        """Return pressure"""
        return self._climatempo.get_data(ATTR_WEATHER_PRESSURE)

    @property
    def visibility(self):
        """Return visibility"""
        return None

    @property
    def condition(self):
        """Return weather condition"""
        return self._climatempo.get_data(ATTR_FORECAST_CONDITION)

    @property
    def forecast(self):
        """Return forecast array"""
        return self._climatempo.get_data(ATTR_FORECAST)

    def update(self):
        """Fetches latest data from Climatempo"""
        self._climatempo.update()
