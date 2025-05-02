import sys
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QListWidget, QLineEdit, QPushButton, QLabel,
                             QMessageBox, QInputDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QAction



COMMANDS = {
    "MSINFO32": "Información del sistema",
    "WINVER": "Versión de Windows",
    "PERFMON": "Monitor de rendimiento",
    "CALC": "Calculadora",
    "SNIPPINGTOOL": "Herramienta de recorte",
    "CONTROL": "Panel de control",
    "MSCONFIG": "Configuración del sistema",
    "CMD": "CMD",
    "DISKPART": "Administración de discos",
    "TASKMGR": "Administrador de tareas",
    "REGEDIT": "Editor del registro",
    "CMDKEY": "Credenciales de Windows",
    "EVENTVWR": "Visor de eventos",
    "FIREWALL.CPL": "Configuración del firewall",
    "DEVMGMT.MSC": "Administrador de dispositivos",
    "SERVICES.MSC": "Servicios de Windows",
    "MMC": "Consola de administración",
    "RUNDLL32.EXE": "Ejecutar DLL",
    "APPWIZ.CPL": "Agregar o quitar programas",
    "INETCPL.CPL": "Opciones de Internet",   
    "POWERCFG.CPL": "Opciones de energía",
    "WSCUI.CPL": "Centro de seguridad",
    "PROPERTIES": "Propiedades del sistema",
    "WINSETUP": "Configuración de Windows",
    "WINUP": "Actualización de Windows",
    "WINLOGON": "Inicio de sesión de Windows",
    "WINLOGON.EXE": "Proceso de inicio de sesión",
    "WININIT": "Inicialización de Windows",
    "WININIT.EXE": "Proceso de inicialización",
    }

class ComandaWin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        header = QLabel("🖥️ Ejecutar Comandos de Windows")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")

        layout = QVBoxLayout(self)
        layout.addWidget(header)
        
        # Crear el menú
        self.menu_bar = self.menuBar()
        
        # Menú de Comandos
        self.commands_menu = self.menu_bar.addMenu("Comandos")
        
        # Acción para agregar comando
        self.add_command_action = QAction("Agregar Comando", self)
        self.add_command_action.triggered.connect(self.add_command)
        self.commands_menu.addAction(self.add_command_action)
        
        # Acción para editar comando
        self.edit_command_action = QAction("Editar Comando", self)
        self.edit_command_action.triggered.connect(self.edit_command)
        self.commands_menu.addAction(self.edit_command_action)
        
        # Acción para borrar comando
        self.delete_command_action = QAction("Borrar Comando", self)
        self.delete_command_action.triggered.connect(self.delete_command)
        self.commands_menu.addAction(self.delete_command_action)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Cabecera
        header = QLabel("Ejecutor de Comandos de Windows")
        header.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #2c3e50; padding: 15px;")
        
        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar comandos...")
        self.search_bar.textChanged.connect(self.filter_commands)
        self.search_bar.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 5px;
                font-size: 14px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        
        # Lista de comandos
        self.command_list = QListWidget()
        self.command_list.itemDoubleClicked.connect(self.execute_command)
        self.command_list.setStyleSheet("""
            QListWidget {
                background-color: #ffffff;
                border-radius: 5px;
                padding: 5px;
                color: #000000;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #dcdde1;
            }
            QListWidget::item:hover {
                background-color: #3498db; 
                color: #ffffff;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: #ffffff;
            }
        """)
        
        # Botones
        btn_execute = QPushButton("Ejecutar Comando")
        btn_execute.clicked.connect(self.execute_command)
        btn_execute.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Diseño
        layout.addWidget(header)
        layout.addWidget(self.search_bar)
        layout.addWidget(self.command_list)
        layout.addWidget(btn_execute)
        
        self.load_commands()
        
    def load_commands(self):
        self.command_list.clear()
        for cmd, desc in COMMANDS.items():
            self.command_list.addItem(f"{cmd} - {desc}")
            
    def filter_commands(self):
        search_text = self.search_bar.text().upper()
        for i in range(self.command_list.count()):
            item = self.command_list.item(i)
            item.setHidden(search_text not in item.text())
            
    def execute_command(self):
        selected = self.command_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Selecciona un comando primero")
            return
            
        cmd = selected.text().split(" - ")[0]
        try:
            subprocess.Popen(f"start {cmd}", shell=True)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo ejecutar el comando:\n{str(e)}")
    
    def add_command(self):
        cmd, ok = QInputDialog.getText(self, "Agregar Comando", "Introduce el comando:")
        if ok and cmd:
            desc, ok = QInputDialog.getText(self, "Agregar Descripción", "Introduce la descripción del comando:")
            if ok and desc:
                COMMANDS[cmd] = desc
                self.load_commands()
    
    def edit_command(self):
        selected = self.command_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Selecciona un comando primero")
            return
        
        cmd = selected.text().split(" - ")[0]
        desc, ok = QInputDialog.getText(self, "Editar Descripción", "Edita la descripción del comando:", text=COMMANDS[cmd])
        if ok and desc:
            COMMANDS[cmd] = desc
            self.load_commands()
    
    def delete_command(self):
        selected = self.command_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Error", "Selecciona un comando primero")
            return
        
        cmd = selected.text().split(" - ")[0]
        del COMMANDS[cmd]
        self.load_commands()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ComandaWin()
    window.show()
    sys.exit(app.exec())