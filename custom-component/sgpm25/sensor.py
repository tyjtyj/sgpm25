import logging
import json
from datetime import timedelta, datetime
from requests import Session
from requests.auth import HTTPBasicAuth, HTTPDigestAuth
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
#from homeassistant.components.rest.sensor import RestData

#from homeassistant.custom_componets.sgnea.sensor import NEARestData
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
DEFAULT_TIMEOUT = 10
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
    verify_ssl = True
					 
    area = config.get(CONF_AREA)

    resourcenow = resource + datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    auth = None
    rest = NEARestData(method, resourcenow, auth, headers, payload, verify_ssl)
    
    rest.update()

    if rest.data is None:
        raise PlatformNotReady

    add_entities([NeaSensorPM25(name, resource, headers, area, verify_ssl)], True)       

class NeaSensorPM25(Entity):
    """Representation of a web scrape sensor."""

    def __init__(self, name, resource, headers, area, verify_ssl):
        """Initialize a web scrape sensor."""
        self._name = name
        self._area = area
        self._resource = resource
        self._headers = headers
        self._state = STATE_UNKNOWN
        self._unit_of_measurement = 'PM2.5'
        self._verify_ssl = verify_ssl

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
        rest = NEARestData('GET', resourcenow, None, self._headers, None, self._verify_ssl)
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

class NEARestData:
    """Class for handling the data retrieval."""

    def __init__(
        self, method, resource, auth, headers, data, verify_ssl, timeout=DEFAULT_TIMEOUT
    ):
        """Initialize the data object."""
        self._method = method
        self._resource = resource
        self._auth = auth
        self._headers = headers
        self._request_data = data
        self._verify_ssl = verify_ssl
        self._timeout = timeout
        self._http_session = Session()
        self.data = None
        self.headers = None

    def __del__(self):
        """Destroy the http session on destroy."""
        self._http_session.close()

    def set_url(self, url):
        """Set url."""
        self._resource = url

    def update(self):
        """Get the latest data from REST service with provided method."""
        _LOGGER.debug("Updating from %s", self._resource)
        try:
            response = self._http_session.request(
                self._method,
                self._resource,
                headers=self._headers,
                auth=self._auth,
                data=self._request_data,
                timeout=self._timeout,
                verify=self._verify_ssl,
            )
            self.data = response.text
            self.headers = response.headers
        except requests.exceptions.RequestException as ex:
            _LOGGER.error("Error fetching data: %s failed with %s", self._resource, ex)
            self.data = None
            self.headers = None
