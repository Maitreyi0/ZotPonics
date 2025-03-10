import mysql.connector
import random
import json

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

def insert_pH_data(pH):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected SQL query
        query = "INSERT INTO pH_data (id, timestamp, pH) VALUES (NULL, NOW(), %s)"
        cursor.execute(query, (pH,))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insert_ec_data(ec):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected SQL query
        query = "INSERT INTO ec_data (id, timestamp, ec) VALUES (NULL, NOW(), %s)"
        cursor.execute(query, (ec,))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insert_mode(mode):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected SQL query
        query = "INSERT INTO mode (id, timestamp, mode) VALUES (NULL, NOW(), %s)"
        cursor.execute(query, (mode,))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insert_pump(pump):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected SQL query
        query = "INSERT INTO pump (id, timestamp, pump) VALUES (NULL, NOW(), %s)"
        cursor.execute(query, (pump,))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insert_data_sensor(mode, pH, EC, pump):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected query to match your table columns
        query = "INSERT INTO sensor_data (mode, pH, EC, pump) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (mode, pH, EC, pump))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def insertRequest(command, arguments: list):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # Corrected query to match your table columns
        query = "INSERT INTO requests (command, arguments) VALUES (%s, %s)"
        json_encoded_string = json.dumps(arguments)
        cursor.execute(query, (command, json_encoded_string))
        conn.commit()

        print("Data inserted successfully!")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def retrieve_most_recent_pH(with_timestamp=False):
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get the most recent pH value
        query = "SELECT pH, timestamp FROM pH_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]  # (pH, timestamp) or just pH value
        else:
            return (None, None) if with_timestamp else None  # Ensuring it never returns just None

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return (None, None) if with_timestamp else None

def retrieve_most_recent_ec(with_timestamp=False):
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get the most recent EC value
        query = "SELECT ec, timestamp FROM ec_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]  # (pH, timestamp) or just pH value
        else:
            return (None, None) if with_timestamp else None  # Ensuring it never returns just None

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_all_pH_values():
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get all the pH values
        query = "SELECT pH FROM pH_data"

        # Execute the query
        cursor.execute(query)

        # Fetch the results
        data = cursor.fetchall()

        # Store results in array
        result = []

        for row in data:
            result.append((row[0]))

        cursor.close()
        conn.close()

        return result[-25:]

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return None

def retrieve_all_ec_values():
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get the all the ec data
        query = "SELECT ec FROM ec_data"

        # Execute the query
        cursor.execute(query)

        # Fetch the results
        data = cursor.fetchall()

        #Store results in array
        result = []

        for row in data:
            result.append((row[0]))

        cursor.close()
        conn.close()

        return result[-25:]

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return None

def retrieve_most_recent_mode(with_timestamp=False):
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get the most recent mode value
        query = "SELECT mode, timestamp FROM mode ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]  # (pH, timestamp) or just pH value
        else:
            return (None, None) if with_timestamp else None  # Ensuring it never returns just None

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pump(with_timestamp=False):
    try:
        # Establish connection to the database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        # SQL query to get the most recent pump value
        query = "SELECT pump, timestamp FROM pump ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]  # (pH, timestamp) or just pH value
        else:
            return (None, None) if with_timestamp else None  # Ensuring it never returns just None

    except mysql.connector.Error as err:
        print(f"Error retrieving pH: {err}")
        return (None, None) if with_timestamp else None

def retrieve_most_recent_command():
    """Fetches the most recent command from the requests table."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = "SELECT command FROM requests ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result[0] if result else None  # Return command or None if table is empty

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_arguments():
    """Fetches the most recent arguments from the requests table."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = "SELECT arguments FROM requests ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result and result[0]:  # Ensure result is not None or empty
            return result[0].split(',')  # Split arguments by comma and return as a list
        else:
            return []  # Return empty list if no arguments are found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pHUpPump(with_timestamp=False):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        query = "SELECT pumpActive, timestamp FROM pPumpActivity WHERE alias = 'pHUpPump' ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]
        else:
            return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pHDownPump(with_timestamp=False):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        query = "SELECT pumpActive, timestamp FROM pPumpActivity WHERE alias = 'pHDownPump' ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]
        else:
            return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_baseA_Pump(with_timestamp=False):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        query = "SELECT pumpActive, timestamp FROM pPumpActivity WHERE alias = 'baseA_Pump' ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]
        else:
            return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_baseB_Pump(with_timestamp=False):
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        query = "SELECT pumpActive, timestamp FROM pPumpActivity WHERE alias = 'baseB_Pump' ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result if with_timestamp else result[0]
        else:
            return (None, None) if with_timestamp else None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_func():
    """Fetches the most recent command from the requests table."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = "SELECT func FROM requests ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        return result[0] if result else None  # Return func or None if table is empty

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pump_activity():
    """Fetches the most recent pump activity from the waterPumpActivity table."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = """
            SELECT timestamp, alias, pwm_freq, on_off_state, mode, auto_cycle_thread_active
            FROM waterPumpActivity
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return {
                "Pump Timestamp": result[0],
                "Pump Alias": result[1],
                "PWM Frequency": result[2],
                "On/Off State": result[3],
                "Mode": result[4],
                "Auto Cycle Thread Active": result[5],
            }
        else:
            return (None, None, None, None, None, None)

    except mysql.connector.Error as err:
        print(f"Error retrieving pump activity: {err}")
        return None

def retrieve_most_recent_pPump_activity():
    """Fetches the most recent pPump activity from the pPumpActivity table (excluding pin)."""
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = """
            SELECT timestamp, alias, pumpActive
            FROM pPumpActivity
            ORDER BY timestamp DESC
            LIMIT 1;
        """
        cursor.execute(query)
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return {
                "pPump Timestamp": result[0],
                "pPump Alias": result[1],
                "pPump Active": result[2]
            }
        else:
            return None

    except mysql.connector.Error as err:
        print(f"Error retrieving pPump activity: {err}")
        return None


'''
test = retrieve_most_recent_pump_activity()
print(test)
'''
