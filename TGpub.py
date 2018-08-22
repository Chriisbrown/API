# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 12:12:21 2018

@author: chris
"""

import time
from time import sleep
from Adafruit_CCS811 import Adafruit_CCS811
import datetime
ccs =  Adafruit_CCS811()

while not ccs.available():
	pass
temp = ccs.calculateTemperature()
ccs.tempOffset = temp - 25.0

import gspread
from oauth2client.service_account import ServiceAccountCredentials


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('Client_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.

def inputno(g, a, lim1, lim2):
#This defines the function used to check user inputs are within range and of correct data type
    if g == 1:
        while True:
            try:
                h = int(input(a))
                if lim1 <= h <= lim2:
                    return h
                else:
                    GPIO.output(17,GPIO.HIGH)
                    time.sleep(0.033)
                    GPIO.output(17,GPIO.LOW)
            except ValueError:
                GPIO.output(17,GPIO.HIGH)
                time.sleep(0.033)
                GPIO.output(17,GPIO.LOW)
                continue
Menu = '0'
while Menu != 'q':
    Menu = raw_input('Press b to begin log, press q to quit: ')
#Menu setup allowing the program to be run multiple times without turning the pi off
    now = datetime.datetime.now()
    if Menu == 'b':
        f = raw_input('Please enter the test number: ')
        g = raw_input('Enter Name: ')

        sheet = client.open("VOC Data").sheet1
        sheet.update_cell(1,1+5*(int(f)-1),'Test Number: '+f)
        sheet.update_cell(1,2+5*(int(f)-1),g)
        sheet.update_cell(2,1+5*(int(f)-1),'Time (s)')
        sheet.update_cell(2,2+5*(int(f)-1),'VOCs (ppb)')
        sheet.update_cell(2,3+5*(int(f)-1),'eCO2 (ppm)')
        sheet.update_cell(2,4+5*(int(f)-1),'Chip Temp (degrees)')
        
        frequency = inputno(1,'Period of data reading in seconds: ',1,100)
        length = int((inputno(1,'Run test for how many minutes: ',1,1500))*60/frequency)
        i = 3
        start_time = time.time()
        while(i < length+3):
            try:
                t1 = time.time()
                if ccs.available():
                    temp = str(ccs.calculateTemperature())
                    if not ccs.readData():
                        t = str(time.time() - start_time) 
                        x = str(ccs.getTVOC()) 
                        y = str(ccs.geteCO2()) 
                        sheet.update_cell(i,1+5*(int(f)-1), t)
                        sheet.update_cell(i,2+5*(int(f)-1), x)
                        sheet.update_cell(i,3+5*(int(f)-1), y)
                        sheet.update_cell(i,4+5*(int(f)-1), temp)
                        
                        with open('VOCdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
                            s = t + ' ' + x + ' ' + y + ' ' + temp
                            print s
                            print >>d, s
                    else:
                        while(1):
                            pass
                t2 = time.time()
                tT = t2-t1
                if frequency-tT <= 0:
                    sleep(10)
                else:
                    sleep(frequency-tT)
                i += 1
                
                if i % (5*6)/frequency == 0:
                    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
                    creds = ServiceAccountCredentials.from_json_keyfile_name('Client_secret.json', scope)
                    client = gspread.authorize(creds)
                    sheet = client.open("VOC Data").sheet1
                else:
                    pass
            
            except:
                try:
                    t1 = time.time()
                    if ccs.available():
                        temp = str(ccs.calculateTemperature())
                        if not ccs.readData():
                            t = str(time.time() - start_time) 
                            x = str(ccs.getTVOC()) 
                            y = str(ccs.geteCO2()) 
                            with open('VOCdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt' ,'a+') as d:
                                s = t + ' ' + x + ' ' + y + ' ' + temp
                                print s
                                print >>d, s
                        else:
                            while(1):
                                pass
                    t2 = time.time()
                    tT = t2-t1
                    if frequency-tT <= 0:
                        sleep(10)
                    else:
                        sleep(frequency-tT)
                    i += 1 
                except:
                    print 'err',i
                    if frequency-tT <= 0:
                        sleep(10)
                    else:
                        sleep(frequency-tT)
                    i += 1
                    
        d.close() 
