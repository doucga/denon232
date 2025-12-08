"""Constants for the Denon AVR RS-232 integration."""

DOMAIN = "denon232"

# Configuration constants
CONF_SERIAL_PORT = "serial_port"
CONF_NAME = "name"

DEFAULT_NAME = "Denon Receiver"

# Input source mappings: friendly name -> protocol command
NORMAL_INPUTS = {
    "Phono": "PHONO",
    "CD": "CD",
    "Tuner": "TUNER",
    "DVD": "DVD",
    "HDP": "HDP",
    "TV": "TV",
    "SAT/CBL": "SAT/CBL",
    "VCR": "VCR",
    "DVR": "DVR",
    "V.AUX": "V.AUX",
    "Sirius": "SIRIUS",
    "iPod": "IPOD",
}

# Zone 2 input sources (TV and HDP not supported per AVR-2310 protocol)
ZONE2_INPUTS = {
    "Phono": "PHONO",
    "CD": "CD",
    "Tuner": "TUNER",
    "DVD": "DVD",
    "SAT/CBL": "SAT/CBL",
    "VCR": "VCR",
    "DVR": "DVR",
    "V.AUX": "V.AUX",
    "Sirius": "SIRIUS",
    "iPod": "IPOD",
}

