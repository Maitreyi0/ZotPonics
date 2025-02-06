import mysql.connector
import random

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

def insert_data(mode, pH, EC, pump):
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

def retrieve_most_recent_pH():
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
        query = "SELECT pH FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return the pH value (first column)
        else:
            return None  # Return None if no data is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_ec():
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
        query = "SELECT EC FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return the EC value (first column)
        else:
            return None  # Return None if no data is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_mode():
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
        query = "SELECT mode FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return the mode value (first column)
        else:
            return None  # Return None if no data is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pump():
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
        query = "SELECT pump FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

        # Execute the query
        cursor.execute(query)

        # Fetch the result
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            return result[0]  # Return the pump value (first column)
        else:
            return None  # Return None if no data is found

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


''' TESTING
insert_data('MANUAL', 5.0, 2.0, 'OFF')
pump = retrieve_most_recent_pH()
print(pump)
'''
