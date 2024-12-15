import mysql.connector

def db_connector():
    try:
        db = mysql.connector.connect(
            database = 'e_commerce',
            user = 'root',
            password = 'Luna2794',
            host = '127.0.0.1'
        )

        if db.is_connected():
            print('connected')
        
    except:
        print('connection failed')

db_connector()