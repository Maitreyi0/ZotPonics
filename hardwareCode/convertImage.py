import mysql.connector
import MySQLdb
import sshtunnel
import io
from PIL import Image

DB_HOST = "superlords1.mysql.pythonanywhere-services.com"
DB_USER = "superlords1"
DB_PASSWORD = "zotponics123"
DB_NAME = "superlords1$default"

def store_image(image_path):
    """ Converts an image to JPEG and stores it in the database. """
    try:
        with open(image_path, "rb") as img_file:
            img_data = img_file.read()  # Read image as binary

        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user=DB_USER,
                passwd=DB_PASSWORD,
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db=DB_NAME,
            )
            cursor = conn.cursor()

            query = "INSERT INTO images (jpeg_bits) VALUES (%s)"
            cursor.execute(query, (img_data,))
            conn.commit()
            print("Image stored successfully!")

            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error storing image: {e}")

def retrieve_image(image_id, output_path):
    """ Retrieves an image from the database and saves it as a JPEG file. """
    try:
        with sshtunnel.SSHTunnelForwarder(
            ('ssh.pythonanywhere.com'),
            ssh_username='superlords1', ssh_password='BinhAn@1962',
            remote_bind_address=('superlords1.mysql.pythonanywhere-services.com', 3306)
        ) as tunnel:
            conn = MySQLdb.connect(
                user=DB_USER,
                passwd=DB_PASSWORD,
                host='127.0.0.1',
                port=tunnel.local_bind_port,
                db=DB_NAME,
            )
            cursor = conn.cursor()

            query = "SELECT jpeg_bits FROM images WHERE id = %s"
            cursor.execute(query, (image_id,))
            result = cursor.fetchone()

            if result and result[0]:
                with open(output_path, "wb") as img_file:
                    img_file.write(result[0])
                print(f"Image retrieved and saved to {output_path}")
            else:
                print("No image found with the given ID.")

            cursor.close()
            conn.close()
    except Exception as e:
        print(f"Error retrieving image: {e}")

if __name__ == "__main__":
    import convertImageTestCases
    
    convertImageTestCases.test_insert_one_and_retrieve()