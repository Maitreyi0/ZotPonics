from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file
from Status import Status
#from AtlasI2C_Sensor import AtlasI2C_Sensor
#from pPump import PeristalticPump
import time
import random
import threading as th
from CircularBuffer import CircularBuffer
from MYSQL import (
    retrieve_most_recent_pH,
    retrieve_most_recent_ec,
    retrieve_most_recent_mode,
    retrieve_most_recent_pump
)
import matplotlib
from matplotlib import pyplot as plt
import os

matplotlib.use('Agg')  # Set backend to Agg for non-GUI rendering

mode = True
# Temporary classes - REMOVE WHEN TESTING
class MockAtlasI2C_Sensor:
    def __init__(self, keyword: str, writeDataToCSV: bool, debugMode: bool, contPollThreadIndependent: bool, isOutermostEntity: bool):
        self.status = Status(isOutermostEntity, debugMode)
        self.status.addStatusFieldTuple("keyword", keyword)
        self.status.addStatusFieldTuple("latestReading", None)
        self.status.addStatusFieldTuple("contPollingThreadActive", False)

        self.deviceKeyword = keyword
        self.polling_thread = None



class MockPeristalticPump:
    def __init__(self, pin, alias, isOutermostEntity, debugMode):
        self.status = Status(isOutermostEntity, debugMode)
        self.status.addStatusFieldTuple("alias", alias)
        self.status.addStatusFieldTuple("pin", pin)
        self.status.addStatusFieldTuple("pumpActive", False)
        self.status.addStatusFieldTuple("activeDescription", "Off")

        self.alias = alias
        self.debugMode = debugMode
        self.duration_thread = None

    def turnOn(self):
        if not self.status.getStatusFieldTupleValueUsingKey("pumpActive"):
            self.status.setStatusFieldTupleValue("pumpActive", True)
            self.status.setStatusFieldTupleValue("activeDescription", "On, with no set duration")
            if self.debugMode:
                print(f"{self.alias} turned on.")
        else:
            if self.debugMode:
                print(f"{self.alias} is already on.")

    def turnOff(self):
        if self.status.getStatusFieldTupleValueUsingKey("pumpActive"):
            self.status.setStatusFieldTupleValue("pumpActive", False)
            self.status.setStatusFieldTupleValue("activeDescription", "Off")
            if self.debugMode:
                print(f"{self.alias} turned off.")
        else:
            if self.debugMode:
                print(f"{self.alias} is already off.")

    def turnOnWithDuration(self, seconds):
        if not self.status.getStatusFieldTupleValueUsingKey("pumpActive"):
            self.status.setStatusFieldTupleValue("pumpActive", True)
            self.status.setStatusFieldTupleValue("activeDescription", f"On, with duration of {seconds} seconds")
            if self.debugMode:
                print(f"{self.alias} turned on for {seconds} seconds.")

            self.duration_thread = th.Thread(target=self._run_for_duration, args=(seconds,))
            self.duration_thread.start()
        else:
            if self.debugMode:
                print(f"{self.alias} is already on and cannot start again with a duration.")

    def _run_for_duration(self, seconds):
        time.sleep(seconds)
        self.turnOff()

# Generates a 2D line plot from the buffer data and saves it as an image
def generate_plot(buffer, filename, label):
    values = buffer.getCB_Values()
    plt.figure(figsize=(8, 4))
    plt.plot(range(1, len(values) + 1), values, marker='o', linestyle='-', color='b')
    plt.xlabel("Sample Index")
    plt.ylabel(label)
    plt.title(f"{label} Readings Over Time")

    # Save plot as an image in the plotImages directory within hardwareCode
    filepath = os.path.join(plot_images_dir, filename)
    plt.savefig(filepath)
    plt.close()
    return filepath


app = Flask(__name__)

# Create a global instance of the Status class
system_status = Status(isTopLevel=True, debugMode=False)

# Specify the directory path for hardwareCode and plotImages
hardware_code_dir = os.path.join(os.getcwd(), "hardwareCode")
plot_images_dir = os.path.join(hardware_code_dir, "plotImages")

# Ensure the plotImages directory exists within hardwareCode
os.makedirs(plot_images_dir, exist_ok=True)

# Initialize the circular buffers for pH and EC sensor readings
ph_buffer = CircularBuffer(size=50)  # Stores the latest 50 pH readings
ec_buffer = CircularBuffer(size=50)  # Stores the latest 50 EC readings

# Temporary - REMOVE WHEN TESTING
ph_sensor = MockAtlasI2C_Sensor(
    keyword="pH", writeDataToCSV=False, debugMode=False,
    contPollThreadIndependent=True, isOutermostEntity=True
)
ec_sensor = MockAtlasI2C_Sensor(
    keyword="EC", writeDataToCSV=False, debugMode=False,
    contPollThreadIndependent=True, isOutermostEntity=True
)
pump = MockPeristalticPump(pin=20, alias="MainPump", isOutermostEntity=True, debugMode=False)
pHStatus = Status(isTopLevel=True, debugMode=False)
ECStatus = Status(isTopLevel=True, debugMode=False)


pHStatus.addStatusFieldTuple("pumpActive", "OFF")

# Route for main menu
@app.route('/')
def index():
    return render_template('main_menu.html')


# Route to get the current status of the system
@app.route('/status', methods=['GET'])
def get_status():
    try:
        # Retrieve the most recent values from the database
        ph_latest_reading = retrieve_most_recent_pH()
        ec_latest_reading = retrieve_most_recent_ec()
        mode = retrieve_most_recent_mode()
        pump_active = retrieve_most_recent_pump()

        # Create the response dictionary
        pump_status_info = {
            "pH Sensor Latest Reading": ph_latest_reading,
            "EC Sensor Latest Reading": ec_latest_reading,
            "Mode": mode,
            "Pump Active": pump_active
        }

        return jsonify(pump_status_info)  # Return as JSON

    except Exception as e:
        return jsonify({"error": str(e)})

# Route to render the status information on an HTML page
@app.route('/status/html', methods=['GET'])
def get_system_status_html():
    global system_status
    try:
        ph_latest_reading = retrieve_most_recent_pH()
        ec_latest_reading = retrieve_most_recent_ec()
        mode = retrieve_most_recent_mode()
        pump_active = retrieve_most_recent_pump()
        return render_template(
            "status.html",
            mode=mode,
            ph_latest_reading=ph_latest_reading,
            ec_latest_reading=ec_latest_reading,
            pump_active=pump_active,
        )
    except Exception as e:
        return f"Error: {str(e)}"

# Route to render a form that will allow the user to manually override the system
@app.route('/form')
def form():
    return render_template('input_form.html')

# Route to submit the form
@app.route('/submit', methods=['POST'])
def submit_form():
    pump_action = request.form.get('pump')
    duration = request.form.get('duration')
    new_mode = request.form.get('mode')

    try:
        # Handle pump action
        if pump_action == "on":
            pump.turnOn()
        elif pump_action == "off":
            pump.turnOff()
        elif pump_action == "on_with_duration" and duration:
            pump.turnOnWithDuration(int(duration))

        # Handle mode change
        global mode
        if new_mode:
            if new_mode in ["automatic", "manual"]:
                mode = new_mode

        return redirect(url_for('get_system_status_html'))
    except Exception as e:
        return f"Error: {str(e)}", 400

@app.route('/generate_ph_plot')
def generate_ph_plot():
    # Simulate adding a new random pH reading to the buffer - REMOVE WHEN TESTING
    new_ph_value = random.uniform(5.0, 8.0)
    ph_buffer.add(new_ph_value)

    ''' Add this code when testing with system
    new_ph_value = ec_sensor.status.getStatusFieldTupleValue("latestReading")

    if new_ec_value is not None:
        ph_buffer.add(new_ec_value)
    '''

    # Generate a plot from the buffer and save it as an image
    ph_image_path = generate_plot(ph_buffer, "ph_plot.png", "pH")

    # Display the image to the front end
    return send_file(ph_image_path, mimetype='image/png')

@app.route('/generate_ec_plot')
def generate_ec_plot():
    # Simulate adding a new random EC reading to the buffer - REMOVE WHEN TESTING
    new_ec_value = random.uniform(500, 1500)
    ec_buffer.add(new_ec_value)

    ''' Add this code when testing with system
    new_ec_value = ec_sensor.status.getStatusFieldTupleValue("latestReading")

    if new_ec_value is not None:
        ec_buffer.add(new_ec_value)
    '''

    # Generate a plot from the buffer and save it as an image
    ec_image_path = generate_plot(ec_buffer, "ec_plot.png", "EC")

    # Display the image to the front end
    return send_file(ec_image_path, mimetype='image/png')

# Route to render the front end page displaying the plots
@app.route('/telemetry')
def telemetry():
    return render_template('telemetry.html')

mode = "automatic"

@app.route('/mode', methods=['GET'])
def get_mode():
    """Route to get the current mode."""
    global mode
    return jsonify({"mode": mode})

@app.route('/mode/set', methods=['POST'])
def set_mode():
    """Route to set the mode."""
    global mode
    new_mode = request.form.get('mode')
    if new_mode in ["automatic", "manual"]:
        mode = new_mode
        return jsonify({"status": "success", "mode": mode})
    else:
        return jsonify({"status": "error", "message": "Invalid mode"}), 400

# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)



