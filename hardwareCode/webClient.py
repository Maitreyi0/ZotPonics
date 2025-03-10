from flask import Flask, jsonify, request, render_template, redirect, url_for, send_file
from Status import Status
import random
from CircularBuffer import CircularBuffer
from MYSQL import (
    insert_pH_data,
    insert_ec_data,
    insert_mode,
    insert_pump,
    insertRequest,
    retrieve_most_recent_pH,
    retrieve_most_recent_ec,
    retrieve_most_recent_mode,
    retrieve_most_recent_pump,
    retrieve_most_recent_pump_activity,
    retrieve_most_recent_pPump_activity,
    retrieve_most_recent_pHUpPump,
    retrieve_most_recent_pHDownPump,
    retrieve_most_recent_baseA_Pump,
    retrieve_most_recent_baseB_Pump,
    ##START OF TEST CODE##
    retrieve_all_pH_values,
    retrieve_all_ec_values
    ##END OF TEST CODE##

)
import matplotlib
from matplotlib import pyplot as plt
import os

matplotlib.use('Agg')  # Set backend to Agg for non-GUI rendering

mode = True

'''
Commands to insert:
-grow light on
-grow light off
-camera move left
-camera move right
'''

# Generates a 2D line plot from the buffer data and saves it as an image
def generate_plot(buffer, filename, label):
    #values = buffer.getCB_Values()

    if buffer == 0:
        values = retrieve_all_pH_values()
    else:
        values = retrieve_all_ec_values()


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
system_status = Status(topLevel=True, debugMode=False)

# Specify the directory path for hardwareCode and plotImages
hardware_code_dir = os.path.join(os.getcwd(), "hardwareCode")
plot_images_dir = os.path.join(hardware_code_dir, "plotImages")

# Ensure the plotImages directory exists within hardwareCode
os.makedirs(plot_images_dir, exist_ok=True)

# Initialize the circular buffers for pH and EC sensor readings
ph_buffer = CircularBuffer(size=50)  # Stores the latest 50 pH readings
ec_buffer = CircularBuffer(size=50)  # Stores the latest 50 EC readings


# Route for main menu
@app.route('/')
def index():
    return render_template('main_menu.html')


# Route to get the current status of the system
@app.route('/status', methods=['GET'])
def get_status():
    try:
        # Retrieve the most recent values from the database
        ph_latest_reading = retrieve_most_recent_pH(with_timestamp=True)
        ec_latest_reading = retrieve_most_recent_ec(with_timestamp=True)

        mode = retrieve_most_recent_mode(with_timestamp=True)

        pump_activity = retrieve_most_recent_pump_activity()
        pPump_activity = retrieve_most_recent_pPump_activity()

        pHUpPump_latest_reading = retrieve_most_recent_pHUpPump(with_timestamp=True)
        pHDownPump_latest_reading = retrieve_most_recent_pHDownPump(with_timestamp=True)
        baseA_Pump_latest_reading = retrieve_most_recent_baseA_Pump(with_timestamp=True)
        baseB_Pump_latest_reading = retrieve_most_recent_baseB_Pump(with_timestamp=True)

        # Create the response dictionary
        pump_status_info = {
            "pH Sensor Latest Reading": ph_latest_reading[0],
            "pH Timestamp": ph_latest_reading[1],
            "EC Sensor Latest Reading": ec_latest_reading[0],
            "EC Timestamp": ec_latest_reading[1],
            "Mode": mode[0],
            "Mode Timestamp": mode[1],
            "pHUpPump Latest Reading": pHUpPump_latest_reading[0],
            "pHUpPump Timestamp": pHUpPump_latest_reading[1],
            "pHDownPump Latest Reading": pHDownPump_latest_reading[0],
            "pHDownPump Timestamp": pHDownPump_latest_reading[1],
            "BaseA Pump Latest Reading": baseA_Pump_latest_reading[0],
            "BaseA Pump Timestamp": baseA_Pump_latest_reading[1],
            "BaseB Pump Latest Reading": baseB_Pump_latest_reading[0],
            "BaseB Pump Timestamp": baseB_Pump_latest_reading[1]
        }

        if pump_activity:
            pump_status_info.update(pump_activity)


        return jsonify(pump_status_info)  # Return as JSON

    except Exception as e:
        return jsonify({"error": str(e)})


# Route to render the status information on an HTML page
@app.route('/status/html', methods=['GET'])
def get_system_status_html():
    global system_status
    try:
        ph_latest_reading = retrieve_most_recent_pH(with_timestamp=True)
        ec_latest_reading = retrieve_most_recent_ec(with_timestamp=True)
        mode = retrieve_most_recent_mode(with_timestamp=True)
        pump_activity = retrieve_most_recent_pump_activity()
        pHUpPump_latest_reading = retrieve_most_recent_pHUpPump(with_timestamp=True)
        pHDownPump_latest_reading = retrieve_most_recent_pHDownPump(with_timestamp=True)
        baseA_Pump_latest_reading = retrieve_most_recent_baseA_Pump(with_timestamp=True)
        baseB_Pump_latest_reading = retrieve_most_recent_baseB_Pump(with_timestamp=True)
        return render_template(
            "status.html",
            mode=mode[0],  # Extract mode value
            mode_timestamp=mode[1],  # Extract mode timestamp
            ph_latest_reading=ph_latest_reading[0],  # Extract pH value
            ph_timestamp=ph_latest_reading[1],  # Extract pH timestamp
            ec_latest_reading=ec_latest_reading[0],  # Extract EC value
            ec_timestamp=ec_latest_reading[1],  # Extract EC timestamp
            pump_activity=pump_activity,
            pHUpPump_latest_reading = pHUpPump_latest_reading[0],
            pHUpPump_timestamp = pHUpPump_latest_reading[1],
            pHDownPump_latest_reading = pHDownPump_latest_reading[0],
            pHDownPump_timestamp = pHDownPump_latest_reading[1],
            baseA_Pump_latest_reading = baseA_Pump_latest_reading[0],
            baseA_Pump_timestamp = baseA_Pump_latest_reading[1],
            baseB_Pump_latest_reading = baseB_Pump_latest_reading[0],
            baseB_Pump_timestamp = baseB_Pump_latest_reading[1]
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
    grow_light = request.form.get('grow_light')
    pHUpPump = request.form.get("pHUpPump")
    pHDownPump = request.form.get("pHDownPump")
    baseA_Pump = request.form.get("baseA_Pump")
    baseB_Pump = request.form.get("baseB_Pump")

    try:
        # Handle mode change
        global mode
        if new_mode:
            if new_mode in ["automatic", "manual"]:
                mode = new_mode
        insert_mode(new_mode)
        insert_pump(pump_action)

        # Pump
        if pump_action == 'on':
            insertRequest("[PumpWater]-manual_turn_on_pump", [])
        elif pump_action == 'off':
            insertRequest("[PumpWater]-manual_turn_off_pump", [])
        else:
            print("Invalid Request")

        # Grow Light
        if grow_light == 'on':
            insertRequest("[GrowLight]-turn_on", [])
        elif grow_light == 'off':
            insertRequest("[GrowLight]-turn_off", [])
        else:
            print("Invalid Request")

        #pPump
        if pHUpPump == 'on':
            insertRequest("[pHUpPump]-manual_turn_on_pump", [])
        elif pHUpPump == 'off':
            insertRequest("[pHUpPump]-manual_turn_off_pump", [])
        else:
            print("Invalid Request")

        if pHDownPump == 'on':
            insertRequest("[pHDownPump]-manual_turn_on_pump", [])
        elif pHDownPump == 'off':
            insertRequest("[pHDownPump]-manual_turn_off_pump", [])
        else:
            print("Invalid Request")

        if baseA_Pump == 'on':
            insertRequest("[baseA]-manual_turn_on_pump", [])
        elif baseA_Pump == 'off':
            insertRequest("[baseA]-manual_turn_off_pump", [])
        else:
            print("Invalid Request")

        if baseB_Pump == 'on':
            insertRequest("[baseB]-manual_turn_on_pump", [])
        elif baseB_Pump == 'off':
            insertRequest("[baseB]-manual_turn_off_pump", [])
        else:
            print("Invalid Request")

        return redirect(url_for('get_system_status_html'))
    except Exception as e:
        return f"Error: {str(e)}", 400


@app.route('/generate_ph_plot')
def generate_ph_plot():
    # Simulate adding a new random pH reading to the buffer - REMOVE WHEN TESTING
    #new_ph_value = random.uniform(5.0, 8.0)
    #ph_buffer.add(new_ph_value)

    ph_buffer = 0

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
    #new_ec_value = random.uniform(500, 1500)
    #ec_buffer.add(new_ec_value)

    ec_buffer = 1

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

@app.route('/camera_motion', methods=['GET'])
def camera_motion():
    return render_template('camera_motion.html')

@app.route('/camera_move', methods=['POST'])
def camera_move():
    direction = request.form.get('direction')

    if direction == 'left':
        insertRequest("[CameraMotion]-move_left", [])
    elif direction == 'right':
        insertRequest("[CameraMotion]-move_right", [])
    else:
        return jsonify({"status": "error", "message": "Invalid direction"}), 400

    return redirect(url_for('camera_motion'))

@app.route('/automatic_mode', methods=['GET'])
def set_automatic_mode():
    insertRequest("[Special]-switch_to_automatic", [])
    return '', 204

@app.route('/manual_mode', methods=['GET'])
def set_manual_mode():
    insertRequest("[Special]-switch_to_manual", [])
    return '', 204


# Start the Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)




