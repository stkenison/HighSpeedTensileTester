# High-Speed Tensile Tester Data Collection and Calibration

## Introduction
This Python script is designed to collect and process data from a high-speed tensile testing setup using an NI DAQ system. The script allows users to calibrate ultrasonic and load cell sensors, perform tensile tests, and visualize the collected data through plots.

The program follows a structured workflow:
- **Calibration**: Guides the user through calibrating the ultrasonic sensor and load cell.
- **Data Collection**: Records high-speed tensile test data using NI DAQ and processes it for analysis.
- **Data Visualization**: Plots force versus displacement and time-based sensor readings.

## Features
- Supports **NI DAQ** for high-speed data acquisition
- Calibration functions for **ultrasonic sensor** and **load cell**
- Saves calibration settings to **JSON files**
- Uses **polynomial fitting** to convert raw sensor data to meaningful force and displacement values
- Plots data in real-time using **Matplotlib**

## Dependencies
Ensure you have the following dependencies installed:
```bash
pip install numpy matplotlib nptdms nidaqmx
```
The script also uses built-in Python libraries such as `os`, `json`, and `datetime`.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/yourusername/high-speed-tensile-tester.git
```
2. Navigate to the project directory:
```bash
cd high-speed-tensile-tester
```
3. Install dependencies as listed above.

## Usage
Run the script using:
```bash
python main.py
```
Upon execution, you will be presented with a menu:
1. **Test**: Initiates the data collection process.
2. **Calibration**: Allows calibration of ultrasonic and load cell sensors.
3. **Exit Program**: Exits the script.

### Calibration
For accurate data collection, perform sensor calibration by selecting **Calibration** from the main menu. The script will prompt you to place known weights on the load cell and set distances for the ultrasonic sensor.

### Data Collection
The script reads sensor data at the specified sampling rate and duration, stores it in a TDMS file, and processes it to extract force and displacement values. It then generates two plots:
- **Time-based data** (Force and Distance over time)
- **Force vs. Distance**

### Data Storage
- `config.json` stores test parameters like sampling rate and duration and sensor calibration data.
- `TestData.tdms` is a temporary file for logged data.

## File Structure
```
├── main.py             # Main script
├── config.json         # DAQ settings, tensile test settings, and sensor calibration data
├── README.md           # Project documentation
└── requirements.txt    # List of dependencies
```

## Future Improvements
- Implement data saving and export to CSV format
- Add GUI for easier user interaction
- Improve real-time visualization during data collection

## License
This project is licensed under the MIT License. See `LICENSE` for details.

## Contact
For questions or contributions, contact spencer.kenison@gmail.com or open an issue on GitHub.

