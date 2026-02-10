# Denon AVR RS-232 Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)

This custom integration allows you to control older Denon AV receivers through an RS-232 serial connection in Home Assistant. It provides comprehensive control over basic receiver functions including power, volume, input selection, and multi-zone support.

## Features

- **Main Zone Control**
  - Power on/off
  - Volume control (up/down, set level, mute)
  - Input source selection

- **Zone 2 Control**
  - Power on/off
  - Volume control (up/down, set level, mute)
  - Input source selection (limited sources - TV and HDP not supported per protocol)

- Serial communication via RS-232
- UI-based configuration (Config Flow)
- Two separate media player entities for Main Zone and Zone 2
- Half-dB volume precision support

## Supported Input Sources

### Main Zone
The following input sources are supported:
- Phono
- CD
- Tuner
- DVD
- HDP
- TV
- SAT/CBL
- VCR
- DVR
- V.AUX
- Sirius (North America models only)
- iPod

### Zone 2
Zone 2 supports all sources except **TV** and **HDP** (per AVR-2310 protocol specification).

## Installation

### HACS (Recommended)

1. Click on the '<> Code' button above
2. Click on the 'Copy URL to Clipboard' button
3. Open HACS in your Home Assistant instance
4. Click the three dots menu in the top right corner
5. Select "Custom repositories"
6. Paste the repository URL and select "Integration" as the category
7. Click "Add"
8. In HACS Search for "Denon AVR RS-232"
9. Click the three dots at the far right and click download
9. Restart Home Assistant

### Manual Installation

1. Download the latest release from the repository
2. Copy the `denon232` folder to your `custom_components` directory:
   ```
   custom_components/
   └── denon232/
       ├── __init__.py
       ├── config_flow.py
       ├── const.py
       ├── denon232_receiver.py
       ├── manifest.json
       ├── media_player.py
       ├── strings.json
       └── translations/
           └── en.json
   ```
3. Restart Home Assistant

## Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **+ Add Integration**
3. Search for "Denon AVR RS-232"
4. Enter a name for your receiver and the serial port path:
   - Linux: `/dev/ttyUSB0` (or similar)
   - Windows: `COM3` (or similar)
5. Click **Submit**

Two media player entities will be created:
- `media_player.<name>_main_zone` - Controls the main zone
- `media_player.<name>_zone_2` - Controls Zone 2

## Hardware Requirements

- Denon AVR with RS-232 serial port
- USB-to-Serial adapter (if your computer doesn't have a serial port)
- Null modem cable or appropriate RS-232 cable

## Troubleshooting

### Serial Port Permissions (Linux)

If you're running Home Assistant on Linux and encounter permission errors, you may need to add the Home Assistant user to the `dialout` group:

```bash
sudo usermod -a -G dialout homeassistant
```

Then restart Home Assistant.

### Finding the Serial Port

**Linux:**
```bash
ls /dev/ttyUSB*
# or
ls /dev/ttyACM*
```

**Windows:**
Check Device Manager under "Ports (COM & LPT)"

## Support

If you encounter issues, please open an issue on the GitHub repository with:
- Home Assistant version
- Integration version
- Denon receiver model
- Error logs from Home Assistant

## License

This project is licensed under the MIT License.

If you found this integration useful you can buy me a coffee.

<script type="text/javascript" src="https://cdnjs.buymeacoffee.com/1.0.0/button.prod.min.js" data-name="bmc-button" data-slug="doucga" data-color="#FFDD00" data-emoji=""  data-font="Cookie" data-text="Buy me a coffee" data-outline-color="#000000" data-font-color="#000000" data-coffee-color="#ffffff" ></script>