import mysql.connector
import MySQLdb
import sshtunnel

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

MAX_ENTRIES = 50
'''
def insert_data_sensor(mode, pH, EC, pump):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
            ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
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
'''
def insert_pH_data(pH):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "INSERT INTO pH_data (id, timestamp, pH) VALUES (NULL, NOW(), %s)"
            cursor.execute(query, (pH,))
            conn.commit()

            print("Data inserted successfully!")

            cursor.close()
            conn.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

def insert_ec_data(ec):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "INSERT INTO ec_data (id, timestamp, ec) VALUES (NULL, NOW(), %s)"
            cursor.execute(query, (ec,))
            conn.commit()

            print("Data inserted successfully!")

            cursor.close()
            conn.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

def insert_mode(mode):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "INSERT INTO mode (id, timestamp, mode) VALUES (NULL, NOW(), %s)"
            cursor.execute(query, (mode,))
            conn.commit()

            print("Data inserted successfully!")

            cursor.close()
            conn.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

def insert_pump(pump):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "INSERT INTO pump (id, timestamp, pump) VALUES (NULL, NOW(), %s)"
            cursor.execute(query, (pump,))
            conn.commit()

            print("Data inserted successfully!")

            cursor.close()
            conn.close()
    except MySQLdb.Error as err:
        print(f"Error: {err}")

def insert_requests_table(command, arguments):
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
            ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()
            if isinstance(arguments, list):
                arguments_str = ','.join(map(str, arguments))
            else:
                arguments_str = str(arguments)
            # Corrected query to match your table columns
            query = "INSERT INTO requests (command, func, arguments) VALUES (%s, %s, %s)"
            cursor.execute(query, (command, None, arguments_str))
            conn.commit()

            print("Data inserted successfully!")

            cursor.close()
            conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def retrieve_most_recent_pH():
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "SELECT pH FROM pH_data ORDER BY timestamp DESC LIMIT 1;"

            cursor.execute(query)

            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result[0] 
            else:
                return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_EC():
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            # SQL query to get the most recent pH value
            query = "SELECT ec FROM ec_data ORDER BY timestamp DESC LIMIT 1;"

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

def retrieve_most_recent_mode():
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "SELECT mode FROM mode ORDER BY timestamp DESC LIMIT 1;"

            cursor.execute(query)

            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result[0]
            else:
                return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_pump():
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()

            query = "SELECT pump FROM pump ORDER BY timestamp DESC LIMIT 1;"

            cursor.execute(query)

            result = cursor.fetchone()

            cursor.close()
            conn.close()

            if result:
                return result[0]
            else:
                return None

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def retrieve_most_recent_command():
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0

    with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username='superlords1', ssh_password='BinhAn@1962',
        remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
        )
        cursor = conn.cursor()
        query = "SELECT command FROM requests ORDER BY timestamp DESC LIMIT 1;"

        cursor.execute(query)

        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result

def retrieve_most_recent_arguments():
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0
    with sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'),
        ssh_username='superlords1', ssh_password='BinhAn@1962',
        remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
        )
        cursor = conn.cursor()
        
        query = "SELECT arguments FROM requests ORDER BY timestamp DESC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        print(result)
        cursor.close()
        conn.close()
            
        if result and result[0]:
            return result[0].split(',')
        else:
            return []

def delete_most_recent_row(table_name):
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user='superlords1',
                passwd='zotponics123',
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db='superlords1$default',
            )
            cursor = conn.cursor()
            
            query = f"""
            DELETE FROM {table_name} 
            WHERE id = (SELECT id FROM (SELECT id FROM {table_name} ORDER BY id DESC LIMIT 1) AS temp);
            """
            
            cursor.execute(query)
            conn.commit()
            
            print("Most recent row deleted successfully from", table_name)
            
            cursor.close()
            conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

def retrieve_most_recent_request() -> tuple:
    """
    The returned tuple will have 3 items, i.e., (primary key, command, arguments)
    """
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0

    with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
    )
        cursor = conn.cursor()

        query = "SELECT id, command, arguments FROM requests ORDER BY id DESC LIMIT 1"
        cursor.execute(query)

        result = cursor.fetchone()  # Returns (id, command, arguments) or None if no row exists
        cursor.close()
        conn.close()

        return result
    
def pop_most_recent_request() -> tuple:
    """
    This will retrieve the most recent request and pop it from the database
    
    IMPORTANT: The returned tuple will have every element as a string (so would need wrapper methods for the base hardware component class methods)
    
    SIDE NOTE: primary key = id
    """
    
    request_entry = retrieve_most_recent_request()
    
    primary_key = request_entry[0]
    command = request_entry[1]
    args_list = request_entry[2]
    
    delete_request_by_id(primary_key)
        
    return [command, args_list]
    
    
    

def delete_request_by_id(id):
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0
    with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
         )
        cursor = conn.cursor()
        query = "DELETE FROM requests WHERE id = %s"
        cursor.execute(query, (id,))

        conn.commit()
        cursor.close()
        conn.close()
        
def retrieve_current_number_of_requests() -> tuple:
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0

    with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
    )
        cursor = conn.cursor()

        query = "SELECT COUNT(*) AS total_rows FROM requests"
        cursor.execute(query)

        result = cursor.fetchone()  # Returns (id, command, arguments) or None if no row exists
        cursor.close()
        conn.close()

        return result
    
def delete_all_entries() -> None:
    """
    The point of this is to clear the table. Most likely won't use during normal operation but can be used for testing
    """
    
    sshtunnel.SSH_TIMEOUT = 20.0
    sshtunnel.TUNNEL_TIMEOUT = 20.0

    with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
    ) as tunnel:
        conn = MySQLdb.connect(
            user='superlords1',
            passwd='zotponics123',
            host='127.0.0.1',
            port=tunnel.local_bind_port,
            db='superlords1$default',
    )
        cursor = conn.cursor()

        query = "SELECT COUNT(*) AS total_rows FROM requests"
        cursor.execute(query)
        
        cursor.close()
        conn.close()
        
#TESTING
if __name__ == "__main__":
    '''
    import MYSQL_TestCases
    
    MYSQL_TestCases.test_insert_and_delete()
    '''
    insert_pump('on')
