# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Modified from ^^
# By: Michael Crothers

from fileinput import filename
import time
from datetime import datetime
import board
import adafruit_dht
import RPi.GPIO as GPIO
import math

import I2C_LCD_driver

from message import *


# Initialize the dht device, with data pin connected to:
# dhtDevice = adafruit_dht.DHT11(board.D5)

dhtDevice = adafruit_dht.DHT22(board.D4)

# you can pass DHT22 use_pulseio=False if you wouldn't like to use pulseio.
# This may be necessary on a Linux single board computer like the Raspberry Pi,
# but it will not work in CircuitPython.
# dhtDevice = adafruit_dht.DHT22(board.D18, use_pulseio=False)

mylcd = I2C_LCD_driver.lcd()

mylcd.lcd_clear()

in1 = 23
in2 = 22
in3 = 27
in4 = 17

tempCMax = 29
tempCMin = 10
humiMax = 80
humiMin = 20

tempState = 0
humiState = 0
prevTempState = tempState
prevHumiState = humiState

messageSentFlagTemp = False
messageSentFlagHumi = False

# tempLEDPin = 20
# humiLEDPin = 21
# errMessageLEDPin = 16
# pasMessageLEDPin = 12

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
# GPIO.setup(tempLEDPin,GPIO.OUT)
# GPIO.setup(humiLEDPin,GPIO.OUT)
# GPIO.setup(errMessageLEDPin,GPIO.OUT)
# GPIO.setup(pasMessageLEDPin,GPIO.OUT)


# GPIO.output(tempLEDPin,GPIO.LOW)
# GPIO.output(humiLEDPin,GPIO.LOW)
# GPIO.output(errMessageLEDPin,GPIO.LOW)
# GPIO.output(pasMessageLEDPin,GPIO.LOW)

GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(in3, GPIO.OUT)
GPIO.setup(in4, GPIO.OUT)

def sendMessages(subject, body):
    if __name__ =='__main__':                 
        email_alert("6366759462@txt.att.net", subject, body) # https://www.digitaltrends.com/mobile/how-to-send-a-text-from-your-email-account/ for other cell companies
        #email_alert("3148259049@txt.att.net", subject, body) 
        # email_alert("lcrothers037@rsdmo.org", subject, body) 
        # print("IT SHOULD BE SENDING A MESSAGE")

now = datetime.now()
strDate = now.strftime("%m-%d-%Y-%H:%M:%S")

fileName = "LabData/"  + strDate + ".txt"

f = open(fileName, 'a')
loopMsgs = True
while loopMsgs:
    try:
        sendMessages("Program Started", strDate)
        loopMsgs = False
    except:
        print("Message Error")
        f.write("Message Error")
print("Program Start")
f.write("Program Start")


while True:
    try:    
      #for testing conditions
        # temperature_c = float(input("Enter Celcius: "))
        # temperature_f = temperature_c * (9 / 5) + 32
        # humidity = float(input("Enter Humidity: "))

        temperature_c = dhtDevice.temperature
        temperature_f = temperature_c * (9 / 5) + 32
        humidity = dhtDevice.humidity  

        now = datetime.now()
        strDate = now.strftime("%m/%d/%Y %H:%M:%S")
        print("\n\n\n" + strDate)
        
        print(
            "Temp: {:.1f} F / {:.1f} C    Humidity: {}% ".format(
                temperature_f, temperature_c, humidity
            )
        )

        mylcd.lcd_clear()
        strTemp = "Temp:{:.1f}F {:.1f}C".format(temperature_f,temperature_c)
        strHumi = "Humidity: {}%".format(humidity)
        mylcd.lcd_display_string(strTemp, 1)
        mylcd.lcd_display_string(strHumi, 2)

        f.write("\n\n\n" + strDate)
        f.write("\n" + strTemp)
        f.write("\n" + strHumi)
        
        if temperature_c > tempCMax:
            #if temp greater than max
            tempState = 1
            #Turn on AC relay
            #Turn off Heater relay
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)            
            strWarn = "Warning {} Time: {}".format(strTemp,strDate)
            print("Warning High Temperature")
            # print(strWarn)
            f.write("\n" + "Warning High Temperature")
            # f.write("\n" + strWarn)
            if tempState != prevTempState:            
                #if temperature greater than max and a message was not just sent, send a message                
                try:                
                    sendMessages("Warning High Temperature", strWarn)
                    print("High Temp Message Sent")
                    f.write("\n" + "High Temp Message Sent")
                    prevTempState = tempState
                except:    
                    print("Message Error")
                    f.write("\n" + "Message Error")

        if temperature_c < tempCMin:
            #if temp less than min 
            tempState = -1
            #Turn on Heater relay
            #Turn off AC Relay
            GPIO.output(in2, GPIO.HIGH)
            GPIO.output(in1, GPIO.LOW)   
            strWarn = "Warning {} Time: {}".format(strTemp,strDate)
            print("Warning Low Temperature")
            # print(strWarn)
            f.write("\n" + "Warning Low Temperature")
            # f.write("\n" + strWarn)
            if tempState != prevTempState:
                #if temp less than min and message was not just sent, send a message
                try:
                    sendMessages("Warning Low Temperature", strWarn)                       
                    print("Low Temp Message Sent")
                    f.write("\n" + "Low Temp Message Sent")
                    prevTempState = tempState                       
                except:
                    print("Message Error")
                    f.write("\n" + "Message Error")


        if humidity > humiMax:
            #if humidity greater than max 
            humiState = 1
            #Turn on Dehumidifier relay
            #Turn off Humidifier relay    
            GPIO.output(in3, GPIO.HIGH)
            GPIO.output(in4, GPIO.LOW)     
            strWarn = "Warning {} Time: {}".format(strHumi,strDate)
            print("Warning High Humidity")
            # print(strWarn)
            f.write("\n" + "Warning High Humidity")
            # f.write("\n" + strWarn)
            if humiState != prevHumiState:
                #if humidity greater than max and a message was not just sent, send a message
                try:
                    sendMessages("Warning High Humidity", strWarn)  
                    print("High Humidity Message Sent")
                    f.write("\n" + "High Humidity Message Sent")                    
                    prevHumiState = humiState
                except:
                    print("Message Error")
                    f.write("\n" + "Message Error")

        if humidity < humiMin:
            #if humidity less than min 
            humiState = -1
            #Turn on Humidifier relay
            #Turn off Dehumidifier relay
            GPIO.output(in4, GPIO.HIGH)
            GPIO.output(in3, GPIO.LOW)   
            strWarn = "Warning {} Time: {}".format(strHumi,strDate)
            print("Warning Low Humidity")
            # print(strWarn)
            f.write("\n" + "Warning High Humidity")
            # f.write("\n" + strWarn)
            if humiState != prevHumiState:
                try:
                    sendMessages("Warning Low Humidity", strWarn)
                    print("Low Humidity Message Sent")
                    f.write("\n" + "Low Humidity Message Sent")                                        
                    prevHumiState = humiState
                except:
                    print("Message Error")
                    f.write("\n" + "Message Error")
                    
        if temperature_c <= tempCMax and temperature_c >= tempCMin:
            #if temp stabilizes 
            tempState = 0
            #Turn off AC
            #Turn off Heating
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)   
            #GPIO.output(in1, GPIO.LOW)
            #GPIO.output(in2, GPIO.LOW)
            strTempStab = "Temperature Stabilized {} Time: {}".format(strTemp,strDate)
            print("Temperature Stabilized")
            # print(strTempStab)
            f.write("\n" + "Temperature Stabilized")
            # f.write("\n" + strTempStab)
            if tempState != prevTempState:
                try:
                    sendMessages("Temperature Stabilized", strTempStab)
                    print("Temp Stablized Message Sent")
                    f.write("\n" + "Temp Stabilized Message Sent")
                    prevTempState = tempState
                except:
                    print("Message Error")
                    f.write("\n" + "Message Error")
                         
        if humidity <= humiMax and humidity >= humiMin:
            #if humidity stabilizes 
            humiState = 0
            #Turn off Humidifier
            #Turn off Dehumidifier
            GPIO.output(in3, GPIO.LOW)
            GPIO.output(in4, GPIO.LOW)
            strHumiStab = "Humidity Stabilized {} Time: {}".format(strHumi,strDate)
            print("Humidity Stabilized")
            # print(strHumiStab)
            f.write("\n" + "Humidity Stabilized")
            # f.write("\n" + strHumiStab)
            if humiState != prevHumiState:                
                try:
                    sendMessages("Humidity Stabilized", strHumiStab)
                    print("Humidity Stabilized Message Sent")  
                    f.write("\n" + "Humidity Stabilized Message Sent")
                    prevHumiState = humiState
                except:
                    print("Message Error")
                    f.write("\n" + "Message Error")
    
        time.sleep(2.0)

    except RuntimeError as error:
        # Errors happen fairly often, DHT's are hard to read, just keep going
        
        print("\n" + error.args[0])
        f.write("\n\n" + error.args[0])
        time.sleep(2.0)
        continue
    except KeyboardInterrupt:
        now = datetime.now()
        strDate = now.strftime("%m/%d/%Y %H:%M:%S")
        sendMsgs = True
        while sendMsgs:
            try:
                sendMessages("Program Terminated", strDate)
                sendMsgs = False
            except:
                print("Message Error")
                f.write("Message Error")
        print("Program Stop")
        f.write("\n\nProgram Terminated")
        mylcd.lcd_clear()
        GPIO.cleanup()
        f.close()
        quit()
    # except Exception as error:
    #     mylcd.lcd_clear()
    #     mylcd.lcd_display_string("Error")
    #     dhtDevice.exit()
    #     GPIO.cleanup()
    #     raise error

GPIO.cleanup()
