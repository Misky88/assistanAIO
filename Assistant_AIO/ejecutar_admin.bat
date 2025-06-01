@echo off
:: Script para ejecutar como administrador
:: Cambia python si usas py o ruta absoluta
powershell -Command "Start-Process python -ArgumentList 'chocolatey.py' -Verb runAs"