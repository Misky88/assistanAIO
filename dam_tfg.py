import ctypes
import os
import platform
import sys
import psutil
import random
import string
import smtplib
import requests
from requests.auth import HTTPBasicAuth
from PyQt6.QtCore import QSize, Qt, QTimer
from datetime import datetime
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtGui import QIcon, QFont, QPixmap
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget,
                             QLineEdit, QSpacerItem, QSizePolicy, QMessageBox,
                             QTableWidget, QTableWidgetItem, QAbstractItemView)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from app_backup import BackupApp
from chocolatey import PackageApp
from comandowin import ComandaWin

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_pc_brand():
    try:
        import wmi
        c = wmi.WMI()
        for system in c.Win32_ComputerSystem():
            manufacturer = system.Manufacturer.strip().lower()
            model = system.Model.strip().lower()
            print(f"[WMI] Manufacturer: {manufacturer}, Model: {model}")
            return manufacturer, model
    except Exception as e:
        print(f"[WMI ERROR] {e}")
        uname = platform.uname()
        print(f"[PLATFORM] system: {uname.system}, node: {uname.node}")
        return uname.system.lower(), uname.node.lower()

class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant AIO")
        self.setGeometry(100, 100, 1400, 800)          
        self.setMinimumSize(1200, 700) 
        # self.setMaximumSize(1000,800)
        
        # Configuración principal de la UI
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)  
        self.setup_sidebar()
        self.setup_main_content()
        self.datetime_label = QLabel(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.datetime_label.setStyleSheet("color: #7f8c8d;")
        
        # Cargar datos iniciales
        self.load_system_info()
        self.show_system_info()

        # Configurar temporizador para actualizar estadísticas en tiempo real
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_realtime_stats)
        self.timer.start(400)  # Actualizar cada 0.4 segundos

        self.register_click_count = 0  # Contador de clics para la página de registro

    def update_realtime_stats(self):
        self.cpu_usage.setText(f"CPU: {psutil.cpu_percent()}%")
        mem = psutil.virtual_memory()
        self.mem_usage.setText(f"RAM: {mem.percent}%")
        from datetime import datetime
        if hasattr(self, "datetime_label"):
            self.datetime_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))


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
        self.btn_drivers.clicked.connect(self.show_drivers_ui)
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
        self.btn_backups.clicked.connect(self.show_backups_ui)
        sidebar_layout.addWidget(self.btn_backups)

        # Botón de Registro
        self.btn_register = QPushButton("Registro")
        self.btn_register.setIcon(QIcon.fromTheme("contact-new"))# Usa aquí el nombre de tu imagen
        self.btn_register.setIconSize(QSize(24, 24))
        self.btn_register.setStyleSheet("""
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
        self.btn_register.clicked.connect(self.show_register_ui)
        sidebar_layout.addWidget(self.btn_register)

        sidebar_layout.addStretch()
        self.main_layout.addWidget(sidebar)

    def set_sidebar_button_states(self, active_button):
    # Lista con todos los botones del sidebar
        for btn in [
            self.btn_home, self.btn_apps, self.btn_drivers,
            self.btn_commands, self.btn_backups, self.btn_register
        ]:
            btn.setEnabled(btn != active_button)


    def setup_main_content(self):
        """Configura el área de contenido principal"""
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Página de información del sistema (INICIO)
        self.system_info_page = QWidget()
        self.stacked_widget.addWidget(self.system_info_page)
        
        # Página de Aplicaciones (Aplicaciones)
        self.applications_page = PackageApp()
        self.stacked_widget.addWidget(self.applications_page)
        
        # Página de Comandos Windows
        self.comanda_win_page = ComandaWin()
        self.stacked_widget.addWidget(self.comanda_win_page)
        
        # # Página de Backups
        self.backups_page = BackupApp()
        self.stacked_widget.addWidget(self.backups_page)
        
        # Página de Registro
        self.register_page = QWidget()
        self.setup_register_page()
        self.stacked_widget.addWidget(self.register_page)
        
        # Página de Drivers
        self.drivers_page = QWidget()
        self.setup_drivers_page()
        self.stacked_widget.addWidget(self.drivers_page)
        
    def setup_register_page(self):
        layout = QVBoxLayout(self.register_page)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Título centrado
        title = QLabel("Registro Assistant AIO")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 30px;")
        layout.addWidget(title)

        # Email
        self.email_label = QLabel("Email:")
        self.email_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.email_input = QLineEdit()
        self.email_input.setMinimumHeight(32)
        layout.addWidget(self.email_label)
        layout.addWidget(self.email_input)

        # Contraseña
        self.password_label = QLabel("Contraseña:")
        self.password_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.password_input = QLineEdit()
        self.password_input.setMinimumHeight(32)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        # Nombre del equipo
        self.hostname_label = QLabel("Nombre del equipo:")
        self.hostname_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.hostname_input = QLineEdit()
        self.hostname_input.setText(platform.node())
        self.hostname_input.setReadOnly(True)
        self.hostname_input.setMinimumHeight(32)
        layout.addWidget(self.hostname_label)
        layout.addWidget(self.hostname_input)

        # IP local
        self.ip_label = QLabel("IP Local:")
        self.ip_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        try:
            addrs = psutil.net_if_addrs()
            ip = None
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == 2 and not addr.address.startswith("169.254"):
                        ip = addr.address
                        break
                if ip:
                    break
            if not ip:
                ip = "No disponible"
        except Exception:
            ip = "No disponible"
        self.ip_input = QLineEdit()
        self.ip_input.setText(ip)
        self.ip_input.setReadOnly(True)
        self.ip_input.setMinimumHeight(32)
        layout.addWidget(self.ip_label)
        layout.addWidget(self.ip_input)

        # Licencia
        self.license_label = QLabel("Licencia:")
        self.license_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.license_input = QLineEdit()
        self.license_input.setReadOnly(True)
        self.license_input.setMinimumHeight(32)
        layout.addWidget(self.license_label)
        layout.addWidget(self.license_input)

        # Botones
        self.button_layout = QHBoxLayout()

        self.btn_generate_license = QPushButton("Generar Licencia")
        self.btn_generate_license.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        self.btn_generate_license.clicked.connect(self.generate_license)
        self.button_layout.addWidget(self.btn_generate_license)

        self.btn_register_form = QPushButton("Registrar")
        self.btn_register_form.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #37D278;
            }
        """)
        self.btn_register_form.clicked.connect(self.register_user)
        self.button_layout.addWidget(self.btn_register_form)

        layout.addLayout(self.button_layout)

        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.register_page.mousePressEvent = self.handle_register_click


    def handle_register_click(self, event):
        
            self.hostname_label.setVisible(True)
            self.hostname_input.setVisible(True)
            self.ip_label.setVisible(True)
            self.ip_input.setVisible(True)
            self.license_label.setVisible(True)
            self.license_input.setVisible(True)
            self.btn_generate_license.setVisible(True)
            self.btn_register.setVisible(True)
    

    def load_system_info(self):
        try:
            import wmi
            c = wmi.WMI()
            # Procesador
            cpu_name = next((cpu.Name.strip() for cpu in c.Win32_Processor()), None)
            # GPU principal
            gpu_name = next((gpu.Name.strip() for gpu in c.Win32_VideoController()), "No detectada")
            # Batería
            battery = next(iter(c.Win32_Battery()), None)
            battery_percent = f"{battery.EstimatedChargeRemaining}%" if battery else "No disponible"
            battery_status = "Cargando" if battery and getattr(battery, "BatteryStatus", 0) == 6 else "No cargando"
        except Exception as e:
            print(f"Error usando wmi: {e}")
            cpu_name = platform.processor() or platform.uname().processor or "Desconocido"
            gpu_name = "No detectada"
            battery_percent = "No disponible"
            battery_status = "No disponible"

        # Almacenamiento
        try:
            disk = psutil.disk_usage('/')
            disk_total = f"{disk.total / (1024**3):.1f} GB"
            disk_used = f"{disk.used / (1024**3):.1f} GB"
            disk_free = f"{disk.free / (1024**3):.1f} GB"
        except Exception:
            disk_total = disk_used = disk_free = "No disponible"

        # Red
        try:
            addrs = psutil.net_if_addrs()
            ip = None
            for iface, addr_list in addrs.items():
                for addr in addr_list:
                    if addr.family == 2 and not addr.address.startswith("169.254"):
                        ip = addr.address
                        iface_name = iface
                        break
                if ip:
                    break
            if not ip:
                ip, iface_name = "No disponible", "No disponible"
        except Exception:
            ip, iface_name = "No disponible", "No disponible"

        # Arquitectura
        arch = platform.machine()
        if arch.upper() == "AMD64":
            arch = "64 bits"

        # Marca para logo/avatar
        manufacturer, _ = get_pc_brand()
        if manufacturer == "windows":
            print("ATENCIÓN: No se pudo detectar el fabricante real, se usará 'windows'. Revisa la instalación y activación del entorno virtual.")
        self.system_data = {
            'os': f"{platform.system()} {platform.release()}",
            'hostname': platform.node(),
            'processor': cpu_name,
            'gpu': gpu_name,
            'cores': psutil.cpu_count(logical=False),
            'threads': psutil.cpu_count(logical=True),
            'ram': f"{psutil.virtual_memory().total / (1024**3):.2f} GB",
            'cpu_freq': f"{(psutil.cpu_freq().current or 0) / 1000:.2f} GHz",
            'architecture': arch,
            'disk_total': disk_total,
            'disk_used': disk_used,
            'disk_free': disk_free,
            'ip': ip,
            'iface': iface_name,
            'battery_percent': battery_percent,
            'battery_status': battery_status,
            'datetime': "",
            'manufacturer': manufacturer
        }
    def create_info_row(self, title, value):
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(10, 5, 10, 5)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; color: #34495e;")
        title_label.setFixedWidth(200)

        layout.addWidget(title_label)
        if isinstance(value, QLabel):
            layout.addWidget(value)
        else:
            value_label = QLabel(str(value))
            value_label.setStyleSheet("color: #7f8c8d;")
            layout.addWidget(value_label)
        return widget

    def create_section_title(self, text, emoji="🖥️"):
        title_widget = QWidget()
        layout = QHBoxLayout(title_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        icon_label = QLabel(emoji)
        icon_label.setStyleSheet("font-size: 32px; margin-right: 12px;")
        text_label = QLabel(text)
        text_label.setStyleSheet("font-size: 28px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(icon_label)
        layout.addWidget(text_label)
        return title_widget

    def show_system_info(self):
    
        """Muestra la información del sistema en el área principal"""
        # Limpiar contenido anterior
        old_layout = self.system_info_page.layout()
        if old_layout is not None:
            # Eliminar widgets del layout anterior
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            # Eliminar el layout del widget
            old_layout.deleteLater()


        self.stacked_widget.setCurrentWidget(self.system_info_page)
        self.set_sidebar_button_states(self.btn_home)
        # Margen reducido para aprovechar espacio
        layout = QVBoxLayout(self.system_info_page)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)
        
        # Encabezado
        header = QLabel("Información del Sistema")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        layout.addWidget(header)

        # Logo/avatar centrado arriba
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        logo_path = None
        manufacturer = self.system_data['manufacturer'].lower()
        print(f"Fabricante detectado: {manufacturer}")

        # Diccionario de marcas y nombres de archivo
        brand_logos = {
            "lenovo": "lenovo.png",
            "asus": "ASUS.png",
            "hp": "HP.png"
            # Añade aquí más marcas si tienes más logos
        }

        for brand, filename in brand_logos.items():
            if brand in manufacturer:
                logo_path = os.path.join(os.path.dirname(__file__), "images", filename)
                print(f"Logo seleccionado: {logo_path}")
                break

        if logo_path and os.path.exists(logo_path):
            print("Logo encontrado y cargado.")
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(180, 70, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print("No se encontró el logo, se muestra emoji.")
            logo_label.setText("🖥️")
            logo_label.setStyleSheet("font-size: 48px;")

        layout.addWidget(logo_label)

        # Info en dos columnas
        from datetime import datetime
        now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # Creamos un QLabel para la fecha y hora y lo guardamos como atributo
        self.datetime_label = QLabel()
        self.datetime_label.setStyleSheet("color: #7f8c8d;")
        self.datetime_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        info_list = [
            ("Sistema Operativo:", self.system_data['os']),
            ("Nombre del Equipo:", self.system_data['hostname']),
            ("Procesador:", self.system_data['processor']),
            ("GPU:", self.system_data['gpu']),
            ("Arquitectura:", self.system_data['architecture']),
            ("Núcleos Físicos:", self.system_data['cores']),
            ("Núcleos Lógicos:", self.system_data['threads']),
            ("Frecuencia CPU:", self.system_data['cpu_freq']),
            ("Memoria RAM:", self.system_data['ram']),
            ("Disco total:", self.system_data['disk_total']),
            ("Disco usado:", self.system_data['disk_used']),
            ("Disco libre:", self.system_data['disk_free']),
            ("IP local:", self.system_data['ip']),
            ("Adaptador de red:", self.system_data['iface']),
            ("Batería:", f"{self.system_data['battery_percent']} ({self.system_data['battery_status']})"),
            # En vez de texto, ponemos el QLabel de fecha/hora
            ("Fecha y hora:", self.datetime_label)
        ]

        # Creamos un temporizador para actualizar la hora cada segundo
        if not hasattr(self, 'datetime_timer'):
            self.datetime_timer = QTimer(self)
            self.datetime_timer.timeout.connect(
            lambda: self.datetime_label.setText(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            )
            self.datetime_timer.start(1000)

        # Crear columnas
        mid = len(info_list) // 2 + len(info_list) % 2
        col1 = QVBoxLayout()
        col2 = QVBoxLayout()
        for title, value in info_list[:mid]:
            col1.addWidget(self.create_info_row(title, value))
        for title, value in info_list[mid:]:
            col2.addWidget(self.create_info_row(title, value))

        columns_widget = QWidget()
        columns_layout = QHBoxLayout(columns_widget)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        columns_layout.addLayout(col1)
        columns_layout.addLayout(col2)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setWidget(columns_widget)
        layout.addWidget(scroll_area)

        # Enlaces rápidos (Administrador de tareas / Configuración)
        links_widget = QWidget()
        links_layout = QHBoxLayout(links_widget)
        btn_taskmgr = QPushButton("Administrador de tareas")
        btn_taskmgr.clicked.connect(lambda: os.system("start taskmgr"))
        btn_settings = QPushButton("Configuración")
        btn_settings.clicked.connect(lambda: os.system("start ms-settings:"))
        links_layout.addWidget(btn_taskmgr)
        links_layout.addWidget(btn_settings)
        layout.addWidget(links_widget)

        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("color: #bdc3c7; margin: 12px 0;")
        layout.addWidget(separator)

        # Estadísticas en tiempo real
        realtime_stats = QLabel("Estadísticas en Tiempo Real")
        realtime_stats.setStyleSheet("""
            font-size: 16px;
            color: #34495e;
            margin-top: 20px;
            margin-bottom: 10px;
        """)
        layout.addWidget(realtime_stats)

        # Widgets de estadísticas
        self.stats_widget = QWidget()
        self.stats_layout = QHBoxLayout(self.stats_widget)
        self.cpu_usage = QLabel()
        self.cpu_usage.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-weight: bold;
        """)
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
        layout.addWidget(self.stats_widget)

        self.stacked_widget.setCurrentWidget(self.system_info_page)
        self.update_realtime_stats()


    def show_comanda_win(self):
        self.stacked_widget.setCurrentWidget(self.comanda_win_page)
        self.set_sidebar_button_states(self.btn_commands)

    def show_chocolatey_ui(self):
        self.stacked_widget.setCurrentWidget(self.applications_page)

    def show_applications_ui(self):
        self.stacked_widget.setCurrentWidget(self.applications_page)
        self.set_sidebar_button_states(self.btn_apps)
    
    def show_backups_ui(self):
        self.stacked_widget.setCurrentWidget(self.backups_page)
        self.set_sidebar_button_states(self.btn_backups)

    def show_register_ui(self):
        self.stacked_widget.setCurrentWidget(self.register_page)
        self.set_sidebar_button_states(self.btn_register)

    def show_drivers_ui(self):
        self.stacked_widget.setCurrentWidget(self.drivers_page)
        self.set_sidebar_button_states(self.btn_drivers)

    def generate_license(self):
        license_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=20))
        self.license_input.setText(license_code)

    def update_realtime_stats(self):
        """Actualiza las estadísticas en tiempo real"""
        self.cpu_usage.setText(f"CPU: {psutil.cpu_percent()}%") 
        mem = psutil.virtual_memory()
        self.mem_usage.setText(f"RAM: {mem.percent}%")

    def setup_drivers_page(self):
        layout = QVBoxLayout(self.drivers_page)
        layout.setContentsMargins(30, 30, 30, 30)
        title = QLabel("Descarga tus Drivers")
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        layout.addWidget(title)

        # Tabla de marcas y enlaces
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Marca", "Enlace de Drivers"])
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        brands = [
            ("ASUS", "https://www.asus.com/support/"),
            ("MSI", "https://www.msi.com/support"),
            ("GIGABYTE", "https://www.gigabyte.com/Support"),
            ("ASRock", "https://www.asrock.com/support/index.asp"),
            ("EVGA", "https://www.evga.com/support/download/"),
            ("Zotac", "https://www.zotac.com/support/download"),
            ("Sapphire", "https://www.sapphiretech.com/en/support/"),
            ("XFX", "https://www.xfxforce.com/support/downloads"),
            ("Palit", "https://www.palit.com/palit/download.php"),
            ("PNY", "https://www.pny.com/support"),
            ("Intel", "https://www.intel.com/content/www/us/en/download-center/home.html"),
            ("AMD", "https://www.amd.com/en/support"),
            ("NVIDIA", "https://www.nvidia.com/Download/index.aspx"),
            ("Samsung", "https://semiconductor.samsung.com/consumer-storage/support/tools/"),
            ("Kingston", "https://www.kingston.com/support/technical/products"),
            ("Corsair", "https://www.corsair.com/us/en/support/downloads"),
            ("Crucial", "https://www.crucial.com/support/drivers-updates"),
            ("Western Digital", "https://support.wdc.com/downloads.aspx"),
            ("Seagate", "https://www.seagate.com/support/downloads/"),
            ("Toshiba", "https://www.toshiba-storage.com/support/"),
            ("Sandisk", "https://kb.sandisk.com/app/answers/list/search/1/kw/drivers"),
            ("Patriot", "https://www.patriotmemory.com/pages/support"),
            ("G.Skill", "https://www.gskill.com/download/1502180912/1548819606/DRAM-Module"),
            ("TeamGroup", "https://www.teamgroupinc.com/en/support/"),
            ("HyperX", "https://www.hyperxgaming.com/unitedstates/us/support/"),
            ("Adata", "https://www.adata.com/en/support/download/"),
            ("Mushkin", "https://mushkin.com/support/"),
            ("Apacer", "https://consumer.apacer.com/eng/support/Driver"),
            ("Biostar", "https://www.biostar.com.tw/app/en/support/download.php"),
            ("Foxconn", "https://www.foxconnchannel.com/ProductDetail.aspx?T=Motherboard"),
            ("ECS", "https://www.ecs.com.tw/en/support/download"),
            ("Supermicro", "https://www.supermicro.com/support/resources/downloadcenter"),
            ("Dell", "https://www.dell.com/support/home/drivers"),
            ("HP", "https://support.hp.com/us-en/drivers"),
            ("Lenovo", "https://pcsupport.lenovo.com/es/es/pagenotfound"),
            ("Acer", "https://www.acer.com/ac/en/US/content/drivers"),
            ("Gigabyte Aorus", "https://www.aorus.com/support/download/"),
            ("Alienware", "https://www.dell.com/support/home/drivers"),
            ("Logitech", "https://support.logi.com/hc/es/articles/360024692814"),
            ("Razer", "https://support.razer.com/pc/"),
            ("SteelSeries", "https://steelseries.com/engine"),
            ("Cooler Master", "https://www.coolermaster.com/catalog/support-downloads/"),
            ("NZXT", "https://nzxt.com/software"),
            ("Thermaltake", "https://www.thermaltake.com/support/download"),
            ("Seasonic", "https://seasonic.com/support/downloads"),
            ("Be Quiet!", "https://www.bequiet.com/en/downloads"),
            ("Enermax", "https://www.enermax.com/en/support/download"),
            ("Realtek", "https://www.realtek.com/en/downloads"),
            ("Broadcom", "https://www.broadcom.com/support/download-search"),
            ("Killer", "https://www.killernetworking.com/driver-downloads/"),
            ("TP-Link", "https://www.tp-link.com/support/download/"),
        ]

        # Detectar marca del equipo
        manufacturer, model = get_pc_brand()
        # Marcas genéricas que siempre se muestran
        always_show = ["intel", "amd", "nvidia", "realtek"]

        # Filtrar marcas relevantes
        filtered = []
        for brand, url in brands:
            if brand.lower() in manufacturer or brand.lower() in model or brand.lower() in always_show:
                filtered.append((brand, url))

        # Si no se detecta ninguna, mostrar todas
        if not filtered:
            filtered = brands

        self.table.setRowCount(len(filtered))
        for row, (brand, url) in enumerate(filtered):
            self.table.setItem(row, 0, QTableWidgetItem(brand))
            link_item = QTableWidgetItem(url)
            link_item.setForeground(Qt.GlobalColor.blue)
            link_item.setToolTip("Haz doble clic para abrir el enlace")
            self.table.setItem(row, 1, link_item)

        self.table.cellDoubleClicked.connect(self.open_driver_link)
        layout.addWidget(self.table)

    def open_driver_link(self, row, column):
        if column == 1:
            url = self.table.item(row, column).text()
            QDesktopServices.openUrl(QUrl(url))

    def register_user(self):
        from requests.auth import HTTPBasicAuth
        import requests

        email = self.email_input.text()
        password = self.password_input.text()
        license_code = self.license_input.text()
        hostname = self.hostname_input.text()
        ip_local = self.ip_input.text()

        # URL del endpoint de registro
        url = "http://assistantaio.dyndns.org:7070/apex/aio/api/equipos/registrar"

        # Cabeceras requeridas por ORDS (van como headers)
        headers = {
            "licencia": license_code,
            "nombre": hostname,
            "ip": ip_local,
            "ubicacion": "Oficina Principal",
            "cargo": "Equipo Técnico",
            "descripcion": "Equipo registrado desde Assistant AIO",
            "estado": "CORRECTO",
            "activo": "S",
            "usado": "0",           # puedes cambiar esto si tienes valor real
            "capacidad": "100 GB"   # puedes ajustar también
        }

        try:
            # Llamada POST con Basic Auth del cliente
            response = requests.post(url, headers=headers, auth=HTTPBasicAuth(email, password))

            if response.status_code == 200:
                QMessageBox.information(self, "Registro exitoso", "El equipo se registró correctamente.")
            else:
                QMessageBox.critical(self, "Error en el registro",
                                    f"Código: {response.status_code}\nRespuesta:\n{response.text}")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Excepción al registrar:\n{str(e)}")


    def ocultar_campos_registro(self):
        # Oculta los campos de registro principales
        self.email_input.setVisible(False)
        self.name_input.setVisible(False)
        self.phone_input.setVisible(False)
        self.position_input.setVisible(False)
        self.location_input.setVisible(False)
        self.descripcion_input.setVisible(False)

        # Oculta las etiquetas asociadas
        for widget in self.register_page.findChildren(QLabel):
            if widget.text() in [
                "Correo Electrónico:",
                "Nombre completo:",
                "Teléfono:",
                "Cargo/Puesto:",
                "Ubicación (Ciudad, Provincia):",
                "Descripción:"
            ]:
                widget.setVisible(False)

        # Oculta el botón Enviar Formulario
        self.btn_send_form.setVisible(False)

        # Solo crear los mensajes si no existen ya
        if not hasattr(self, "agradecimiento_label"):
            self.agradecimiento_label = QLabel(
                "Gracias por realizar la solicitud de registro, nos pondremos en contacto con\nusted en la mayor brevedad posible."
            )
            self.agradecimiento_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            self.agradecimiento_label.setStyleSheet("font-size: 22px; color: #222; margin-top: 40px;")
            self.register_page.layout().addWidget(self.agradecimiento_label)

        if not hasattr(self, "registro_pendiente_label"):
            self.registro_pendiente_label = QLabel("Registro pendiente")
            self.registro_pendiente_label.setStyleSheet("color: red; font-weight: bold; font-size: 20px;")
            self.registro_pendiente_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
            self.register_page.layout().addWidget(self.registro_pendiente_label)

        # Asegúrate de que estén visibles
        self.agradecimiento_label.setVisible(True)
        self.registro_pendiente_label.setVisible(True)
        
    def registrar_equipo(self):
        # Mensaje para verificar que el botón fue presionado
        QMessageBox.information(self, "Depuración", "Intentando realizar la conexión...")

        # Obtener los datos del formulario
        nombre = self.name_input.text()
        ip = self.ip_input.text()
        licencia = self.license_input.text()
        correo = self.email_input.text()
        contraseña = self.password_input.text()

        # Validar que todos los campos estén completos
        if not (nombre and ip and licencia and correo and contraseña):
            QMessageBox.warning(self, "Error", "Por favor, completa todos los campos.")
            return

        # URL de la API
        url = "http://assistantaio.dyndns.org:7070/apex/aio/api/equipos/actualizar"

        # Datos a enviar
        datos = {
            "nombre_equipo": nombre,
            "ip_local": ip,
            "licencia": licencia,
            "correo": correo,
            "contraseña": contraseña
        }

        # Credenciales de Basic Auth
        usuario = "WSAIO"  # Reemplaza con tu usuario
        contraseña_auth = "WSAIO"  # Reemplaza con tu contraseña

        try:
            # Mensaje para verificar que se está intentando la conexión
            QMessageBox.information(self, "Depuración", "Conectando con la API...")

            # Realizar la petición PUT con Basic Auth
            respuesta = requests.put(url, json=datos, auth=HTTPBasicAuth(usuario, contraseña_auth))

            # Verificar la respuesta
            if respuesta.status_code == 200:
                QMessageBox.information(self, "Éxito", "Información enviada correctamente.")
            else:
                QMessageBox.warning(self, "Error", f"Error al enviar la información: {respuesta.text}")
        except Exception as e:
            # Mostrar el error en una alerta
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")

    def actualizar_espacio_usado(self, licencia, espacio_usado):
        # URL de la API
        url = "http://assistantaio.dyndns.org:7070/apex/aio/api/equipos/actualizar"

        # Credenciales de Basic Auth
        usuario = "WSAIO"
        contraseña = "WSAIO"

        # Cabeceras requeridas
        headers = {
            "licencia": licencia,
            "usado": str(espacio_usado)  # Convertir el espacio usado a string
        }

        try:
            # Realizar la petición PUT con Basic Auth y las cabeceras
            respuesta = requests.put(url, headers=headers, auth=HTTPBasicAuth(usuario, contraseña))

            # Verificar la respuesta
            if respuesta.status_code == 200:
                QMessageBox.information(self, "Éxito", "Espacio usado actualizado correctamente.")
            else:
                QMessageBox.warning(self, "Error", f"Error al actualizar el espacio usado: {respuesta.text}")
        except Exception as e:
            # Mostrar el error en una alerta
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")

    def actualizar_equipo(self):
        # URL de la API
        url = "http://assistantaio.dyndns.org:7070/apex/aio/api/equipos/actualizar"

        # Credenciales de Basic Auth
        usuario = "WSAIO"
        contraseña = "WSAIO"

        # Cabeceras requeridas
        headers = {
            "licencia": self.license_input.text(),
            "usado": "40",
            "estado": "CORRECTO",
            "nombre": self.hostname_input.text(),
            "ip": self.ip_input.text(),
            "ubicacion": "Oficina",
            "capacidad": "200",
            "activo": "true"
        }

        print("Datos enviados:", headers)  # Depuración

        try:
            respuesta = requests.put(url, headers=headers, auth=HTTPBasicAuth(usuario, contraseña))
            print("Estado HTTP:", respuesta.status_code)
            print("Respuesta del servidor:", respuesta.text)

            if respuesta.status_code == 200:
                QMessageBox.information(self, "Éxito", "Equipo actualizado correctamente.")
            else:
                QMessageBox.warning(self, "Error", f"Error al actualizar el equipo: {respuesta.text}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {e}")

if __name__ == "__main__":
    if not ctypes.windll.shell32.IsUserAnAdmin():
        # Relaunch the script with admin rights
        import sys
        import os
        params = " ".join([f'"{x}"' for x in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, f'"{__file__}" {params}', None, 1
        )
        sys.exit()
        
        # ---- CODIGO PARA OCULTAR LA CONSOLA CUANDO SE EJECUTA EL PROGRAMA COMO ADMINISTRADOR ----
        # import subprocess
        # import sys
        # import os
        # params = " ".join([f'"{x}"' for x in sys.argv])
        # executable = sys.executable
        # script = os.path.abspath(__file__)
        # subprocess.run(
        #     ['powershell', '-Command',
        #      f'Start-Process "{executable}" -ArgumentList \'"{script}" {params}\' -Verb RunAs -WindowStyle Hidden'],
        #     shell=True
        # )
        # sys.exit()
    else:
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(10)
        app.setFont(font)
        
        window = SystemInfoApp()
        window.show()
        app.exec()
