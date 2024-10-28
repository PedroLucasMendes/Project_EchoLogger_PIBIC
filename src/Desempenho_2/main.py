import os
import time
from machine import Pin, Timer, SDCard, ADC, SoftI2C, RTC
import bluetooth
import i2smic
import struct
from ble_advertising import advertising_payload
import random
import machine

# BLE Configuration Variables
_UART_UUID = bluetooth.UUID(0x181A)
_UUIDBASE = "{}-B5A3-F393-E0A9-E50E24DCCA9E"
_UART_RX = (bluetooth.UUID(_UUIDBASE.format("6E400002")), 0x0008 | 0x0004,)  # receive
_UART_TX = (bluetooth.UUID(_UUIDBASE.format("6E400003")), 0x0002 | 0x0010,)  # send
_UART_CFG = ( bluetooth.UUID(0x2A6D),0x0002 | 0x0010,) # CFG
_ADV_APPEARANCE_MULTISENSOR = const(1366)
_UART_SERVICE = (_UART_UUID, (_UART_TX, _UART_RX, _UART_CFG),)

# BLE Peripheral Class
class BLEPeripheral:
    def __init__(self, ble, name="EchoLogger - 1"):
        
        self._ble = ble
        print("func")
        self._ble.active(True)
        
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx, self._handle_cfg),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID], appearance=_ADV_APPEARANCE_MULTISENSOR,)
        self._advertise()

    def _irq(self, event, data):
        if event == 1:  # Connection established
            conn_handle, _, _ = data
            print("Connected", conn_handle)
            self._connections.add(conn_handle)
            # LED.set('green')  # Removido para evitar uso de LED
        elif event == 2:  # Disconnected
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            self._connections.remove(conn_handle)
            # LED.set('white')  # Removido para evitar uso de LED
            self._advertise()
        elif event == 3:  # Data received
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)



    #check connections
    def is_connected(self):
        return len(self._connections) > 0

    
    def on_write(self, callback):
        self._write_callback = callback

    def _advertise(self, interval_us=500000):
        print("Advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)





print("iniciei")

# Function to Update Configuration Based on BLE Data
def on_rx(data):
    try:
        message = data.decode('utf-8')
        if message.startswith("cf:"):
            parts = message[3:].split(";")
            bits = int(parts[0])
            rate = int(parts[1])
            volume_audio = int(parts[2])
            
            # SDCard Controller
            _SD = None
            try:
                _SD = SDCard(slot=2)
                os.mount(_SD, "/sd")
            except:
                _SD = None
        
            # Audio Recording Variables
            _MIC = i2smic.Controller()
            _AUDIO_LENGTH = 120  # seconds

            file_name = f"/sd/{bits}_{rate}_{volume_audio}.wav"
            config_str = f"{bits}_{rate}_{volume_audio}.wav\n"

            # Start recording with the received configuration
            print(f"Recording with {bits} bits, {rate} Hz, volume {volume_audio}. Saving to {file_name}")
            _MIC = i2smic.Controller(sample_rate=rate, sample_bits=bits, volume=volume_audio)
            _MIC.record(file_name)
            time.sleep(_AUDIO_LENGTH)
            _MIC.stop()
            print(f"Recording saved: {file_name}")

            BLESerial.send("status:recorded")
        else:
            print("Invalid configuration format")
    except Exception as e:
        print("Error:", e)
        pass

def loadBluetooth():
     try: 
          global BLESerial
          ble = bluetooth.BLE()
          print("ble init")
          BLESerial = BLEPeripheral(ble)
          
          BLESerial.on_write(on_rx)
          print("Bluetooth Loaded...")
     except Exception as e:
          print(e)
          pass 



# BLE Initialization
BLESerial=""

loadBluetooth() 
