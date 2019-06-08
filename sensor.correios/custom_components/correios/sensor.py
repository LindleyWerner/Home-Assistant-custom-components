"""Sensor for Correios packages."""
import logging
import requests
from datetime import timedelta
import voluptuous as vol
import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (CONF_NAME, CONF_SCAN_INTERVAL)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'correios'
ICON = 'mdi:package-variant-closed'
CONF_CODE = 'code'
BASE_URL = 'https://linketrack.com/{}/json'

STATE_NOT_FOUND = 'sem_status'
STATE_ERROR = 'erro'
STATE_DELIVERED = 'entregue'
STATE_DELIVERING = 'saindo_entrega'
STATE_FAIL_DELIVER = 'entrega_falhou'
STATE_POSTED = 'postado'
STATE_DELIVER_ATTEMPT = 'tentativa_entrega'
STATE_WAITING = 'esperando_retirada'
STATE_ON_THE_WAY = 'a_caminho'

STATUS_DELIVERED = 'Objeto entregue'
STATUS_DELIVERING = 'Objeto saiu para entrega'
STATUS_FAIL_DELIVER = 'A entrega não pode ser efetuada'
STATUS_POSTED = 'Objeto postado'
STATUS_DELIVER_ATTEMPT = 'Tentativa de entrega'
STATUS_WAITING = 'Objeto aguardando retirada'

CORREIOS_AMOUNT = 'quantidade'
CORREIOS_EVENTS = 'eventos'
CORREIOS_DATE = 'data'
CORREIOS_TIME = 'hora'
CORREIOS_LOCAL = 'local'
CORREIOS_STATUS = 'status'
CORREIOS_SUB_STATUS = 'subStatus'
CORREIOS_SUB_STATUS_1_INDEX = 0
CORREIOS_SUB_STATUS_2_INDEX = 1

ATTR_STATUS = 'status'
ATTR_DATE = 'date'
ATTR_TIME = 'time'
ATTR_LOCAL = 'local'
ATTR_SUB_STATUS_1 = 'info_1'
ATTR_SUB_STATUS_2 = 'info_2'

SCAN_INTERVAL = timedelta(seconds=1800)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_CODE): cv.string,
    vol.Optional(CONF_NAME, default=DOMAIN): cv.string,
    vol.Optional(CONF_SCAN_INTERVAL, default=SCAN_INTERVAL): cv.time_period,
})

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Correios platform."""
    add_entities([CorreiosSensor(
        config.get(CONF_CODE),
        config.get(CONF_NAME),
        config.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
    )], True)

class CorreiosSensor(Entity):
    """Sensor Correios."""

    def __init__(self, code, name, interval):
        """Initialize the sensor."""
        self._code = code
        self._name = name
        self._state = None
        self._date = None
        self._time = None
        self._local = None
        self._status = None
        self._sub_status_1 = None
        self._sub_status_2 = None
        self.update = Throttle(interval)(self.update)

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Icon to use in the frontend."""
        return ICON

    @property
    def device_state_attributes(self):
        """Return the device state attributes."""
        return {
            CONF_CODE: self._code,
            ATTR_STATUS: self._status,
            ATTR_DATE: self._date,
            ATTR_TIME: self._time,
            ATTR_LOCAL: self._local,
            ATTR_SUB_STATUS_1: self._sub_status_1,
            ATTR_SUB_STATUS_2: self._sub_status_2
        }

    def update(self):
        """Update sensor."""
        try:
            url = BASE_URL.format(self._code)
            response = requests.get(url).json()
            events = response[CORREIOS_EVENTS]
            if response[CORREIOS_AMOUNT] == 0:
                self._state = STATE_NOT_FOUND
            else:
                first_event = events[0]
                status = first_event[CORREIOS_STATUS]
                self._state = set_state(status)
                self._status = status
                self._date = first_event[CORREIOS_DATE]
                self._time = first_event[CORREIOS_TIME]
                self._local = first_event[CORREIOS_LOCAL]
                sub_status = first_event[CORREIOS_SUB_STATUS]
                if (sub_status):
                    self._sub_status_1 = sub_status[CORREIOS_SUB_STATUS_1_INDEX]
                    self._sub_status_2 = sub_status[CORREIOS_SUB_STATUS_2_INDEX]
        except Exception as error:
            self._state = STATE_ERROR
            _LOGGER.debug('%s - Could not update - %s', self._name, error)

def set_state(status):
    if STATUS_DELIVERED in status:
        return STATE_DELIVERED
    elif STATUS_DELIVERING in status:
        return STATE_DELIVERING
    elif STATUS_DELIVER_ATTEMPT in status:
        return STATE_DELIVER_ATTEMPT
    elif STATUS_FAIL_DELIVER in status:
        return STATE_FAIL_DELIVER
    elif STATUS_POSTED in status:
        return STATE_POSTED
    elif STATUS_WAITING in status:
        return STATE_WAITING
    else:
        return STATE_ON_THE_WAY
