# Backup7z/scheduler.py
import schedule
import time
import logging
from threading import Thread
from backup import compress_and_upload

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def schedule_backup(frequency: str, files: list, password: str = None, days: list = None, time_of_day: str = "02:00", week_of_month: str = None):
    """Programa backups automáticos."""
    job_map = {
        "Diario": schedule.every().day.at(time_of_day),
        "Semanal": schedule.every().monday.at(time_of_day),  # Default to Monday if no days provided
        "Mensual": schedule.every(30).days.at(time_of_day)  # Default to every 30 days if no specific week provided
        
    }
    
    if frequency == "Diario":
        job_map["Diario"].do(
            lambda: compress_and_upload_with_logging(files, password)
        )
        logging.info(f"Backup diario programado a las {time_of_day}")
    
    elif frequency == "Semanal" and days:
        for day in days:
            getattr(schedule.every(), day.lower()).at(time_of_day).do(
                lambda: compress_and_upload_with_logging(files, password)
            )
        logging.info(f"Backup semanal programado en los días: {', '.join(days)} a las {time_of_day}")
    
    elif frequency == "Mensual" and week_of_month and days:
        for day in days:
            getattr(schedule.every(), week_of_month.lower()).at(time_of_day).do(
                lambda: compress_and_upload_with_logging(files, password)
            )
        logging.info(f"Backup mensual programado en la {week_of_month} semana de {', '.join(days)} a las {time_of_day}")
         
    else:
        logging.error(f"Frecuencia no válida o parámetros faltantes: {frequency}")
    
    # Iniciar hilo del scheduler
    Thread(target=run_scheduler, daemon=True).start()

def compress_and_upload_with_logging(files: list, password: str = None):
    """Wrapper para agregar logging al proceso de compresión y subida."""
    try:
        compress_and_upload(files, password)
        logging.info("Backup completado exitosamente.")
    except Exception as e:
        logging.error(f"Error durante el backup: {e}")

def run_scheduler():
    """Ejecuta el scheduler en segundo plano."""
    while True:
        schedule.run_pending()
        time.sleep(60)

def manual_backup(files, password):
    try:
        # Lógica para realizar la copia de seguridad manual
        logging.info("Iniciando copia de seguridad manual.")
        # ...código para realizar la copia de seguridad...
        logging.info("Copia de seguridad manual completada.")
    except Exception as e:
        logging.error(f"Error en la copia de seguridad manual: {e}")
        raise e