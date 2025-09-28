# R4DCB08 Temperature Collector Python Interface

A Python library and command-line interface for communicating with R4DCB08 8-channel temperature collectors using Modbus RTU protocol.

## Features

- Read temperatures from all 8 channels
- Read temperature from individual channels  
- Set temperature correction values for calibration
- Read current temperature corrections
- Command-line interface for easy automation
- Simple Python API for integration

## R4DCB08 Technical Specifications

| Feature | Details |
|---------|---------|
| **Operating Voltage** | 6-24V DC |
| **Operating Current** | 8-13mA (depends on connected DS18B20 sensors) |
| **Temperature Range** | -55°C to +125°C |
| **Accuracy** | ±0.5°C from -10°C to +85°C |
| **Baud Rates** | 1200, 2400, 4800, 9600 (default), 19200 |
| **Data Format** | N, 8, 1 (No parity, 8 data bits, 1 stop bit) |
| **Communication Protocol** | Modbus RTU |
| **Temperature Channels** | 8 channels (DS18B20 sensors) |
| **Default Address** | 1 |

## Installation

1. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirement.txt
```

### Required Packages
```
pyserial
pymodbus
```

## Usage

### Command Line Interface

The `r4dcb08_cli.py` script provides a complete command-line interface:

#### Basic Usage
```bash
python r4dcb08_cli.py [OPTIONS] COMMAND
```

#### Connection Options
- `--port, -p`: Serial port (required, e.g., `/dev/ttyUSB0`, `COM3`)
- `--address, -a`: Modbus device address (1-247, default: 1)
- `--baudrate, -b`: Baud rate (1200, 2400, 4800, 9600, 19200, default: 9600)
- `--timeout, -t`: Communication timeout in seconds (default: 1.0)

#### Available Commands

##### 1. Read All Temperatures
Read temperatures from all 8 channels:
```bash
python r4dcb08_cli.py --port /dev/ttyUSB0 --address 1 read-all
```

Output:
```
R4DCB08 Temperature Readings:
-----------------------------------
Channel 0: 22.5°C
Channel 1: 23.1°C
Channel 2: No sensor
Channel 3: 21.8°C
...
```

##### 2. Read Single Channel Temperature
Read temperature from a specific channel (0-7):
```bash
python r4dcb08_cli.py --port /dev/ttyUSB0 read-channel 0
```

Output:
```
Channel 0: 22.5°C
```

##### 3. Set Temperature Correction
Set a temperature correction value for calibration:
```bash
python r4dcb08_cli.py --port /dev/ttyUSB0 set-correction 3 1.5
```

This adds +1.5°C correction to channel 3. Corrections can be negative:
```bash
python r4dcb08_cli.py --port /dev/ttyUSB0 set-correction 2 -0.8
```

##### 4. Read Temperature Corrections
View current correction values for all channels:
```bash
python r4dcb08_cli.py --port /dev/ttyUSB0 read-corrections
```

Output:
```
Temperature Correction Values:
-----------------------------------
Channel 0: +0.0°C
Channel 1: +1.2°C
Channel 2: -0.8°C
Channel 3: +1.5°C
...
```

#### Example Commands

```bash
# Linux/macOS examples
python r4dcb08_cli.py --port /dev/ttyUSB0 --address 1 read-all
python r4dcb08_cli.py --port /dev/ttyUSB0 read-channel 5
python r4dcb08_cli.py --port /dev/ttyUSB0 set-correction 0 2.1

# Windows examples  
python r4dcb08_cli.py --port COM3 --address 2 read-all
python r4dcb08_cli.py --port COM3 --baudrate 19200 read-channel 3

# Different device address and baud rate
python r4dcb08_cli.py --port /dev/ttyUSB0 --address 5 --baudrate 19200 read-all
```

### Python API Usage

You can also use the R4DCB08Client class directly in your Python code:

```python
from r4dcb08_cli import R4DCB08Client

# Create client
client = R4DCB08Client("/dev/ttyUSB0", address=1, baudrate=9600)

# Connect
if client.connect():
    try:
        # Read all temperatures
        temperatures = client.read_all_temperatures()
        for i, temp in enumerate(temperatures):
            if temp is not None:
                print(f"Channel {i}: {temp:.1f}°C")
        
        # Read single channel
        temp = client.read_single_temperature(0)
        print(f"Channel 0: {temp:.1f}°C")
        
        # Set correction
        client.set_temperature_correction(0, 1.5)
        
    finally:
        client.disconnect()
```

## Protocol Information

### Register Map
- **0x0000-0x0007**: Temperature readings (8 registers, one per channel)
- **0x0008-0x000F**: Temperature corrections (8 registers, one per channel)

### Temperature Encoding
- Temperature values are stored as signed 16-bit integers
- Actual temperature = raw_value / 10.0
- Example: 235 = 23.5°C, -150 = -15.0°C
- 0x8000 (32768) = sensor error/disconnected

### Connection Settings
```python
# Correct settings for R4DCB08
baudrate = 9600    # Default, can be 1200, 2400, 4800, 9600, 19200
parity = 'N'       # No parity (important!)
stopbits = 1       # 1 stop bit
bytesize = 8       # 8 data bits
```

## Troubleshooting

### Connection Issues
1. **Device not responding**:
   - Ensure R4DCB08 is powered (6-24V DC)
   - Check serial cable connection
   - Verify correct serial port path

2. **Communication errors**:
   - Confirm device address (default: 1)
   - Check baud rate setting (default: 9600)  
   - Ensure no other program is using the serial port
   - Verify parity is set to 'N' (None)

### Temperature Reading Issues
1. **"No sensor" readings**:
   - Check DS18B20 sensor connections
   - Verify if sensors is powered by checking voltage between 5V and ground, also D* line should have about 5 V to ground
   - Test sensors individually or replace with known working sensors

2. **Incorrect temperature values**:
   - Check temperature corrections with `read-corrections`
   - Verify sensor calibration
   - Check for electromagnetic interference

### Common Error Messages
- **"Failed to connect"**: Check port path and permissions
- **"Modbus error"**: Device communication issue, check address/baud rate
- **"Channel must be 0-7"**: Invalid channel number specified
- **"Correction must be between -327.6 and +327.6"**: Correction value out of range

## File Structure

```
Modbus-RTU/
├── r4dcb08_cli.py      # Command-line interface (main script)
├── requirement.txt     # Python dependencies
└── README.md          # This documentation
```

## Hardware Setup

1. Connect R4DCB08 to power supply (6-24V DC)
2. Connect DS18B20 temperature sensors to the 8 channels
3. Connect USB-to-RS485 converter to your computer
4. Connect RS485 A/B lines to R4DCB08 Modbus terminals

## License

This project is open source and available under standard open source licenses.
