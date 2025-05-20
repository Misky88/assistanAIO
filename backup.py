# Backup7z/backup.py
import os
import py7zr
from b2sdk.v1 import B2Api, InMemoryAccountInfo
from config import B2_APP_KEY_ID, B2_APP_KEY, B2_BUCKET_NAME
from typing import List

def compress_files(output_path: str, files: List[str], password: str = None) -> str:
    """Comprime archivos usando py7zr con encriptación opcional."""
    try:
        with py7zr.SevenZipFile(output_path, 'w', password=password) as z:
            for file_path in files:
                if os.path.isdir(file_path):
                    z.writeall(file_path, os.path.basename(file_path))
                else:
                    z.write(file_path, os.path.basename(file_path))
        return output_path
    except Exception as e:
        raise Exception(f"Error en compresión: {str(e)}")

def upload_to_backblaze(file_path: str):
    """Sube el archivo a Backblaze B2."""
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", B2_APP_KEY_ID, B2_APP_KEY)
        
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        bucket.upload_local_file(
            local_file=file_path,
            file_name=os.path.basename(file_path)
        )
        return True
    except Exception as e:
        raise Exception(f"Error en subida a B2: {str(e)}")

def compress_and_upload(files: List[str], password: str = None, output_name: str = "backup", part_size: int = None) -> str:
    """Ejecuta todo el proceso de backup con compresión opcionalmente dividida."""
    if not output_name.endswith(".7z"):
        output_name += ".7z"

    output_path = output_name
    compress_files(output_path, files, password)

    # Si part_size está definido, aquí podrías implementar la división (no está implementada aún)
    # por ejemplo, usando una librería externa o dividiendo el archivo manualmente.

    upload_to_backblaze(output_path)
    os.remove(output_path)
    return f"Backup completado exitosamente: {output_name}"

