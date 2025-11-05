import mysql.connector

def conectar():
    conexion = mysql.connector.connect(
        host="b9zwqn3idkqwnk359njt-mysql.services.clever-cloud.com",
        user="u99hgdmzhdyeexrb",
        password="BWDGJRckc3HMdCjhWS2i",
        database="b9zwqn3idkqwnk359njt"
    )
    cursor = conexion.cursor(dictionary=True)
    print("Conexión exitosa:", conexion.is_connected())
    return conexion, cursor
