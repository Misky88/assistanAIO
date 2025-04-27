import sqlite3
import json

DB_NAME = "backup_config.db"

def create_database():
    """Crea la base de datos y la tabla de configuraciones si no existe."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS backups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE NOT NULL,
            archivos TEXT NOT NULL,
            encriptado BOOLEAN NOT NULL,
            password TEXT,
            frecuencia TEXT NOT NULL,
            hora TEXT NOT NULL,
            dias TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def save_backup_config(nombre, archivos, encriptado, password, frecuencia, hora, dias=None):
    """Guarda una nueva configuración de backup."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    archivos_json = json.dumps(archivos)
    dias_json = json.dumps(dias) if dias else None

    cursor.execute("""
        INSERT INTO backups (nombre, archivos, encriptado, password, frecuencia, hora, dias)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nombre, archivos_json, encriptado, password, frecuencia, hora, dias_json))

    conn.commit()
    conn.close()

def get_all_backup_configs():
    """Devuelve todas las configuraciones de backup almacenadas."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM backups")
    backups = cursor.fetchall()
    
    conn.close()
    return backups

def delete_backup_config(nombre):
    """Elimina una configuración de backup."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM backups WHERE nombre = ?", (nombre,))
    
    conn.commit()
    conn.close()
