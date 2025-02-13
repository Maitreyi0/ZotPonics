import mysql.connector
import MySQLdb
import sshtunnel

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

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

def insert_data_requests(command, func, arguments):
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
            cursor.execute(query, (command, func, arguments_str))
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

            query = "SELECT pH FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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
            query = "SELECT EC FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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

            query = "SELECT mode FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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

            query = "SELECT pump FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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
        
#TESTING
if __name__ == "__main__":
    insert_data_requests('test', 'test', [1, 2, 3])
    delete_most_recent_row('sensor_data')
    import mysql.connector
import MySQLdb
import sshtunnel

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

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

def insert_data_requests(command, func, arguments):
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
            cursor.execute(query, (command, func, arguments_str))
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

            query = "SELECT pH FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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
            query = "SELECT EC FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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

            query = "SELECT mode FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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

            query = "SELECT pump FROM sensor_data ORDER BY timestamp DESC LIMIT 1;"

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
        
#TESTING
if __name__ == "__main__":
    insert_data_requests('test', 'test', [1, 2, 3])
    delete_most_recent_row('sensor_data')
    
