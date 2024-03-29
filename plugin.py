#!/usr/bin/env python
"""
Energy Meter LED Puls Counter via GPIO
Author: Derenback
Requirements:
    1. LED detector
    2. Domoticz running on a Raspberry pi
    3. python 3.x
    4. sudo apt install python3-rpi.gpio

"""
"""
<plugin key="EnergyLEDCount" name="Energy Meter LED Puls Counter via GPIO" version="0.0.4" author="Derenback">
    <params>
        <param field="Mode1" label="GPIO pin" width="40px" required="true" default="8" />
        <param field="Mode2" label="Report interval sec." width="40px" required="true" default="10" />
        <param field="Mode3" label="Debug" width="75px">
            <options>
                <option label="On" value="Debug"/>
                <option label="Off" value="Off" default="true" />
            </options>
        </param>
    </params>
</plugin>
"""
import Domoticz
import RPi.GPIO as GPIO 
import time

pulse_count = 0
pulse_count_total = 0
time_for_last_update = time.time()
update_interval = 10

def update_sensor():
    global pulse_count, pulse_count_total, time_for_last_update
    time_diff = time.time() - time_for_last_update
    if (time_diff > update_interval):
        time_for_last_update = time.time()
        pulse_count_total += pulse_count
        wattage = 0
        if (pulse_count != 0):
            wattage = int(3600 / (time_diff / pulse_count))
        Devices[1].Update(0, str(wattage) + ";" + str(pulse_count_total))
        if (Parameters["Mode3"] == "Debug"):
            Domoticz.Log("EnergyLEDCount, Time: " + str(round(time_diff,5)))  
            Domoticz.Log("EnergyLEDCount, Wattage: " + str(wattage) + " Pulses total: " + str(pulse_count_total))
        
        pulse_count = 0

def led_pulse_callback(channel):
    global pulse_count
    pulse_count += 1
    update_sensor()
    if (Parameters["Mode3"] == "Debug"):
        Domoticz.Log("EnergyLEDCount, callback, pulses: " + str(pulse_count))

def onStart():
    global pulse_count_total, update_interval
    Domoticz.Log("Energy Meter LED Puls Counter via GPIO plugin started")
    update_interval = int(Parameters["Mode2"])
    Domoticz.Heartbeat(update_interval * 2)

    if (Parameters["Mode3"] == "Debug"):
        Domoticz.Log("Debug is On")
        Domoticz.Log("Heartbeat time: " + str(update_interval * 2))
        Domoticz.Log("RPi.GPIO imported, Version: "+str(GPIO.VERSION)+", Raspberry Pi board revision: "+str(GPIO.RPI_INFO['P1_REVISION']))

    if 1 not in Devices:
        Domoticz.Device(Name="Usage", Unit=1, TypeName="kWh", Used=1).Create()
    else:
        temp_str = Devices[1].sValue.split(";")
        pulse_count_total = int(float(temp_str[1]))
        if (Parameters["Mode3"] == "Debug"):
            Domoticz.Log("EnergyLEDCount restored pulse count on restart to: " + str(pulse_count_total)) 

    PIN_LED_IN = int(Parameters["Mode1"])

    GPIO.setmode(GPIO.BOARD)  
    GPIO.setup(PIN_LED_IN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(PIN_LED_IN, GPIO.FALLING, callback=led_pulse_callback, bouncetime=50)
    if (Parameters["Mode3"] == "Debug"):
        Domoticz.Log("EnergyLEDCount, GPIO setup done")


def onHeartbeat():
    update_sensor()

def onStop():
    GPIO.cleanup()
