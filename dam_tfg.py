import ctypes
import sys
import os
import platform
import sys
import psutil
import random
import string

from PyQt6.QtCore import QSize, Qt, QTimer, QUrl
from datetime import datetime
from PyQt6.QtWidgets import QScrollArea
from PyQt6.QtGui import QIcon, QFont, QDesktopServices, QPixmap
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QFrame, QStackedWidget,
                             QLineEdit, QSpacerItem, QSizePolicy, QMessageBox,
                             QTableWidget, QTableWidgetItem, QAbstractItemView)
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from io import BytesIO

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
            return manufacturer, model
    except Exception:
        uname = platform.uname()
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
        self.timer.start(400)  # Actualizar cada segundo

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

        # Correo electrónico
        email_label = QLabel("Correo Electrónico:")
        email_label.setStyleSheet("font-weight: bold; color: #34495e;")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Introduce tu correo electrónico")
        self.email_input.setMinimumHeight(32)
        layout.addWidget(email_label)
        layout.addWidget(self.email_input)

        # Contraseña
        password_label = QLabel("Contraseña:")
        password_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Introduce tu contraseña")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setMinimumHeight(32)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)

        # Licencia
        license_label = QLabel("Licencia:")
        license_label.setStyleSheet("font-weight: bold; color: #34495e; margin-top: 10px;")
        self.license_input = QLineEdit()
        self.license_input.setReadOnly(True)
        self.license_input.setMinimumHeight(32)
        layout.addWidget(license_label)
        layout.addWidget(self.license_input)

        # Botón Generar Licencia
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
        layout.addWidget(self.btn_generate_license)

        # Espaciador
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

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

        if "lenovo" in manufacturer:
            logo_path = os.path.join(os.path.dirname(__file__), "images", "Branding_lenovo-logo_lenovologoposred_low_res.png")
        elif "asus" in manufacturer:
            logo_path = os.path.join(os.path.dirname(__file__), "images", "ASUS_Corporate_Logo.png")
        elif "hp" in manufacturer:
            logo_path = os.path.join(os.path.dirname(__file__), "images", "HP_logo_2008.png")
        # Añade más marcas si quieres...

        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            logo_label.setPixmap(pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
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
