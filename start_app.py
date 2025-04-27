import os
import sys
import subprocess

def start_application():
    # Ruta donde está realmente tu archivo principal dam_tfg.py
    project_dir = os.path.join(os.path.dirname(__file__), "assistant_AIO")
    
    if not os.path.exists(project_dir):
        print("Error: No se encontró la carpeta 'assistant_AIO'. ¿Seguro que la carpeta está bien nombrada?")
        sys.exit(1)

    dam_tfg_path = os.path.join(project_dir, "dam_tfg.py")

    if not os.path.isfile(dam_tfg_path):
        print("Error: No se encontró 'dam_tfg.py' dentro de 'assistant_AIO.")
        sys.exit(1)

    # Ejecutar el dam_tfg.py
    subprocess.run([sys.executable, dam_tfg_path])

if __name__ == "__main__":
    start_application()
