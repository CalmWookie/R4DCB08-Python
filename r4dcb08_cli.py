#!/usr/bin/env python3
"""
R4DCB08 Temperature Collector Command Line Interface
===================================================

A command-line tool for interacting with R4DCB08 8-channel temperature collectors
using Modbus RTU protocol.

Usage Examples:
    python r4dcb08_cli.py --port /dev/ttyUSB0 --address 1 read-all
    python r4dcb08_cli.py --port COM3 --address 2 read-channel 0
    python r4dcb08_cli.py --port /dev/ttyUSB0 set-correction 3 1.5
"""

import argparse
import sys
from typing import List, Optional
from pymodbus.client import ModbusSerialClient as ModbusClient


class R4DCB08Client:
    """R4DCB08 Temperature Collector Client"""
    
    def __init__(self, port: str, address: int = 1, baudrate: int = 9600, timeout: float = 1.0):
        """Initialize the R4DCB08 client."""
        self.port = port
        self.address = address
        self.baudrate = baudrate
        self.timeout = timeout
        self.client = None
        
    def connect(self) -> bool:
        """Connect to the device."""
        try:
            self.client = ModbusClient(
                port=self.port,
                baudrate=self.baudrate,
                parity='N',  # No parity for R4DCB08
                stopbits=1,
                bytesize=8,
                timeout=self.timeout
            )
            return self.client.connect()
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the device."""
        if self.client:
            self.client.close()
    
    @staticmethod
    def decode_temperature(raw_value: int) -> Optional[float]:
        """
        Decode temperature from raw register value.
        
        Returns:
            Temperature in °C or None if sensor is disconnected
        """
        if raw_value == 0x8000:  # 32768 indicates sensor error/disconnection
            return None
        
        # Convert unsigned to signed 16-bit integer
        if raw_value > 32767:
            signed_value = raw_value - 65536
        else:
            signed_value = raw_value
        
        # Temperature is encoded as (temperature * 10), divide by 10
        return signed_value / 10.0
    
    @staticmethod
    def encode_temperature(temperature: float) -> int:
        """Encode temperature to raw register value."""
        # Multiply by 10 and convert to integer
        raw_value = int(temperature * 10)
        
        # Convert signed to unsigned 16-bit integer
        if raw_value < 0:
            raw_value = raw_value + 65536
        
        return raw_value
    
    def read_all_temperatures(self) -> List[Optional[float]]:
        """Read temperatures from all 8 channels."""
        try:
            result = self.client.read_holding_registers(0, 8, device_id=self.address)
            if result.isError():
                raise Exception(f"Modbus error: {result}")
            
            return [self.decode_temperature(raw) for raw in result.registers]
        except Exception as e:
            raise Exception(f"Failed to read temperatures: {e}")
    
    def read_single_temperature(self, channel: int) -> Optional[float]:
        """Read temperature from a single channel."""
        if not 0 <= channel <= 7:
            raise ValueError("Channel must be 0-7")
        
        try:
            result = self.client.read_holding_registers(channel, 1, device_id=self.address)
            if result.isError():
                raise Exception(f"Modbus error: {result}")
            
            return self.decode_temperature(result.registers[0])
        except Exception as e:
            raise Exception(f"Failed to read temperature from channel {channel}: {e}")
    
    def set_temperature_correction(self, channel: int, correction: float):
        """Set temperature correction for a specific channel."""
        if not 0 <= channel <= 7:
            raise ValueError("Channel must be 0-7")
        
        if not -327.6 <= correction <= 327.6:
            raise ValueError("Correction must be between -327.6 and +327.6 °C")
        
        try:
            raw_correction = self.encode_temperature(correction)
            correction_register = 0x0008 + channel  # Correction registers start at 0x0008
            
            result = self.client.write_register(
                correction_register, raw_correction, device_id=self.address
            )
            if result.isError():
                raise Exception(f"Modbus error: {result}")
        except Exception as e:
            raise Exception(f"Failed to set correction for channel {channel}: {e}")
    
    def read_temperature_corrections(self) -> List[Optional[float]]:
        """Read temperature corrections from all 8 channels."""
        try:
            result = self.client.read_holding_registers(0x0008, 8, device_id=self.address)
            if result.isError():
                raise Exception(f"Modbus error: {result}")
            
            return [self.decode_temperature(raw) for raw in result.registers]
        except Exception as e:
            raise Exception(f"Failed to read temperature corrections: {e}")


def cmd_read_all(client: R4DCB08Client):
    """Read temperatures from all channels."""
    try:
        temperatures = client.read_all_temperatures()
        print("R4DCB08 Temperature Readings:")
        print("-" * 35)
        
        for i, temp in enumerate(temperatures):
            if temp is not None:
                print(f"Channel {i}: {temp:.1f}°C")
            else:
                print(f"Channel {i}: No sensor")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_read_channel(client: R4DCB08Client, channel: int):
    """Read temperature from a specific channel."""
    try:
        temperature = client.read_single_temperature(channel)
        
        if temperature is not None:
            print(f"Channel {channel}: {temperature:.1f}°C")
        else:
            print(f"Channel {channel}: No sensor connected")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_set_correction(client: R4DCB08Client, channel: int, correction: float):
    """Set temperature correction for a channel."""
    try:
        client.set_temperature_correction(channel, correction)
        print(f"Successfully set correction for channel {channel} to {correction:+.1f}°C")
        print("Note: The correction will be applied to future temperature readings.")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def cmd_read_corrections(client: R4DCB08Client):
    """Read temperature corrections from all channels."""
    try:
        corrections = client.read_temperature_corrections()
        print("Temperature Correction Values:")
        print("-" * 35)
        
        for i, correction in enumerate(corrections):
            if correction is not None:
                print(f"Channel {i}: {correction:+.1f}°C")
            else:
                print(f"Channel {i}: No correction")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    return 0


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="R4DCB08 Temperature Collector Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --port /dev/ttyUSB0 --address 1 read-all
  %(prog)s --port COM3 --address 2 read-channel 0
  %(prog)s --port /dev/ttyUSB0 set-correction 3 1.5
  %(prog)s --port /dev/ttyUSB0 read-corrections
        """
    )
    
    # Connection parameters
    parser.add_argument('--port', '-p', required=True,
                        help='Serial port (e.g., /dev/ttyUSB0, COM3)')
    parser.add_argument('--address', '-a', type=int, default=1,
                        help='Modbus device address (1-247, default: 1)')
    parser.add_argument('--baudrate', '-b', type=int, default=9600,
                        choices=[1200, 2400, 4800, 9600, 19200],
                        help='Baud rate (default: 9600)')
    parser.add_argument('--timeout', '-t', type=float, default=1.0,
                        help='Communication timeout in seconds (default: 1.0)')
    
    # Commands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Read all temperatures
    subparsers.add_parser('read-all', help='Read temperatures from all 8 channels')
    
    # Read single channel
    read_parser = subparsers.add_parser('read-channel', help='Read temperature from specific channel')
    read_parser.add_argument('channel', type=int, choices=range(8),
                            help='Channel number (0-7)')
    
    # Set temperature correction
    corr_parser = subparsers.add_parser('set-correction', help='Set temperature correction for a channel')
    corr_parser.add_argument('channel', type=int, choices=range(8),
                            help='Channel number (0-7)')
    corr_parser.add_argument('correction', type=float,
                            help='Correction value in °C (-327.6 to +327.6)')
    
    # Read temperature corrections
    subparsers.add_parser('read-corrections', help='Read temperature corrections from all channels')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Validate device address
    if not 1 <= args.address <= 247:
        print("Error: Device address must be between 1 and 247")
        return 1
    
    # Create client and connect
    client = R4DCB08Client(args.port, args.address, args.baudrate, args.timeout)
    
    if not client.connect():
        print(f"Error: Failed to connect to R4DCB08 at {args.port}")
        print("Troubleshooting:")
        print("1. Check that the device is powered and connected")
        print("2. Verify the serial port path is correct")
        print("3. Ensure no other program is using the serial port")
        print("4. Check device address and baud rate settings")
        return 1
    
    try:
        # Execute command
        if args.command == 'read-all':
            return cmd_read_all(client)
        elif args.command == 'read-channel':
            return cmd_read_channel(client, args.channel)
        elif args.command == 'set-correction':
            return cmd_set_correction(client, args.channel, args.correction)
        elif args.command == 'read-corrections':
            return cmd_read_corrections(client)
        else:
            print(f"Unknown command: {args.command}")
            return 1
    
    finally:
        client.disconnect()


if __name__ == "__main__":
    sys.exit(main())