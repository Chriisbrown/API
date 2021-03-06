# -*- coding: utf-8 -*-
"""
Created on Wed Aug 15 12:12:21 2018

@author: chris
"""

import time
import logging
#from time import sleep
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from w1thermsensor import W1ThermSensor

logging.basicConfig(filename='app.log', level=logging.INFO)
#Sets a logging file for any exceptiosns raised by the code

def datareading():
#Temperature probe management, this will not break and manages any exceptions, if the incorrect
    data = []
    for sensor in W1ThermSensor.get_available_sensors():
        data.append(sensor.get_temperature())
#For each available sensor the data from the sensor will be printed into the data list, this
#will cycle for as many sensors. The final insertion of the time ensures that the correct
#time corresponding to the final probe entering its data into the list is recorded
    return data

def inputno(input_type, input_text, lim1, lim2):
#This defines the function used to check user inputs are within range and of correct data type
    if input_type == 1:
        while True:
            try:
                input_number = int(input(input_text))
                if lim1 <= input_number <= lim2:
                    return input_number
                else:
                    time.sleep(0.033)
            except ValueError:
                time.sleep(0.033)
                continue
Menu = '0'
while Menu != 'q':
    Menu = input('Press b to begin log, press q to quit: ')
#Menu setup allowing the program to be run multiple times without turning the pi
#off
    now = datetime.datetime.now()
#Allows the backup file to be called todays date and time
    if Menu == 'b':
        test_number = str(inputno(1, 'Please enter the test number: ', 1, 10))
        test_name = input('Enter Name: ')
#Test number allows the data writing to happen to the correct columns to stop
#overwriting. Beyond 10 and google sheets will raise an error due to the sheet
#being too long
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('Client_temp.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Temperature Data").sheet1
#Opens the correct sheet and correct tab, if the sheet is changed this needs
#changing
        sheet.update_cell(1, 1+7*(int(test_number)-1), 'Test Number: '+test_number)
        sheet.update_cell(1, 2+7*(int(test_number)-1), test_name)
#Labels the data run with the number and specified name
        sheet.update_cell(2, 1+7*(int(test_number)-1), 'Time (s)')
        sheet.update_cell(2, 2+7*(int(test_number)-1), 'Temperature 1 (°C)')
        sheet.update_cell(2, 3+7*(int(test_number)-1), 'Temperature 2 (°C)')
        sheet.update_cell(2, 4+7*(int(test_number)-1), 'Temperature 3 (°C)')
        sheet.update_cell(2, 5+7*(int(test_number)-1), 'Temperature 4 (°C)')
        sheet.update_cell(2, 6+7*(int(test_number)-1), 'Temperature 5 (°C)')
#Names the columns with the correct headings and units.
        frequency = inputno(1, 'Period of data reading in seconds: ', 1, 100)
        length = int((inputno(1, 'Run test for how many minutes: ', 1, 1500))*60/frequency)
#Inputs the correct period of logging and how long the test is converted into
#a number of readings to be taken
        i = 3
        start_time = time.time()
#i is initialized as 3 to prevent the column headings being overwritten
        while i < length+3:
#Total main loop in which all readings occur
            try:
                time_1 = time.time()
                current_time = str(time.time() - start_time)
                (Temperature_1, Temperature_2, Temperature_3, Temperature_4,
                 Temperature_5) = datareading()
#Takes all readings, first checking if the VOC meter is functioning correctly
                try:
                    sheet.update_cell(i, 1+7*(int(test_number)-1), current_time)
                    sheet.update_cell(i, 2+7*(int(test_number)-1), Temperature_1)
                    sheet.update_cell(i, 3+7*(int(test_number)-1), Temperature_2)
                    sheet.update_cell(i, 4+7*(int(test_number)-1), Temperature_3)
                    sheet.update_cell(i, 5+7*(int(test_number)-1), Temperature_4)
                    sheet.update_cell(i, 6+7*(int(test_number)-1), Temperature_5)
#updates all the cells in turn
                except Exception as error_message:
                    logging.error('Error occurred in sheet updating' + str(error_message))
#logs any error due to not connecting to google sheets correctly

                with open('Tempdata'+now.strftime("%Y-%m-%d %H-%M")+'.txt', 'a+') as d:
                    data_string = ','.join(current_time, str(Temperature_1)
                                           , str(Temperature_2), str(Temperature_3)
                                           , str(Temperature_4), str(Temperature_5))
                    print(data_string)
                    print(data_string, file=d)
#writes data to the backup datafile seperated by a comma

                if i % (5*6)/frequency == 0:
                    try:
                        scope = ['https://spreadsheets.google.com/feeds',
                                 'https://www.googleapis.com/auth/drive']
                        creds = ServiceAccountCredentials.from_json_keyfile_name(
                            'Client_temp.json', scope)
                        client = gspread.authorize(creds)
                        sheet = client.open("Temperature Data").sheet1
                        print('Authenticating.....')
#reauthenticates the code so that google does not block the sheet request
                    except Exception as error_message:
                        logging.error('Error occurred in authentication' + str(error_message))
#If this fails, log the error

                time_2 = time.time()
                if frequency-(time_2-time_1) <= 0:
                    sleep(10)
#Calculates how long the taking of data and writing to google and ensures the
#frequency of readings doesn't drift. If less than 0 will check the reading
#didn't take longer than the period
                else:
                    sleep(frequency-(time_2-time_1))
                i += 1

            except Exception as error_message:
                logging.error('Error occurred in full code' + str(error_message))
                print('err', i)
#Any extra error will be caught by this logging system, and will rerun the
#content of the while loop
                sleep(10)
                i += 1
        d.close()
    if Menu == 'q':
        exit()
