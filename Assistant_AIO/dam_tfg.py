import sys
import platform
import psutil
import os
# Añadir la ruta al módulo chocolatey.py
sys.path.append(os.path.join(os.path.dirname(__file__), 'Backup7z'))
from assistant_aio.chocolatey import ChocolateyUI
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget, QTabWidget, QLineEdit, QListWidget)
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import QSize, Qt, QTimer
import subprocess


class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistan AIO")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(800, 600)

        # Aplicar estilos
        self.setStyleSheet(self.get_styles())
        
        # Configuración principal de la UI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.setup_sidebar()
        self.setup_main_content()
        
        # Cargar datos iniciales
        self.load_system_info()
        self.show_system_info()

        # Configurar temporizador para actualizar estadísticas en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_realtime_stats)
        self.timer.start(400)  # Actualizar cada segundo
    
    def get_styles(self):
        return """
        QWidget {
            background-color: #f0f3f5;
            font-family: 'Segoe UI';
        }
        QLabel {
            font-size: 16px;
            color: #34495e;
        }
        QPushButton {
            background-color: #2980b9;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 5px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QPushButton:pressed {
            background-color: #1d6fa5;
        }
        QLineEdit {
            padding: 6px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 4px;
            background-color: white;
            color: #34495e;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #dcdcdc;
            font-size: 14px;
            color: #34495e;
        }
        QTabWidget::pane {
            border: 0px solid #ccc;
            top: -1px;
        }
        QTabBar::tab {
            background: #ecf0f1;
            color: #34495e;
            padding: 10px 20px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            font-weight: 500;
        }
        QTabBar::tab:selected {
            background: #f0f3f5;
            color: #2980b9;
            font-weight: bold;
            border: 2px solid #2980b9;
            border-bottom: none;
        }
        QTabBar::tab:hover {
            background: #d0e7f9;
        }
        QProgressBar {
            border: 1px solid #ccc;
            border-radius: 5px;
            text-align: center;
            color: #34495e;
            background-color: #ecf0f1;
        }
        QProgressBar::chunk {
            background-color: #2980b9;
            width: 10px;
            border-radius: 5px;
        }
        QComboBox {
            background-color: white;
            border: 1px solid #ccc;
            border-radius: 4px;
            padding: 5px;
            font-size: 14px;
            color: #34495e;
        }
        QComboBox QAbstractItemView {
            background-color: white;
            selection-background-color: #d0e7f9;
            selection-color: #000000;
            border: 0;
        }
        QCheckBox {
            spacing: 8px;
            font-size: 14px;
            color: #34495e;
        }
        """

    def setup_sidebar(self):
        """Configura la barra lateral con estilos y botones"""
        sidebar = QWidget()
        sidebar.setFixedWidth(190)
        sidebar.setStyleSheet("""
            background-color: #2c3e50;
            padding: 20px 0;
        """)
        
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Botón de Inicio
        self.btn_home = QPushButton("Inicio")
        self.btn_home.setIcon(QIcon.fromTheme("go-home"))
        self.btn_home.setIconSize(QSize(24, 24))
        self.btn_home.setStyleSheet("""
            QPushButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.btn_home.clicked.connect(self.show_system_info)
        sidebar_layout.addWidget(self.btn_home)

        # Botón de Aplicaciones
        self.btn_apps = QPushButton("Aplicaciones")
        self.btn_apps.setIcon(QIcon.fromTheme("applications-system"))
        self.btn_apps.setIconSize(QSize(24, 24))
        self.btn_apps.setStyleSheet("""
            QPushButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.btn_apps.clicked.connect(self.show_applications_ui)
        sidebar_layout.addWidget(self.btn_apps)

        # Botón de Drivers
        self.btn_drivers = QPushButton("Drivers")
        self.btn_drivers.setIcon(QIcon.fromTheme("drive-harddisk"))
        self.btn_drivers.setIconSize(QSize(24, 24))
        self.btn_drivers.setStyleSheet("""
            QPushButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        sidebar_layout.addWidget(self.btn_drivers)

        # Botón de Comandos Windows
        self.btn_commands = QPushButton("Comandos Windows")
        self.btn_commands.setIcon(QIcon.fromTheme("utilities-terminal"))
        self.btn_commands.setIconSize(QSize(24, 24))
        self.btn_commands.setStyleSheet("""
            QPushButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        self.btn_commands.clicked.connect(self.show_comanda_win)
        sidebar_layout.addWidget(self.btn_commands)

        # Botón de Backups
        self.btn_backups = QPushButton("Backups")
        self.btn_backups.setIcon(QIcon.fromTheme("document-save"))
        self.btn_backups.setIconSize(QSize(24, 24))
        self.btn_backups.setStyleSheet("""
            QPushButton {
                color: white;
                text-align: left;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #34495e;
            }
        """)
        sidebar_layout.addWidget(self.btn_backups)

        sidebar_layout.addStretch()
        self.main_layout.addWidget(sidebar)

    def setup_main_content(self):
        """Configura el área de contenido principal"""
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)

    # Página de información del sistema
        self.system_info_page = QWidget()
        self.stacked_widget.addWidget(self.system_info_page)

    # Página de Comandos Windows
        self.comanda_win_page = QWidget()  # Placeholder for Comandowin
        # Replace QWidget with Comandowin() once the class is defined or imported
        self.stacked_widget.addWidget(self.comanda_win_page)

    # Página de Chocolatey (Nueva gestión de aplicaciones)
        self.chocolatey_page = ChocolateyUI()
        self.stacked_widget.addWidget(self.chocolatey_page)

    # Página de Backups (opcional, si quieres integrarlo más adelante)
    # self.backup_page = BackupUI() 
    # self.stacked_widget.addWidget(self.backup_page)


    def load_system_info(self):
        """Carga y procesa la información del sistema"""
        try:
            self.system_data = {
                'os': f"{platform.system()} {platform.release()}",
                'hostname': platform.node(),
                'processor': platform.processor() or "Desconocido",
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'ram': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
                'cpu_freq': f"{(psutil.cpu_freq().current or 0) / 1000:.2f} GHz",
                'architecture': platform.machine()
            }
        except Exception as e:
            print(f"Error obteniendo información del sistema: {e}")
            self.system_data = {
                'os': "No disponible",
                'hostname': "No disponible",
                'processor': "No disponible",
                'cores': 0,
                'threads': 0,
                'ram': "0 GB",
                'cpu_freq': "0 GHz",
                'architecture': "No disponible"
            }

    def create_info_row(self, title, value):
        """Crea una fila de información con estilos"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #34495e;")
        title_label.setFixedWidth(200)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet("color: #7f8c8d;")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        return widget

    def show_system_info(self):
        """Muestra la información del sistema en el área principal"""
        # Limpiar contenido anterior
        if self.system_info_page.layout():
            QWidget().setLayout(self.system_info_page.layout())
        
        layout = QVBoxLayout(self.system_info_page)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Encabezado
        header = QLabel("Información del Sistema")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        layout.addWidget(header)
        
        # Sección principal
        main_content = QWidget()
        main_layout = QVBoxLayout(main_content)
        
        # Agregar filas de información
        main_layout.addWidget(self.create_info_row("Sistema Operativo:", self.system_data['os']))
        main_layout.addWidget(self.create_info_row("Nombre del Equipo:", self.system_data['hostname']))
        main_layout.addWidget(self.create_info_row("Procesador:", self.system_data['processor']))
        main_layout.addWidget(self.create_info_row("Arquitectura:", self.system_data['architecture']))
        main_layout.addWidget(self.create_info_row("Núcleos Físicos:", self.system_data['cores']))
        main_layout.addWidget(self.create_info_row("Núcleos Lógicos:", self.system_data['threads']))
        main_layout.addWidget(self.create_info_row("Frecuencia CPU:", self.system_data['cpu_freq']))
        main_layout.addWidget(self.create_info_row("Memoria RAM:", self.system_data['ram']))
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #bdc3c7;")
        main_layout.addWidget(separator)
        
        # Estadísticas en tiempo real
        realtime_stats = QLabel("Estadísticas en Tiempo Real")
        realtime_stats.setStyleSheet("""
            font-size: 16px;
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(realtime_stats)
        
        # Widgets de estadísticas
        self.stats_widget = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_widget)
        
        # Uso de CPU
        self.cpu_usage = QLabel()
        self.cpu_usage.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        """)
        
        # Uso de Memoria
        self.mem_usage = QLabel()
        self.mem_usage.setStyleSheet("""
            background-color: #e67e22;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        """)
        
        self.stats_layout.addWidget(self.cpu_usage)
        self.stats_layout.addWidget(self.mem_usage)
        main_layout.addWidget(self.stats_widget)
        
        layout.addWidget(main_content)
        self.stacked_widget.setCurrentWidget(self.system_info_page)

        # Actualizar estadísticas en tiempo real inmediatamente
        self.update_realtime_stats()

    def show_comanda_win(self):
        """Muestra la vista de Comandos Windows"""
        self.stacked_widget.setCurrentWidget(self.comanda_win_page)

    def show_chocolatey_ui(self):
        """Muestra la vista de Chocolatey"""
        self.stacked_widget.setCurrentWidget(self.chocolatey_page)

    def show_applications_ui(self):
        """Muestra la vista de Aplicaciones"""
        self.stacked_widget.setCurrentWidget(self.applications_page)

    def update_realtime_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        self.cpu_usage.setText(f"CPU: {psutil.cpu_percent()}%")
        mem = psutil.virtual_memory()
        self.mem_usage.setText(f"RAM: {mem.percent}%")

class ApplicationsUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

     
    def setup_ui(self):
        layout = QVBoxLayout()

        # Encabezado
        header = QLabel("Gestor de Aplicaciones - WinGet y Chocolatey")
        header.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        layout.addWidget(header)

        # Pestañas para WinGet y Chocolatey
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_winget_tab(), "WinGet")
        self.tabs.addTab(self.create_chocolatey_tab(), "Chocolatey")
        layout.addWidget(self.tabs)

        self.setLayout(layout)

    def create_winget_tab(self):
        """Crea la pestaña para gestionar aplicaciones con WinGet"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Barra de búsqueda
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar aplicaciones con WinGet...")
        self.search_bar.returnPressed.connect(self.search_apps)  # Conectar búsqueda
        layout.addWidget(self.search_bar)

        # Resultados de búsqueda
        self.search_results = QListWidget()
        layout.addWidget(self.search_results)

        # Botón para instalar la aplicación seleccionada
        install_button = QPushButton("Instalar Aplicación Seleccionada")
        install_button.clicked.connect(self.install_selected_app)
        layout.addWidget(install_button)

        tab.setLayout(layout)
        return tab

    def create_chocolatey_tab(self):
        """Crea la pestaña para gestionar aplicaciones con Chocolatey"""
        tab = QWidget()
        layout = QVBoxLayout()

        # Barra de búsqueda
        self.choco_search_bar = QLineEdit()
        self.choco_search_bar.setPlaceholderText("Buscar aplicaciones con Chocolatey...")
        self.choco_search_bar.returnPressed.connect(self.search_choco_apps)  # Conectar búsqueda
        layout.addWidget(self.choco_search_bar)

        # Resultados de búsqueda
        self.choco_results = QListWidget()
        layout.addWidget(self.choco_results)

        # Botón para instalar la aplicación seleccionada
        choco_install_button = QPushButton("Instalar Aplicación Seleccionada")
        choco_install_button.clicked.connect(self.install_selected_choco_app)
        layout.addWidget(choco_install_button)

        tab.setLayout(layout)
        return tab

    def search_apps(self):
        """Busca aplicaciones con WinGet y muestra más información"""
        query = self.search_bar.text()
        if not query:
            return

        self.search_results.clear()
        try:
            # Ejecuta el comando `winget search` con el término ingresado
            result = subprocess.run(["winget", "search", query], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines()[2:]:
                if line.strip():
                    # Procesar cada línea para extraer información
                    parts = line.split()
                    app_id = parts[0]  # ID de la aplicación
                    name = " ".join(parts[1:-2])  # Nombre de la aplicación
                    version = parts[-2]  # Versión
                    source = parts[-1]  # Fuente
                    # Mostrar información en la lista
                    self.search_results.addItem(f"{name} ({app_id}) - Versión: {version} - Fuente: {source}")
        except subprocess.CalledProcessError as e:
            print(f"Error al buscar aplicaciones: {e}")

    def search_choco_apps(self):
        """Busca aplicaciones con Chocolatey y muestra más información"""
        query = self.choco_search_bar.text()
        if not query:
            return

        self.choco_results.clear()
        try:
            # Ejecuta el comando `choco search` con el término ingresado
            result = subprocess.run(["choco", "search", query], capture_output=True, text=True, check=True)
            if result.returncode != 0 or not result.stdout.strip():
                self.choco_results.addItem("No se encontraron resultados.")
                return

            for line in result.stdout.splitlines()[1:]:
                if line.strip():
                    # Procesar cada línea para extraer información
                    parts = line.split("|")
                    name = parts[0].strip()  # Nombre de la aplicación
                    version = parts[1].strip() if len(parts) > 1 else "Desconocida"  # Versión
                    description = parts[2].strip() if len(parts) > 2 else "Sin descripción"  # Descripción
                    # Mostrar información en la lista
                    self.choco_results.addItem(f"{name} - Versión: {version} - {description}")
        except subprocess.CalledProcessError as e:
            self.choco_results.addItem(f"Error al buscar aplicaciones: {e}")
        except Exception as e:
            self.choco_results.addItem(f"Error inesperado: {e}")

    def install_selected_app(self):
        """Instala la aplicación seleccionada de los resultados de búsqueda de WinGet"""
        selected_item = self.search_results.currentItem()
        if not selected_item:
            return

        app_id = selected_item.text().split("(")[-1].split(")")[0]  # Extraer el ID de la aplicación
        try:
            subprocess.run(["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
            print(f"{app_id} instalado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar {app_id}: {e}")

    def install_selected_choco_app(self):
        """Instala la aplicación seleccionada de los resultados de búsqueda de Chocolatey"""
        selected_item = self.choco_results.currentItem()
        if not selected_item:
            return

        app_id = selected_item.text().split(" - ")[0]  # Extraer el nombre de la aplicación
        try:
            subprocess.run(["choco", "install", app_id, "-y"], check=True)
            print(f"{app_id} instalado correctamente.")
        except subprocess.CalledProcessError as e:
            print(f"Error al instalar {app_id}: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configurar fuente global
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = SystemInfoApp()
    window.show()
    sys.exit(app.exec())