
import sys
import platform
import psutil
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QWidget,
                             QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, 
                             QFrame, QStackedWidget, QTabWidget, QLineEdit, QListWidget
                             QLineEdit, QSpacerItem, QSizePolicy, QMessageBox,
                             QTableWidget, QTableWidgetItem, QAbstractItemView)
from PyQt6.QtGui import QIcon, QFont, QDesktopServices
from PyQt6.QtCore import QSize, Qt, QTimer, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtCore import QUrl
from comandowin import ComandaWin  # Importar la clase ComandaWin
from chocolatey import ChocolateyApp
from app_backup import BackupApp
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


class SystemInfoApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Assistant AIO")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(1000, 600)
        # self.setMaximumSize(1000,800)
        
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
        self.btn_drivers.clicked.connect(self.show_drivers_ui)
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
        self.btn_backups.clicked.connect(self.show_backups_ui)
        sidebar_layout.addWidget(self.btn_backups)
        sidebar_layout.addStretch()
        self.main_layout.addWidget(sidebar)

    def setup_main_content(self):
        """Configura el área de contenido principal"""
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        # Página de información del sistema (INICIO)
        self.system_info_page = QWidget()
        self.stacked_widget.addWidget(self.system_info_page)

        # Página de Drivers
        self.drivers_page = QWidget()
        self.setup_drivers_page()
        self.stacked_widget.addWidget(self.drivers_page)
    
       
        # Página de Aplicaciones (Aplicaciones)
        self.applications_page = ChocolateyApp()
        self.stacked_widget.addWidget(self.applications_page)
        
        # Página de Comandos Windows
        self.comanda_win_page = ComandaWin()
        self.stacked_widget.addWidget(self.comanda_win_page)
        
        # # Página de Backups
        self.backups_page = BackupApp()
        self.stacked_widget.addWidget(self.backups_page)
        
     def setup_register_page(self):
        layout = QVBoxLayout(self.register_page)
        layout = QVBoxLayout(self.register_page)
        layout.setContentsMargins(60, 60, 60, 60)
        layout.setContentsMargins(60, 60, 60, 60)

    def show_register_ui(self):
        self.stacked_widget.setCurrentWidget(self.register_page)
        self.stacked_widget.setCurrentWidget(self.register_page)
    
    def show_drivers_ui(self):
        self.stacked_widget.setCurrentWidget(self.drivers_page)
       
        

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
    
    def show_backups_ui(self):
        """Muestra la vista de Backups"""
        self.stacked_widget.setCurrentWidget(self.backups_page)


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
            ("Lenovo", "https://pcsupport.lenovo.com/us/en/downloads"),
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
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Configurar fuente global
    font = QFont()
    font.setFamily("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
    
    window = SystemInfoApp()
    window.show()
