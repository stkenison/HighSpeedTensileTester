"""
High-Speed Tensile Tester Data Collection and Calibration Script

This script collects and processes data from a high-speed tensile tester 
using a DAQ system. It includes calibration routines for an ultrasonic 
sensor and a load cell, as well as data acquisition and analysis.

This script was written as a part of MAE 4810 Capstone Senior Design
at Utah State University.

Author: Spencer Kenison 
Date Created: 2025-02-06
Last Modified: 2025--2-13 
Version: 1.0  
License: MIT License
"""

#import necessary functions
import os; import json; os.system('cls') #clear terminal
import numpy as np; import matplotlib.pyplot as plt; from numpy.polynomial.polynomial import Polynomial
from nptdms import TdmsFile; import nidaqmx
from datetime import datetime; from zoneinfo import ZoneInfo
from nidaqmx.constants import (READ_ALL_AVAILABLE,AcquisitionType,LoggingMode,LoggingOperation)
plt.rcParams['font.family'] = 'Times New Roman' #set desired font

#get inputs from .json file
with open('input.json') as f: input_data = json.load(f) #get input data from .json file
with open('calibration.json') as f: calibration_data = json.load(f) #get calibration data from .json file

#function to calibrate ultrasonic sensor
def calibrate_ultrasonic():
    
    print("\nCalibrating ultrasonic sensor.")
    
    for i in range(len(calibration_data['ultrasonic']['calibration_distances_m'])):
        while True:
            print("\nPlace object",calibration_data['ultrasonic']['calibration_distances_m'][i]*1000,"mm away from ultrasonic sensor.")
            choice = input("Press 'y' when ready or 'c' to cancel: ").strip()
            
            # get 1 second of data from DAQ for calibration
            if choice in ['y', 'Y']: 
                with nidaqmx.Task() as task:
                    freq = np.round(calibration_data['ultrasonic']['calibration_frequency_hz']).astype(int) #get desired frequency from input file
                    task.ai_channels.add_ai_voltage_chan("myDAQ1/ai1") #create task to record ultrasonic voltage
                    task.timing.cfg_samp_clk_timing(freq, samps_per_chan=freq) #configure task frequency and number of samples
                    calib_val = np.median(np.array(task.read(freq))) #set calibration voltage to median of collected data
                    calibration_data['ultrasonic']['calibration_voltages'][i] = calib_val #store calibration voltage to .json file
                    print('Voltage Recorded = ', calib_val, 'V') #print median recorded voltage to screen for reference
                break
            elif choice in ['c','C']: print('\nCalibration cancelled.\n');return 0
            else: print("\nError. Please press 'y' to confirm or 'c' to cancel.")

    #close out ultrasonic sensor calibration
    print("\nUltrasonic sensor calibration complete.\n") 
    calibration_data['ultrasonic']['date'] = datetime.now(ZoneInfo("America/Denver")).isoformat() # Update the date in the JSON data
    with open('calibration.json', 'w') as f: json.dump(calibration_data, f, indent=4) # Write the updated JSON data back to the file
    return 0

def calibrate_load_cell():

    print("\nCalibrating load cell.\nPosition load cell in verticl orientation.")
    
    for i in range(len(calibration_data['load_cell']['calibration_masses_kg'])):
        while True:
            print("\nPlace",calibration_data['load_cell']['calibration_masses_kg'][i]*1000,"g on load cell.")
            choice = input("Press 'y' when ready or 'c' to cancel: ").strip()
            
            # get 1 second of data from DAQ for calibration
            if choice in ['y', 'Y']: 
                with nidaqmx.Task() as task:
                    freq = np.round(calibration_data['load_cell']['calibration_frequency_hz']).astype(int) #get desired frequency from input file
                    task.ai_channels.add_ai_voltage_chan("myDAQ1/ai1") #create task to record load cell voltage
                    task.timing.cfg_samp_clk_timing(freq, samps_per_chan=freq) #configure task frequency and number of samples
                    calib_val = np.median(np.array(task.read(freq))) #set calibration voltage to median of collected data
                    calibration_data['load_cell']['calibration_voltages'][i] = calib_val #store calibration voltage to .json file
                    print('Voltage Recorded = ', calib_val, 'V') #print median recorded voltage to screen for reference
                break
            elif choice in ['c','C']: print('\nCalibration cancelled.\n');return 0
            else: print("\nError. Please press 'y' to confirm or 'c' to cancel.")

    #close out ultrasonic sensor calibration
    print("\nLoad cell calibration complete.\n") 
    calibration_data['load_cell']['date'] = datetime.now(ZoneInfo("America/Denver")).isoformat() # Update the date in the JSON data
    with open('calibration.json', 'w') as f: json.dump(calibration_data, f, indent=4) # Write the updated JSON data back to the file
    return 0

def calibrate():
    print("\nCalibration selected.\n")
    
    # Convert ISO 8601 string to datetime object
    load_cell_date = datetime.fromisoformat(calibration_data['load_cell']['date'].replace("-7:00", ""))
    ultrasonic_date = datetime.fromisoformat(calibration_data['ultrasonic']['date'].replace("-7:00", ""))
    # Print formatted dates
    print("Load cell calibration last performed:", load_cell_date.strftime("%Y-%m-%d %H:%M:%S"))
    print("Ultrasonic sensor calibration last performed:", ultrasonic_date.strftime("%Y-%m-%d %H:%M:%S"), "\n")

    while True:
        print("Select an option:")
        print("1 - Calibrate Load Cell")
        print("2 - Calibrate Ultrasonic Sensor")
        print("3 - Exit Calibration")

        choice = input("Enter your choice (1/2/3): ").strip()

        # Load Cell Calibration
        if choice == "1":
            calibrate_load_cell()

        # Ultrasonic Calibration
        elif choice == "2":
            calibrate_ultrasonic()

        # Exit Calibration Menu
        elif choice == "3":
            print("\nReturning to main menu.\n")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, or 3.\n")
    return 0

def collect_data():
    print("\nTest selected. Proceeding with data collection...\n")

    # Define parameters
    sampling_rate = input_data['sampling_rate_hz']  # Hz
    test_duration_ms = input_data['test_duration_ms']  # Total duration in milliseconds
    num_samples = int((sampling_rate * test_duration_ms) / 1000)  # Convert duration to number of samples
    test_duration = test_duration_ms / 1000  # Convert to seconds
    print('Running Testing with',sampling_rate,'Hz sampling rate for',test_duration,'s')

    # Acquire and log data
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan("myDAQ1/ai0")
        task.ai_channels.add_ai_voltage_chan("myDAQ1/ai1")  # Added AI1
        task.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=num_samples)
        task.in_stream.configure_logging(
            "TestData.tdms", LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE
        )
        task.read(READ_ALL_AVAILABLE)

    # Read data from TDMS file and plot
    with TdmsFile.open("TestData.tdms") as tdms_file:
        group = tdms_file.groups()[0]  # Get the first (and only) group
        ai0_data = np.array(group['myDAQ1/ai0'][:])
        ai1_data = np.array(group['myDAQ1/ai1'][:])
        time = np.linspace(0, test_duration, num_samples)

    # Cleanup TDMS files
    for file in ["TestData.tdms", "TestData.tdms_index"]:
        if os.path.exists(file):
            os.remove(file)

    # Calculate line of best fits to interpret data based off of calibration
    f_load_cell = Polynomial.fit(np.array(calibration_data['load_cell']['calibration_masses_kg'])*9.81, np.array(calibration_data['load_cell']['calibration_voltages']), deg=1) #added factor to account for gravity
    f_ultrasonic = Polynomial.fit(np.array(calibration_data['ultrasonic']['calibration_distances_m']), np.array(calibration_data['ultrasonic']['calibration_voltages']), deg=1)
    load_cell_data = f_load_cell(ai0_data)*9.81
    ultrasonic_data = f_ultrasonic(ai1_data)

    # Print data to terminal
    print('\nTest Complete.\n')
    print('Max Force = ', np.max(load_cell_data))
    print('Max Displacement = ', ultrasonic_data[np.argmax(load_cell_data)])
    print('\nClose all plots to resume program.\n')

    # Plot the data over time and configure figure
    plt.figure('Time-Based Plot', figsize=(8, 4))
    plt.plot(time, load_cell_data, label="Force (N)", color='b')
    plt.plot(time, ultrasonic_data, label="Distance (m)", color='r')
    plt.xlabel("Time (s)")
    #plt.ylabel("Voltage (V)")
    plt.title("High-Speed Tensile Tester Data")
    plt.legend()
    plt.grid(True)

    #plot force over distance data and configure figure
    plt.figure('Force Over Distance', figsize=(8, 4))
    plt.plot(ultrasonic_data, load_cell_data, label="Force (N)", color='b')
    plt.xlabel("Distance(m)")
    plt.ylabel("Force (N)")
    plt.title("High-Speed Tensile Tester Data")
    plt.legend()
    plt.grid(True)

    plt.show()
    return 0

# Main Menu Selection
while True:
    print("Select an option:"); print("1 - Test"); print("2 - Calibration"); print("3 - Exit Program")
    choice = input("Enter your choice (1/2/3): ").strip()
    
    # Main Menu Options
    if choice == "1": collect_data()
    elif choice == "2": calibrate()
    elif choice == "3": print("\nExiting program.\n"); exit()
    else: print("\nInvalid choice. Please enter 1, 2, or 3.\n")



