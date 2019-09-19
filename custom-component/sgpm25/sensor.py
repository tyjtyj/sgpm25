import logging
import json
from datetime import timedelta, datetime


import voluptuous as vol
													   


from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.components.rest.sensor import RestData

from homeassistant.const import (
    CONF_NAME, CONF_RESOURCE, STATE_UNKNOWN)
																	  
																  
							   
from homeassistant.helpers.entity import Entity
from homeassistant.exceptions import PlatformNotReady
import homeassistant.helpers.config_validation as cv

										

_LOGGER = logging.getLogger(__name__)

CONF_AREA = 'area'
DEFAULT_RESOURCE = 'https://api.data.gov.sg/v1/environment/pm25?date_time=' 
DEFAULT_NAME = 'SG 1Hour PM2.5'
SCAN_INTERVAL = timedelta(minutes=1800)
PARALLEL_UPDATES = 1

TIMEOUT = 10


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_AREA): cv.string,
    vol.Optional(CONF_RESOURCE, default=DEFAULT_RESOURCE): cv.string,

    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,

})

def setup_platform(hass, config, add_entities,
                               discovery_info=None):

    """Set up the Web scrape sensor."""
    _LOGGER.info('SGPM25 loaded')
    name = config.get(CONF_NAME)
    resource = config.get(CONF_RESOURCE)


    method = 'GET'
    payload = None
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36"}
    verify_ssl = 0
					 
    area = config.get(CONF_AREA)

    resourcenow = resource + datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    auth = None
    rest = RestData(method, resourcenow, auth, headers, payload, verify_ssl)
    
    rest.update()

    if rest.data is None:
        raise PlatformNotReady

    add_entities([NeaSensorPM25(name, resource, headers, area)], True)       

class NeaSensorPM25(Entity):
    """Representation of a web scrape sensor."""

    def __init__(self, name, resource, headers, area):
        """Initialize a web scrape sensor."""
        self._name = name
        self._area = area
        self._resource = resource
        self._headers = headers
        self._state = STATE_UNKNOWN
        self._unit_of_measurement = 'PM2.5'


    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property             
    def state(self):
        """Return the state of the device."""
        return self._state
		
    @property
    def unit_of_measurement(self):
        """Return the unit the value is expressed in."""
        return self._unit_of_measurement
		
    def update(self):
        """Get the latest data from the source and updates the state."""
        resourcenow = self._resource + datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        rest = RestData('GET', resourcenow, None, self._headers, None, 0)
        rest.update()
        try: 
            json_dict = json.loads(rest.data)
            forecasts = json_dict['items'][0]['readings']['pm25_one_hourly']
            if forecasts[self._area] is not None:
                value = int(forecasts[self._area])
            else:
                value = None
                _LOGGER.error("Unable to fetch data from %s", value)
                return False
        except (TimeoutError,KeyError):
            _LOGGER.error("Error. The data value is: %s", rest.data)
            return
        _LOGGER.debug("The data value is: %s", rest.data)

        self._state = value
