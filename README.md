# Denon RS-232 Receiver Integration for Home Assistant

This custom component allows you to control Denon AV receivers through an RS-232 serial connection in Home Assistant. It provides comprehensive control over basic receiver functions including power, volume, input selection, and multi-zone support.

## Features

- Power control (on/off)
- Volume control (up/down, set level, mute)
- Input source selection
- Zone 2 support
  - Power control
  - Volume control
  - Mute control
- Serial communication via RS-232

## Supported Input Sources

The following input sources are supported by default:
- CD
- DVD
- TV/CBL
- HDP
- DVR
- Video Aux

## Configuration

Download a zip file of the component from the repository and unzip it into the custom_components folder in your Home Assistant config directory.
Add the following to your Home Assistant configuration:

media_player:
  - platform: denon232
    serial_port: /dev/ttyUSB?
    name: DenonReceiver

 replace ? with the number of the usb serial device you are using.
