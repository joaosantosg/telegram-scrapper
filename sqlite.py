import sqlite3

def get_db():
    try:
        print("Conectando ao banco de dados")
        conn = sqlite3.connect('database.db')
        print("Conexão estabelecida")
        return conn
    except Exception as e:
        conn.close()
        print(e)
