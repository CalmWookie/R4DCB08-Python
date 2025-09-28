#!/usr/bin/env python3
"""
R4DCB08 Temperature Collector - Basic Example
===========================================

Simple example script showing how to read temperatures from R4DCB08
8-channel temperature collector using pymodbus.
"""

import pymodbus
from pymodbus.client import ModbusSerialClient as ModbusClient


def decode_temperature(raw_value):
    """Decode temperature from R4DCB08 raw register value."""
    if raw_value == 0x8000:  # 32768 indicates sensor error/disconnection
        return None
    
    # Convert unsigned to signed 16-bit integer
    if raw_value > 32767:
        signed_value = raw_value - 65536
    else:
        signed_value = raw_value
    
    # Temperature is encoded as (temperature * 10), divide by 10
    return signed_value / 10.0


def main():
    """Main function to read temperatures from R4DCB08."""
    # R4DCB08 configuration according to technical specs
    client = ModbusClient(
        port="/dev/tty.usbserial-A10N5MZK",  # Adjust for your system
        baudrate=9600,                       # Default baud rate
        parity='N',                         # No parity
        stopbits=1,
        bytesize=8,
        timeout=1.0
    )
    
    # Connect to device
    if not client.connect():
        print("Failed to connect to R4DCB08 device!")
        print("Check:")
        print("1. Device is powered and connected")
        print("2. Serial port path is correct")
        print("3. No other program is using the port")
        return
    
    print("Connected to R4DCB08 Temperature Collector")
    
    try:
        # Read all 8 temperature channels
        device_address = 1  # Default R4DCB08 address
        result = client.read_holding_registers(0, count=8, device_id=device_address)
        
        if result.isError():
            print(f"Error reading from device: {result}")
        else:
            print("\nR4DCB08 Temperature Readings:")
            print("-" * 35)
            
            for i, raw_temp in enumerate(result.registers):
                temperature = decode_temperature(raw_temp)
                if temperature is not None:
                    print(f"Channel {i}: {temperature:.1f}°C")
                else:
                    print(f"Channel {i}: No sensor")
            
            print(f"\nRaw register values: {result.registers}")
    
    except Exception as e:
        print(f"Communication error: {e}")
    
    finally:
        client.close()
        print("\nDisconnected from device.")


if __name__ == "__main__":
    main()