# High-Speed Tensile Tester Data Collection and Calibration

## Introduction
This Python script is designed to collect and process data from a high-speed tensile testing setup using an NI myDAQ system. The script allows users to calibrate ultrasonic and load cell sensors, perform tensile tests, and visualize the collected data through plots.

The program follows a structured workflow:
- **Calibration**: Guides the user through calibrating the ultrasonic sensor and load cell.
- **Data Collection**: Records high-speed tensile test data using NI DAQ and processes it for analysis.
- **Data Visualization**: Plots force versus displacement and time-based sensor readings.

## Features
- Supports **NI myDAQ** for high-speed data acquisition
- Calibration functions for **ultrasonic sensor** and **load cell**
- Saves calibration settings to **JSON files**
- Uses **polynomial fitting** to convert raw sensor data to meaningful force and displacement values
- Plots data in real-time using **Matplotlib**

## Dependencies
Ensure you have the following Python libraries installed:
```bash
pip install numpy matplotlib nptdms nidaqmx
```
The script also uses standard Python libraries such as `os`, `json`, and `datetime`.

## Installation and Setup

### 1. Download Drivers
Download the NI myDAQ drivers from the National Instruments website:  
[NI myDAQ Software Suite](https://www.ni.com/en/support/downloads/software-products/download.mydaq-software-suite.html#305519)

### 2. Hardware Connection
Connect your **NI myDAQ** device to your computer via USB.

### 3. Clone the Repository
```bash
git clone https://github.com/yourusername/high-speed-tensile-tester.git
cd high-speed-tensile-tester
```

### 4. (Optional but Recommended) Create a Virtual Environment
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

### 5. Install Dependencies
```bash
pip install -r requirements.txt
```

## Usage

### Running the Script
To run the main program:
```bash
py main.py
```

You will be presented with a menu:
1. **Test**: Start data collection.
2. **Calibration**: Calibrate the sensors.
3. **Exit Program**: Close the application.

### Calibration
Select **Calibration** to perform calibration procedures:
- **Ultrasonic Sensor**: Set known distances.
- **Load Cell**: Place known weights for force calibration.

Calibration data is saved to `config.json` for later use.

### Data Collection
After initiating a tensile test:
- Data is collected using the NI myDAQ and stored in a temporary TDMS file (`TestData.tdms`)
- Polynomial fits are applied to sensor readings
- The script plots:
  - **Force and Distance vs. Time**
  - **Force vs. Distance**

### Data Storage
- `config.json`: Stores test parameters and calibration data
- `TestData.tdms`: Temporary TDMS data file used during analysis

## File Structure
```
├── main.py             # Main script
├── config.json         # Sensor calibration and DAQ settings
├── README.md           # Project documentation
└── requirements.txt    # List of dependencies
```

## Future Improvements
- Develop a GUI for simplified user interaction
- Enhance real-time plotting and analysis features

## Contact
For questions or contributions, please contact **spencer.kenison@gmail.com**.
