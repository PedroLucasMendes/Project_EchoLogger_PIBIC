import os
import time
from machine import Pin, Timer, SoftI2C, ADC, Timer, RTC, SDCard
from ble_advertising import advertising_payload
import machine
import bme680 
import RGBLib
import i2smic
import random
import struct
import bluetooth


# LED CONTROLLER
LED = RGBLib.Controller(4,26,27)

# LDR SENSOR (ANALOGIC INTERFACE)
adc = ADC(Pin(34), atten=ADC.ATTN_6DB) #10kOhm - 3.3v
_MAXL = 65535

# BMP680 SENSOR (I2C INTERFACE)
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
bme = bme680.BME680_I2C(i2c=i2c)

#TIMERS
UPDTimer=Timer(2)
lumin, temp, hum, pres, gas = 0,0,0,0,0

#SDCard Controller
_SD=None
try:
     _SD = SDCard(slot=2)
     os.mount(_SD, "/sd") 
except:_SD=None

# BLUETOOTH LOW ENERGY ADVERTISERMENTS
_UART_UUID =  bluetooth.UUID(0x181A)
_UUIDBASE="{}-B5A3-F393-E0A9-E50E24DCCA9E"  
_UART_RX = (bluetooth.UUID(_UUIDBASE.format("6E400002")),0x0008 | 0x0004,) # receive from app
_UART_TX = (bluetooth.UUID(_UUIDBASE.format("6E400003")),0x0002 | 0x0010,) # send to app
_UART_PRES = ( bluetooth.UUID(0x2A6D),0x0002 | 0x0010,) # Pressure hPA
_UART_TEMP = ( bluetooth.UUID(0x2A6E),0x0002 | 0x0010,) # Temperature ºC
_UART_HUMI = ( bluetooth.UUID(0x2A6F),0x0002 | 0x0010,) # Humidity %
_UART_AQUA = ( bluetooth.UUID(0x2AF9),0x0002 | 0x0010,) # Generic Level 
_UART_LUMI = ( bluetooth.UUID(0x2AFB),0x0002 | 0x0010,) # Illuminance %
_UART_TIME = ( bluetooth.UUID(0x2B90),0x0002 | 0x0010,) # Current device time sec from 2000/01/01 00:00:00
_UART_SDCARD = ( bluetooth.UUID(0x2B04),0x0002 | 0x0010,) # Percentage (%)
_ADV_APPEARANCE_MULTISENSOR = const(1366) # Multisensor

_UART_SERVICE = (_UART_UUID,(_UART_TX, _UART_RX, _UART_TEMP, _UART_HUMI, _UART_PRES, _UART_AQUA, _UART_LUMI, _UART_TIME, _UART_SDCARD),)

#BLE Peripheral
#--------------------------------- FUNCTIONS ----------------------------------------#
class BLEPeripheral:
     #declare status, handles and operation mode
     def __init__(self, ble, name="EchoLogger"):
          self._ble = ble
          self._ble.active(True)
          self._ble.irq(self._irq)
          ((self._handle_tx, self._handle_rx, self._handle_temp, self._handle_humi, self._handle_pres, self._handle_aqua, self._handle_lumi,self._handle_time, self._handle_sdcard),) = self._ble.gatts_register_services((_UART_SERVICE,))
          self._connections = set()
          self._write_callback = None
          self._payload = advertising_payload(name=name, services=[_UART_UUID], appearance=_ADV_APPEARANCE_MULTISENSOR,)
          self._advertise()

     #Handler ble interruptions
     def _irq(self, event, data):
          if event == 1:
               conn_handle, _, _ = data
               print("Connected", conn_handle)
               self._connections.add(conn_handle)
               LED.set('green')
               IMUTimer.init(period=BLEPeriod, mode=Timer.PERIODIC, callback=readSensor)
          elif event == 2:
               conn_handle, _, _ = data
               print("Disconnected", conn_handle)
               LED.set('white')
               IMUTimer.deinit()
               self._connections.remove(conn_handle)
               self._advertise()
          elif event == 3:
               conn_handle, value_handle = data
               value = self._ble.gatts_read(value_handle)
               if value_handle == self._handle_rx and self._write_callback:
                    self._write_callback(value)

     #Send message
     def send(self, data):
          for conn_handle in self._connections:
               self._ble.gatts_notify(conn_handle, self._handle_tx, data)
     
     #Update advertisers
     def update_vals(self, data):
          
          self._ble.gatts_write(self._handle_temp, bytearray(struct.pack("f",data["temp"])),True)
          self._ble.gatts_write(self._handle_humi, bytearray(struct.pack("f",data["humi"])),True)
          self._ble.gatts_write(self._handle_pres, bytearray(struct.pack("f",data["pres"])),True)
          self._ble.gatts_write(self._handle_lumi, bytearray(struct.pack("f",data["lumi"])),True)
          self._ble.gatts_write(self._handle_aqua, bytearray(struct.pack("f",data["aqua"])),True)
          self._ble.gatts_write(self._handle_time, bytearray(struct.pack("f",data["time"])),True)
          self._ble.gatts_write(self._handle_sdcard, bytearray(struct.pack("f",data["sdcard"])),True)

          #Update values notifying clients
          #for conn_handle in self._connections:     
               #self._ble.gatts_notify(conn_handle, self._handle_temp, bytearray(struct.pack("f",data["temp"])))
               #self._ble.gatts_notify(conn_handle, self._handle_humi, bytearray(struct.pack("f",data["humi"])))
               #self._ble.gatts_notify(conn_handle, self._handle_pres, bytearray(struct.pack("f",data["pres"])))
               #self._ble.gatts_notify(conn_handle, self._handle_lumi, bytearray(struct.pack("f",data["lumi"])))
               #self._ble.gatts_notify(conn_handle, self._handle_aqua, bytearray(struct.pack("f",data["aqua"])))
               #self._ble.gatts_notify(conn_handle, self._handle_time, bytearray(struct.pack("f",data["time"])))
               #self._ble.gatts_notify(conn_handle, self._handle_sdcard, bytearray(struct.pack("f",data["sdcard"])))
               
     #check connections
     def is_connected(self):
          return len(self._connections) > 0

     #start advertiserment
     def _advertise(self, interval_us=500000):
          print("Advertising")
          self._ble.gap_advertise(interval_us, adv_data=self._payload)

     #receive data callback
     def on_write(self, callback):
          self._write_callback = callback   

#BLUETOOT TIMERS
BLESerial=""
BLEPeriod=5000
IMUTimer=Timer(2)
random.seed(123)

#blueototh callback function to handle incoming data
def on_rx(v):
     global BLESerial
     print("RX", v)
     if v.startswith(b"time:"):    #time:YYYYMMDDhhmmss
          #UNIX_OFFSET=946684800
          tstamp = v.decode('utf-8').split(":")[1]
          ano = int(tstamp[:4],10)
          mes = int(tstamp[4:6],10)
          dia = int(tstamp[6:8],10)
          hora = int(tstamp[8:10],10)
          minuto = int(tstamp[10:12],10)
          segundo = int(tstamp[12:14],10)
          _CLOCK.datetime((ano,mes,dia,0,hora,minuto,segundo,0))
          BLESerial.send("status:clock_ok")
     elif v.startswith(b"gps:"): #gps:-0123.456;987.5212
          coord = v.decode('utf-8').split(":")[1]
          lat,lon = coord.split(';')
          gps={"lat":lat,"lon":lon}
          print(gps)
          BLESerial.send("status:gps_ok")
     elif v.startswith("led"): #led:color
          label = v.decode('utf-8').split(":")[1]
          LED.set(label)
          BLESerial.send("status:led_ok")
     elif v.startswith("rgb"): #led:r,g,b
          r,g,b,h = v.decode('utf-8').split(":")[1].split(',')
          LED.man(int(r,10)*4,int(g,10)*4,int(b,10)*4)          
          BLESerial.send("status:rgb_ok")
     elif v.startswith("mic:record"):
          LED.set('orange')
          with open("/timeflag.tmp","w") as fp:
            fp.write("ok")
          BLESerial.send("status:Init")
     elif v.startswith("mic:stop"):
          LED.set('green')
          _MIC.stop()
          BLESerial.send("status:stoped") 
     else:
          BLESerial.send("status:fail")    

def loadBluetooth():
     try: 
          global BLESerial, LED, SD
          ble = bluetooth.BLE()
          BLESerial = BLEPeripheral(ble)
          BLESerial.on_write(on_rx)
          print("Bluetooth Loaded...")
     except Exception as e:
          print(e)
          pass 

#read all information you want to advertise
def readSensor(t):
     global BLESerial, bme
     pkg = {}
     pkg["time"]=time.time() # s from 2000
     pkg["temp"]=round(bme.temperature, 2) # ºC
     pkg["humi"]=round(bme.humidity, 2) # %
     pkg["pres"]=round(bme.pressure, 2) #avg sea level: 1013,25 
     pkg["lumi"]=int(round((adc.read_u16() / _MAXL * 100),2))
     pkg["aqua"]=round(bme.gas/1000, 2) #values ranges in https://cdn-shop.adafruit.com/product-files/3660/BME680.pdf
     _,_,x,y,_,_,_,_,_,_=os.statvfs('/sd/'); 
     pkg["sdcard"]=round(100*(y/x),2)
     print(pkg)
     #send data to bluetooth
     BLESerial.update_vals(pkg)


#MAIN SENSOR CYCLE
def read_sensors(t):
    global lumin, temp, hum, pres, gas, _SAMPLES_LOOPS
    print("Collecting Sample")
    lumin = round(lumin+(adc.read_u16() / _MAXL * 100)/_SAMPLES_LOOPS,2)
    temp = round(temp+(bme.temperature/_SAMPLES_LOOPS), 2)
    hum = round(hum+(bme.humidity/_SAMPLES_LOOPS), 2)
    pres = round(pres+(bme.pressure/_SAMPLES_LOOPS), 2) #avg sea level: 1013,25 
    gas = round(gas+((bme.gas/1000)/_SAMPLES_LOOPS), 2) #values ranges in https://cdn-shop.adafruit.com/product-files/3660/BME680.pdf
    print("Sampling: {},{},{},{},{},{};".format(time.time(),temp,hum,pres,gas,lumin))
 
 
#Gets the last record on the SDCard and return the new filename
def new_file():
     FCount = 0
     FPath="/sd/record_{}.wav"
     try: 
          while os.stat(FPath.format(FCount)):
               FCount+=1
     except:pass
     return FPath.format(FCount)


#LOAD BLE
LED.boot()
loadBluetooth() 


cond = False

_CLOCK=RTC()
try:
    _=os.stat("/timeflag.tmp")
    cond = True 
except:
    pass
        

if(cond == True):
    #I2s Microphone
    _MIC = i2smic.Controller()
    _SENSORS_FILE="/sd/data.txt"
    _AUDIO_FILE="/sd/record-{}".format(time.time())
    _AUDIO_LENGTH=300 #s
    _READINGS_INTERVAL=900 #s
    _SAMPLES_LOOPS=_AUDIO_LENGTH//_READINGS_INTERVAL

    print("Now is",time.localtime())
    LED.set('orange')

    UPDTimer.init(period=_READINGS_INTERVAL*1000, mode=Timer.PERIODIC, callback=read_sensors)

    _MIC.record(_AUDIO_FILE)
    time.sleep(_AUDIO_LENGTH)
    UPDTimer.deinit()
    _MIC.stop() 

    header=False
    try:os.stat(_SENSORS_FILE)
    except:header=True
    pen = open(_SENSORS_FILE,"a+")
    if header: pen.write('timestamp,temperatura(C),umidade(%),pressao(Pa),gas(ohms),luminisidade(%);audio;')
    print("Saving: {},{},{},{},{},{};".format(time.time(),temp,hum,pres,gas,lumin,_AUDIO_FILE))
    pen.write("{},{},{},{},{},{};".format(time.time(),temp,hum,pres,gas,lumin,_AUDIO_FILE))        
    pen.close()
        
    print("Done")
    machine.deepsleep(_AUDIO_LENGTH*1000)


