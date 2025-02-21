"""
High-Speed Tensile Tester Data Collection and Calibration Script

This script collects and processes data from a high-speed tensile tester 
using a DAQ system. It includes calibration routines for an ultrasonic 
sensor and a load cell, as well as data acquisition and analysis.

This script was written as a part of MAE 4810 Capstone Senior Design
at Utah State University.

Author: Spencer Kenison 
Date Created: 2025-02-06
Last Modified: 2025-2-21
Version: 1.0.9  
License: NA
"""

#import necessary functions
import os; import json; import time; os.system('cls') #clear terminal
import numpy as np; import matplotlib.pyplot as plt; from numpy.polynomial.polynomial import Polynomial
from nptdms import TdmsFile; import nidaqmx
from datetime import datetime; from zoneinfo import ZoneInfo
from nidaqmx.constants import (READ_ALL_AVAILABLE,AcquisitionType,LoggingMode,LoggingOperation)
plt.rcParams['font.family'] = 'Times New Roman' #set desired font

default_config_json = {"DAQ_config":{"DAQ_name":"myDAQ1","load_cell_channel":"ai0","ultrasonic_channel":"ai1"},"test_config":{"sampling_rate_hz":1000,"min_sampling_rate_hz":1,"max_sampling_rate_hz":300000,"test_duration_ms":3000,"min_test_duration_ms":1,"max_test_duration_ms":10000},"load_cell":{"calibration_date":"2020-01-01T01:01:01.000001-07:00","calibration_masses_kg":[0,0.1,0.2,0.3,0.4,0.5],"calibration_voltages":[2.0, 2.125, 2.25, 2.375, 2.5, 2.625],"calibration_frequency_hz":100},"ultrasonic":{"calibration_date":"2020-01-01T01:01:01.000001-07:00","calibration_distances_m":[0.25,0.5,0.75,1,1.25],"calibration_voltages":[1,2.5,3.0,4.5,6.0],"calibration_frequency_hz":100}}

# Get inputs from .json file
try:
    with open('config.json') as f: config_data = json.load(f)  # Get calibration data from .json file
except FileNotFoundError: # Handle config.json not found
    print("Error: 'config.json' file not found. Creating config.json file using default settings."); time.sleep(3)
    config_data = default_config_json
    with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
except json.JSONDecodeError: # Handle config.json decode error
    print("Error: 'config.json' contains invalid JSON. Creating new config.json file using default settings."); time.sleep(3)
    config_data = default_config_json
    with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
    

# Function to edit settings
def settings():
    while True:
        os.system('cls') #clear terminal
        
        # Permenanent settings
        print("DAQ Settings: (edit config.json file to change)")
        print("  DAQ Name:",config_data['DAQ_config']['DAQ_name'])
        print("  Load Cell Channel:",config_data['DAQ_config']['load_cell_channel'])
        print("  Ultrasonic Channel:",config_data['DAQ_config']['ultrasonic_channel'])

        # Print options for user
        print("\nTensile Test Settings: (select option to edit or exit settings)")
        print("  1 - Test Frequency:", config_data['test_config']['sampling_rate_hz'], "Hz")
        print("  2 - Test Duration:", config_data['test_config']['test_duration_ms']/1000, "sec")
        print("  3 - Exit Settings")

        choice = input("Enter your choice (1/2/3): ").strip()

        # Edit Testing Frequency
        if choice == "1":
            while True:
                try:
                    new_frequency = int(input("\nEnter the desired test frequency in Hz: ")) # Get new test frequency from user
                    if config_data['test_config']['min_sampling_rate_hz'] <= new_frequency <= config_data['test_config']['max_sampling_rate_hz']: # Check that the frequency is in desired range
                        config_data['test_config']['sampling_rate_hz'] = new_frequency # Store entered frequency into internal config file
                        print("\nTest frequency has been updated\n"); time.sleep(1) # Print message and give user time to read it
                        with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
                        break
                    else:
                        print("\nInvalid frequency entered. Please enter a frequency between",config_data['test_config']['min_sampling_rate_hz'],"and",config_data['test_config']['max_sampling_rate_hz'], "Hz")
                except ValueError:
                    print("\nInvalid input. Please enter a valid integer.")
            
        # Edit Test Duration
        elif choice == "2":
            while True:
                try:
                    new_duration = int(input("\nEnter the desired test duration in ms: ")) # Get new test duration from user
                    if config_data['test_config']['min_test_duration_ms'] <= new_duration <= config_data['test_config']['max_test_duration_ms']: # Check that the duration is in desired range
                        config_data['test_config']['test_duration_ms'] = new_duration
                        print("\nTest duration has been updated\n"); time.sleep(1) # Print message and give user time to read it
                        with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
                        break
                    else:
                        print("\nInvalid duration entered. Please enter a duration between",config_data['test_config']['min_test_duration_ms'], "and",config_data['test_config']['max_test_duration_ms'],"ms")
                except ValueError:
                    print("\nInvalid input. Please enter a valid integer.")

        # Exit Settings Menu
        elif choice == "3":
            print("\nReturning to main menu.\n")
            break
        else: print("\nInvalid choice. Please enter 1, 2, or 3.\n") # Error if invalid choice is selected
    return 0

def moving_average(data, window_size):
    if window_size > len(data): raise ValueError("Window size cannot exceed data length.")
    if window_size <= 0: raise ValueError("Window size must be positive.")
      
    kernel = np.ones(window_size) / window_size
    smoothed_data = np.convolve(data, kernel, mode='same')
    return smoothed_data

#function to calibrate ultrasonic sensor
def calibrate_ultrasonic():
    os.system('cls') #clear terminal
    print("Calibrating ultrasonic sensor.")
    
    for i in range(len(config_data['ultrasonic']['calibration_distances_m'])):
        while True:
            print("\nPlace object",config_data['ultrasonic']['calibration_distances_m'][i]*1000,"mm away from ultrasonic sensor.")
            choice = input("Press 'y' when ready or 'c' to cancel: ").strip()
            
            # get 1 second of data from DAQ for calibration
            if choice in ['y', 'Y']: 
                with nidaqmx.Task() as task:
                    freq = np.round(config_data['ultrasonic']['calibration_frequency_hz']).astype(int) #get desired frequency from input file
                    task.ai_channels.add_ai_voltage_chan("myDAQ1/ai1") #create task to record ultrasonic voltage
                    task.timing.cfg_samp_clk_timing(freq, samps_per_chan=freq) #configure task frequency and number of samples
                    calib_val = np.median(np.array(task.read(freq))) #set calibration voltage to median of collected data
                    config_data['ultrasonic']['calibration_voltages'][i] = calib_val #store calibration voltage to .json file
                    print('Voltage Recorded = ', calib_val, 'V') #print median recorded voltage to screen for reference
                break
            elif choice in ['c','C']: print('\nCalibration cancelled.\n');return 0
            else: print("\nError. Please press 'y' to confirm or 'c' to cancel.")

    #close out ultrasonic sensor calibration
    print("\nUltrasonic sensor calibration complete.\n") 
    config_data['ultrasonic']['calibration_date'] = datetime.now(ZoneInfo("America/Denver")).isoformat() # Update the date in the JSON data
    with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
    return 0

def calibrate_load_cell():
    os.system('cls') #clear terminal
    print("Calibrating load cell.\nPosition load cell in vertical orientation.")
    
    for i in range(len(config_data['load_cell']['calibration_masses_kg'])):
        while True:
            print("\nPlace",config_data['load_cell']['calibration_masses_kg'][i]*1000,"g on load cell.")
            choice = input("Press 'y' when ready or 'c' to cancel: ").strip()
            
            # get 1 second of data from DAQ for calibration
            if choice in ['y', 'Y']: 
                with nidaqmx.Task() as task:
                    freq = np.round(config_data['load_cell']['calibration_frequency_hz']).astype(int) #get desired frequency from input file
                    task.ai_channels.add_ai_voltage_chan("myDAQ1/ai0") #create task to record load cell voltage
                    task.timing.cfg_samp_clk_timing(freq, samps_per_chan=freq) #configure task frequency and number of samples
                    calib_val = np.median(np.array(task.read(freq))) #set calibration voltage to median of collected data
                    config_data['load_cell']['calibration_voltages'][i] = calib_val #store calibration voltage to .json file
                    print('Voltage Recorded = ', calib_val, 'V') #print median recorded voltage to screen for reference
                break
            elif choice in ['c','C']: print('\nCalibration cancelled.\n');return 0
            else: print("\nError. Please press 'y' to confirm or 'c' to cancel.")

    #close out ultrasonic sensor calibration
    print("\nLoad cell calibration complete.\n") 
    config_data['load_cell']['calibration_date'] = datetime.now(ZoneInfo("America/Denver")).isoformat() # Update the date in the JSON data
    with open('config.json', 'w') as f: json.dump(config_data, f, indent=4) # Write the updated JSON data back to the file
    return 0

def calibrate():
    os.system('cls') #clear terminal
    print("Calibration selected.\n")
    
    # Convert ISO 8601 string to datetime object
    load_cell_date = datetime.fromisoformat(config_data['load_cell']['calibration_date'].replace("-7:00", ""))
    ultrasonic_date = datetime.fromisoformat(config_data['ultrasonic']['calibration_date'].replace("-7:00", ""))
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
        if choice == "1": calibrate_load_cell()

        # Ultrasonic Calibration
        elif choice == "2": calibrate_ultrasonic()

        # Exit Calibration Menu
        elif choice == "3":
            print("\nReturning to main menu.\n")
            break

        else: print("\nInvalid choice. Please enter 1, 2, or 3.\n")
    return 0

def collect_data():

    # Define parameters
    sampling_rate = config_data['test_config']['sampling_rate_hz']  # Hz
    test_duration_ms = config_data['test_config']['test_duration_ms']  # Total duration in milliseconds
    num_samples = int((sampling_rate * test_duration_ms) / 1000)  # Convert duration to number of samples
    test_duration = test_duration_ms / 1000  # Convert to seconds
    print('Running tensile test with',sampling_rate,'Hz sampling rate for',test_duration,'s') #Print current settings to screen
    load_cell_channel = config_data['DAQ_config']['DAQ_name']+"/"+config_data['DAQ_config']['load_cell_channel'] # Create variable to for NIDAQmx to reference
    ultrasonic_channel = config_data['DAQ_config']['DAQ_name']+"/"+config_data['DAQ_config']['ultrasonic_channel'] # Create variable to for NIDAQmx to reference

    # Acquire and log data
    with nidaqmx.Task() as task:
        task.ai_channels.add_ai_voltage_chan(load_cell_channel) #collect load cell data
        task.ai_channels.add_ai_voltage_chan(ultrasonic_channel)  #collect ultraonic sensor data
        task.timing.cfg_samp_clk_timing(sampling_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=num_samples)
        task.in_stream.configure_logging(
            "TestData.tdms", LoggingMode.LOG_AND_READ, operation=LoggingOperation.CREATE_OR_REPLACE
        )
        task.read(READ_ALL_AVAILABLE)

    # Read data from TDMS file and plot
    with TdmsFile.open("TestData.tdms") as tdms_file:
        group = tdms_file.groups()[0]  # Get the first (and only) group
        raw_load_cell_data = np.array(group[load_cell_channel][:])
        raw_ultrasonic_data = np.array(group[ultrasonic_channel][:])
        time = np.linspace(0, test_duration, num_samples)

    # Cleanup TDMS files
    for file in ["TestData.tdms", "TestData.tdms_index"]:
        if os.path.exists(file):
            os.remove(file)

    # Calculate line of best fits to interpret data based off of calibration
    f_load_cell = Polynomial.fit(np.array(config_data['load_cell']['calibration_voltages']),np.array(config_data['load_cell']['calibration_masses_kg'])*9.8, deg=1) #added factor to account for gravity (kg > N)
    f_ultrasonic = Polynomial.fit(np.array(config_data['ultrasonic']['calibration_voltages']), np.array(config_data['ultrasonic']['calibration_distances_m']), deg=1)
    load_cell_data = f_load_cell(raw_load_cell_data)
    load_cell_data = load_cell_data-np.mean(load_cell_data[0:10])
    load_cell_data = moving_average(load_cell_data,5) #slightly smooth out load cell data to account for oscillations
    ultrasonic_data = f_ultrasonic(raw_ultrasonic_data)

    # Print data to terminal
    print('\nTest Complete.\n')
    print('Max Force = ', np.max(load_cell_data))
    print('Max Displacement = ', ultrasonic_data[np.argmax(load_cell_data)])
    print('\nClose all plots to resume program.\n')

    return load_cell_data, ultrasonic_data, time  # Return as a tuple

def plot_data(load_cell_data, ultrasonic_data, time):

    # Create the figure and first axis
    fig, ax1 = plt.subplots(figsize=(8, 4))
    
    # Plot the first dataset (Force) on the primary y-axis
    ax1.plot(time, load_cell_data, label="Force (N)", color='b')
    ax1.set_xlabel("Time (s)")
    ax1.set_ylabel("Force (N)", color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    
    # Create a second y-axis sharing the same x-axis
    ax2 = ax1.twinx()
    ax2.plot(time, ultrasonic_data, label="Distance (m)", color='r')
    ax2.set_ylabel("Distance (m)", color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    # Title and grid
    plt.title("High-Speed Tensile Tester Data")
    ax1.grid(True)
    
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

def export_data(load_cell_data, ultrasonic_data, time):
    return 0

def tensile_test():
    os.system('cls') #clear terminal
    print("Test selected. Proceeding with data collection...\n")
    
    load_cell_data, ultrasonic_data, time = collect_data() #Call function to collect data 
    
    plot_data(load_cell_data, ultrasonic_data, time) #Call function to visualize data
    export_data(load_cell_data, ultrasonic_data, time) #Call function to export data
    
    return 0

# Main Menu Selection
while True:
    os.system('cls') #clear terminal
    print("Welcome to the High-Speed Tensile Tester.\n")
    print("Select an option:"); print("1 - Tensile Testing"); print("2 - Calibration"); print("3 - Settings"); print("4 - Exit Program")
    choice = input("Enter your choice (1/2/3/4): ").strip()
    
    # Main Menu Options
    if choice == "1": tensile_test()
    elif choice == "2": calibrate()
    elif choice == "3": settings()
    elif choice == "4": print("\nExiting program.\n"); exit()
    else: print("\nInvalid choice. Please enter 1, 2, or 3.\n")
