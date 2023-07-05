import dht
import machine
from machine import Pin, PWM, ADC
import utime
import wifiConnection
import network
import urequests as requests
from time import sleep
import random
import ujson

#Variables -------------------------------------------------

dth = dht.DHT11(machine.Pin(15))
adc = ADC(Pin(27))
morning = False
noon = False
night = False
i = 0
DELAY = 5  # Delay in seconds between posts

TOKEN = "BBFF-f9ern0sUq3AyXuyypxaEtd0afcT4l1"
DEVICE_LABEL = "picowboard"
TEMPERATURE_LABEL = "sensor"
HUMIDITY_LABEL = "humidity"
LIGHT_LABEL = "light"
WIFI_SSID = 'SpectrumSetup-90'
WIFI_PASS = 'terrifictruck893'

#Methods for my sensors ------------------------------------

def PicoLedOn():
    Pin("LED", Pin.OUT).on()

def PicoLedOff():
    Pin("LED", Pin.OUT).off()

def MeasureTemperature():
    try:
        utime.sleep(1)
        dth.measure()
        return dth.temperature()
    except Exception as error:
        LedRedOn()
        print("Exception occurred while measuring temperature: ", error)

def MeasureHumidity():
    try:
        utime.sleep(1)
        dth.measure()
        return dth.humidity()
    except Exception as error:
        LedRedOn()
        print("Exception occurred while measuring humidity: ", error)

def MeasureLumi():
    try:
        volt = adc.read_u16()
        return int((volt/42000) * 100)
    except Exception as error:
        LedRedOn()
        print("Exception occurred while measuring Light: ", error)

    #Method for Green LED on
def LedGreenOn():
    led = machine.Pin(13, machine.Pin.OUT).on()

    #Method for Green LED off
def LedGreenOff():
    led = machine.Pin(13, machine.Pin.OUT).off()
    
    #Method for Red LED on
def LedRedOn():
    led = machine.Pin(14, machine.Pin.OUT).on()

    #Method for Red LED off
def LedRedOff():
    led = machine.Pin(14, machine.Pin.OUT).off()

def ToString():
    try:
        print("Temperatur i rummet: {0} C, fuktigheten i rummet: {1} %, rummet 'a'r {2}".format(
            MeasureTemperature(), 
            MeasureHumidity(), 
            "m'o'rkt" if MeasureLumi() > 70 else "ljust"))
    except Exception as error:
        LedRedOn()
        print("Exception occured while printing ToString", error)

#Method for button
#the connection to the button pin is very unstable and the return value flux
#without the user pressing the button
def Button():
    push_button = Pin(16, Pin.IN)
    print(push_button.value())
    if push_button.value() == 0:
        return False
    else:
        return True

#test case for the pico
def test_case_1():
    try:
        output = MeasureLumi()
        LedGreenOn()
        PicoLedOn()
        assert output < 70
        return True
    except AssertionError:
        LedRedOn()
        return False

#WiFi ---------------------------------------

def http_get(url = 'http://www.google.com'):
    response = None
    try:
        response = requests.get(url)
        status = response.status_code
        print('GET request status: {0}'.format(status))
        if 200 <= status < 300: # response OK
            print(response.text)
    finally:
        if response != None:
            response.close()

# WiFi disconnection
def disconnect():
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
        wlan.active(False)

# WiFi connection
def connect():
    wlan = network.WLAN(network.STA_IF)         # Put modem on Station mode
    if not wlan.isconnected():                  # Check if already connected
        print('connecting to network...')
        wlan.active(True)                       # Activate network interface
        # set power mode to get WiFi power-saving off (if needed)
        wlan.config(pm = 0xa11140)
        wlan.connect(WIFI_SSID, WIFI_PASS)  # Your WiFi Credential
        print('Waiting for connection...', end='')
        # Check if it is connected otherwise wait
        while not wlan.isconnected() and wlan.status() >= 0:
            print('.', end='')
            sleep(1)
    # Print the IP assigned by router
    ip = wlan.ifconfig()[0]
    print('\nConnected on {}'.format(ip))
    return ip

#Methods for ubidots ---------------------------------------

# Method to create the json to send the request
def build_json(variable1, value1, variable2=None, value2=None, variable3=None, value3=None):
    try:
        data = {variable1: value1}
        if variable2 != None and value2 != None:
            data.update({variable2: value2})
        if variable3 != None and value3 != None:
            data.update({variable3: value3})
        return data
    except:
        return None

# Method to send data to Ubidots
def sendData(device, variable, value):
    try:
        url = "http://industrial.api.ubidots.com/"
        url = url + "api/v1.6/devices/" + device
        headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}
        data = build_json(variable, value)

        if data is not None:
            data = ujson.dumps(data)  # Manually convert dict to JSON string
            print(data)
            req = requests.post(url=url, headers=headers, data=data)  # Pass data to the `data` parameter
            response = req.json()
            print(response)  # Print the response from the server
            return response
        else:
            pass
    except Exception as e:  # Catch any exceptions and print them
        print("Exception occurred: ", e)
        pass

#Running program
test_case_1()
print("connecting to UBIDOTS")

# WiFi connection
connect()

while i < 50:
    utime.sleep(2)
    ToString()
    if 30 < MeasureLumi() < 70 and not morning:
        sendData(DEVICE_LABEL, TEMPERATURE_LABEL, MeasureTemperature())
        sleep(DELAY)
        sendData(DEVICE_LABEL, HUMIDITY_LABEL, MeasureHumidity())
        sleep(DELAY)
        sendData(DEVICE_LABEL, LIGHT_LABEL, MeasureLumi())
        sleep(DELAY)
        morning = True
    elif MeasureLumi() < 30 and not noon:
        returnValue = sendData(DEVICE_LABEL, TEMPERATURE_LABEL, MeasureTemperature())
        sleep(DELAY)
        returnValue = sendData(DEVICE_LABEL, HUMIDITY_LABEL, MeasureHumidity())
        sleep(DELAY)
        returnValue = sendData(DEVICE_LABEL, LIGHT_LABEL, MeasureLumi())
        sleep(DELAY)
        noon = True
    elif MeasureLumi() > 70 and not night:
        returnValue = sendData(DEVICE_LABEL, TEMPERATURE_LABEL, MeasureTemperature())
        sleep(DELAY)
        returnValue = sendData(DEVICE_LABEL, HUMIDITY_LABEL, MeasureHumidity())
        sleep(DELAY)
        returnValue = sendData(DEVICE_LABEL, LIGHT_LABEL, MeasureLumi())
        sleep(DELAY)
        night = True
    if morning and noon and night:
        morning = False
        noon = False
        night = False
    i = i+1

# WiFi disconnection
disconnect()
print("Program has ended")
LedGreenOff()
PicoLedOff()
