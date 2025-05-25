import os
import py7zr
from b2sdk.v1 import B2Api, InMemoryAccountInfo
from config import B2_APP_KEY_ID, B2_APP_KEY, B2_BUCKET_NAME
from typing import List

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
            password=password,
            filters=[{"id": py7zr.FILTER_LZMA2}],
        ) as z:
            for file_path in files:
                if os.path.isdir(file_path):
                    z.writeall(file_path, os.path.basename(file_path))
                else:
                    arcname = os.path.basename(file_path)
                    if encrypt_filenames:
                        arcname = "encrypted_" + arcname  # Personaliza si lo deseas
                    z.write(file_path, arcname)
        # Particionar si part_size está indicado
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
        # Configuración avanzada de inmutabilidad aquí si tu bucket lo permite
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
    encryption_algorithm="AES256"
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
    for part in parts:
        upload_to_backblaze(part, immutable=immutable, immutability_duration=immutability_duration)
        os.remove(part)
    return f"Backup completado exitosamente: {output_name} {'(' + str(len(parts)) + ' partes)' if len(parts)>1 else ''}"
