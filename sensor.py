"""Sensor platform for Bizi Zaragoza."""
import requests
import logging
from datetime import timedelta
from homeassistant.components.sensor import SensorEntity

_LOGGER = logging.getLogger(__name__)

API_INFO = "https://zaragoza.publicbikesystem.net/customer/gbfs/v2/en/station_information"
API_STATUS = "https://zaragoza.publicbikesystem.net/customer/gbfs/v2/en/station_status"

SCAN_INTERVAL = timedelta(minutes=1)


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Bizi Zaragoza sensor."""
    station_id = config.get("station_id")
    if station_id is None:
        _LOGGER.error("No se ha configurado 'station_id' en el sensor")
        return

    add_entities([
        BiziSensor(station_id, "bikes"),
        BiziSensor(station_id, "docks"),
    ], True)


class BiziSensor(SensorEntity):
    """Representation of a Bizi Zaragoza sensor."""

    def __init__(self, station_id, sensor_type):
        self._station_id = str(station_id)
        self._type = sensor_type
        self._attr_name = f"Bizi {station_id} {sensor_type}"
        self._attr_unique_id = f"bizi_{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = "bicis" if sensor_type == "bikes" else "huecos"
        self._state = None
        self._station_name = None

    def update(self):
        """Fetch data from API."""
        try:
            status = requests.get(API_STATUS, timeout=10).json()
            info = requests.get(API_INFO, timeout=10).json()

            stations_info = {s["station_id"]: s for s in info["data"]["stations"]}

            for st in status["data"]["stations"]:
                if st["station_id"] == self._station_id:
                    s_info = stations_info.get(self._station_id, {})
                    self._station_name = s_info.get("name", self._station_id)

                    if self._type == "bikes":
                        self._state = st["num_bikes_available"]
                    else:
                        self._state = st["num_docks_available"]
                    break

        except Exception as e:
            _LOGGER.error("Error consultando API Bizi Zaragoza: %s", e)
            self._state = None

    @property
    def native_value(self):
        return self._state

    @property
    def extra_state_attributes(self):
        return {"station_name": self._station_name}
