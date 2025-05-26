import os
import py7zr
import sys
from b2sdk.v1 import B2Api, InMemoryAccountInfo
from config import B2_APP_KEY_ID, B2_APP_KEY, B2_BUCKET_NAME
from typing import List

print(">>> Python:", sys.executable)
print(">>> py7zr version:", py7zr.__version__)


def compress_files(
    output_path: str,
    files: List[str],
    password: str = None,
    part_size: int = None,
    encrypt_filenames: bool = False,
    encryption_algorithm: str = "AES256"
) -> list:
    try:
        with py7zr.SevenZipFile(
            output_path,
            'w',
            password=password if password else None,
            filters=[{"id": py7zr.FILTER_LZMA2}],
            encrypt_header=encrypt_filenames  # <-- AÑADE ESTO
        ) as z:
            for file_path in files:
                if os.path.isdir(file_path):
                    z.writeall(file_path, os.path.basename(file_path))
                else:
                    arcname = os.path.basename(file_path)
                    z.write(file_path, arcname)
        parts = [output_path]
        if part_size:
            parts = split_file(output_path, part_size)
        return parts
    except Exception as e:
        raise Exception(f"Error en compresión: {str(e)}")


def split_file(file_path, part_size):
    parts = []
    with open(file_path, "rb") as f:
        idx = 1
        while True:
            chunk = f.read(part_size)
            if not chunk:
                break
            part_file = f"{file_path}.part{idx:03d}"
            with open(part_file, "wb") as pf:
                pf.write(chunk)
            parts.append(part_file)
            idx += 1
    os.remove(file_path)
    return parts

def upload_to_backblaze(file_path: str, immutable=False, immutability_duration=None):
    try:
        info = InMemoryAccountInfo()
        b2_api = B2Api(info)
        b2_api.authorize_account("production", B2_APP_KEY_ID, B2_APP_KEY)
        bucket = b2_api.get_bucket_by_name(B2_BUCKET_NAME)
        extra_args = {}
        bucket.upload_local_file(
            local_file=file_path,
            file_name=os.path.basename(file_path),
            **extra_args
        )
        return True
    except Exception as e:
        raise Exception(f"Error en subida a B2: {str(e)}")

def compress_and_upload(
    files,
    password=None,
    output_name="backup",
    part_size=None,
    encrypt_filenames=False,
    immutable=False,
    immutability_duration=None,
    encryption_algorithm="AES256",
    encrypt_with_aes=False  # <--- NUEVO
):
    if not output_name.endswith(".7z"):
        output_name += ".7z"
    output_path = output_name
    parts = compress_files(
        output_path, files, password,
        part_size=part_size,
        encrypt_filenames=encrypt_filenames,
        encryption_algorithm=encryption_algorithm
    )

    # Nuevo: Cifrar con AES si se pide
    if encrypt_with_aes:
        new_parts = []
        for part in parts:
            encrypted_part = part + '.enc'
            encrypt_file_with_aes(part, encrypted_part)  # Guardará la clave en .enc.key
            os.remove(part)
            new_parts.append(encrypted_part)
        parts = new_parts

    for part in parts:
        upload_to_backblaze(part, immutable=immutable, immutability_duration=immutability_duration)
        os.remove(part)
    return f"Backup completado exitosamente: {output_name} {'(' + str(len(parts)) + ' partes)' if len(parts)>1 else ''}"

def descomprimir_archivo(ruta_7z, carpeta_destino, password):
    with py7zr.SevenZipFile(ruta_7z, 'r', password=password) as z:
        z.extractall(carpeta_destino)