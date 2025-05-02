import subprocess
import json
import re
import os
import ctypes

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QTextEdit, QFileDialog, QWidget, QTabWidget, QListWidgetItem,
    QFrame, QSizePolicy, QSpacerItem, QComboBox, QDialog, QVBoxLayout, QLabel, QDialog, 
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QGuiApplication

# DEPENDENCIAS NECESARIAS PARA LA OPCION DE INSTALAR CHOCOLATEY AUTOMATICAMENTE
# from PyQt6.QtWidgets import QProgressBar
# from PyQt6.QtCore import QThread, pyqtSignal
# from PyQt6.QtGui import QIcon


class ChocolateyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Package App Manager")
        
        self.setGeometry(100, 100, 700, 500)
        self.setStyleSheet(self.get_styles())
        self.app_dict = {}
        self.group_dict = {}
        self.package_manager = 'winget'
        self.setup_ui()

    def is_running_as_admin(self):
        """Devuelve True si el programa se ejecuta como Administrador"""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False

    def get_styles(self):
        return """
        QWidget {
            background-color: #f0f3f5;
            font-family: 'Segoe UI';
        }
        QLabel {
            font-size: 16px;
        }
        QPushButton {
            background-color: #2980b9;
            color: white;
            padding: 8px 16px;
            font-size: 14px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #3498db;
        }
        QLineEdit {
            padding: 6px;
            font-size: 14px;
            border: 1px solid #ccc;
            border-radius: 4px;
        }
        QListWidget {
            background-color: white;
            border: 1px solid #dcdcdc;
            font-size: 14px;
        }
        QTextEdit {
            background-color: #ffffff;
            font-size: 13px;
            border: 1px solid #ccc;
            padding: 6px;
        }
        """


    def create_frame(self):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        return frame


    def setup_ui(self):
        # Crear layout principal
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        
        # Crear título centrado
        header = QLabel("🧩 Gestor de Aplicaciones")
        header.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        header.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")

        # Añadir al layout
        layout.addWidget(header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
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
        """)
        self.tabs.addTab(self.create_home_tab(), "🏠 Inicio")
        self.tabs.addTab(self.create_search_tab(), "🔍 Buscar e Instalar")
        self.tabs.addTab(self.create_group_tab(), "📦 Agrupaciones")
        self.tabs.addTab(self.create_manage_tab(), "🛠️ Actualizar/Desinstalar")
        self.tabs.addTab(self.create_log_tab(), "📝 Historial")
        self.setCentralWidget(self.tabs)


    def create_title_label(self, text):
        label = QLabel(text)
        label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        label.setStyleSheet("color: #2c3e50;")
        return label


    def create_button(self, text, callback):
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        return btn


    def add_spacer(self, layout):
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))


    def is_chocolatey_installed(self):
        """Verifica si Chocolatey está instalado ejecutando su ruta absoluta"""
        choco_path = r"C:\ProgramData\chocolatey\bin\choco.exe"
        if os.path.exists(choco_path):
            try:
                result = subprocess.run([choco_path, "-v"], capture_output=True, text=True)
                return result.returncode == 0 and result.stdout.strip() != ""
            except Exception as e:
                self.log_text.append(f"Error al verificar Chocolatey: {e}")
        return False
        

    def is_winget_installed(self):
        """Verifica si WinGet está instalado"""
        try:
            result = subprocess.run(["winget", "-v"], capture_output=True, text=True, shell=True)
            return result.returncode == 0
        except FileNotFoundError:
            return False
        

    def show_toast(self, message, duration=3000):
        """Muestra una notificación tipo toast en la parte inferior derecha"""
        toast = QLabel(message, self)
        toast.setStyleSheet("""
            QLabel {
                background-color: #2ecc71;
                color: white;
                padding: 10px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        toast.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toast.adjustSize()

        x = self.width() - toast.width() - 400
        y = self.height() - toast.height() - 40
        toast.move(x, y)
        toast.show()

        QTimer.singleShot(duration, toast.deleteLater)


    def create_home_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(10)
        
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2980b9, stop:1 #3498db);
                border-radius: 12px;
                color: white;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(30, 25, 30, 25)
        
        title_row = QHBoxLayout()
        
        logo_label = QLabel("🚀")
        logo_label.setFont(QFont("Segoe UI Emoji", 40))
        logo_label.setStyleSheet("color: white; background: transparent;")
        title_row.addWidget(logo_label)
        
        title_column = QVBoxLayout()
        title = QLabel("Package App Manager")
        title.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
        title.setStyleSheet("color: white; background: transparent;")
        title_column.addWidget(title)
        
        subtitle = QLabel("Gestión simplificada de software para Windows")
        subtitle.setFont(QFont("Segoe UI", 13))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.85); background: transparent;")
        title_column.addWidget(subtitle)
        
        title_row.addLayout(title_column)
        title_row.addStretch()

        selector_column = QVBoxLayout()
        selector_label = QLabel("Gestor de Paquetes")
        selector_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        selector_label.setStyleSheet("color: white; background: transparent;")
        selector_column.addWidget(selector_label)

        self.package_selector = QComboBox()
        self.package_selector.addItems(["WinGet", "Chocolatey"])
        self.package_selector.setCurrentIndex(0)
        self.package_selector.setStyleSheet("""
            QComboBox {
                background-color: white;
                color: #2c3e50;
                padding: 6px 10px;
                border-radius: 6px;
                font-size: 13px;
                min-width: 150px;
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #d0e7f9;
                selection-color: #000000;
                border: 0;
            }
        """)
        self.package_selector.currentIndexChanged.connect(self.on_package_manager_changed)
        selector_column.addWidget(self.package_selector)

        title_row.addLayout(selector_column)

        header_layout.addLayout(title_row)
        
        layout.addWidget(header_frame)
        
        cards_container = QFrame()
        cards_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
            }
        """)
        cards_layout = QHBoxLayout(cards_container)
        cards_layout.setSpacing(20)
        
        system_card = QFrame()
        system_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        system_layout = QVBoxLayout(system_card)
        system_layout.setContentsMargins(20, 20, 20, 20)
        
        system_header = QHBoxLayout()
        system_icon = QLabel("🖥️")
        system_icon.setFont(QFont("Segoe UI Emoji", 18))
        system_header.addWidget(system_icon)
        
        system_title = QLabel("Sistema")
        system_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        system_title.setStyleSheet("color: #2c3e50;")
        system_header.addWidget(system_title)
        system_header.addStretch()
        system_layout.addLayout(system_header)
        
        sys_separator = QFrame()
        sys_separator.setFrameShape(QFrame.Shape.HLine)
        sys_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        system_layout.addWidget(sys_separator)
        
        windows_status = QLabel("Windows 10/11")
        windows_status.setFont(QFont("Segoe UI", 12))
        windows_status.setStyleSheet("color: #34495e; padding: 10px 0;")
        windows_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_layout.addWidget(windows_status)
        
        self.status_indicator = QLabel("✓ Operativo")
        self.status_indicator.setFont(QFont("Segoe UI", 11))
        self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 10px; background-color: rgba(46, 204, 113, 0.1); padding: 5px;")
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_layout.addWidget(self.status_indicator)
        
        cards_layout.addWidget(system_card)
        
        winget_card = QFrame()
        winget_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        winget_layout = QVBoxLayout(winget_card)
        winget_layout.setContentsMargins(20, 20, 20, 20)
        
        winget_header = QHBoxLayout()
        winget_icon = QLabel("📦")
        winget_icon.setFont(QFont("Segoe UI Emoji", 18))
        winget_header.addWidget(winget_icon)
        
        winget_title = QLabel("WinGet")
        winget_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        winget_title.setStyleSheet("color: #2c3e50;")
        winget_header.addWidget(winget_title)
        winget_header.addStretch()
        winget_layout.addLayout(winget_header)
        
        win_separator = QFrame()
        win_separator.setFrameShape(QFrame.Shape.HLine)
        win_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        winget_layout.addWidget(win_separator)
        
        winget_status = QLabel("Gestor de paquetes")
        winget_status.setFont(QFont("Segoe UI", 12))
        winget_status.setStyleSheet("color: #34495e; padding: 10px 0;")
        winget_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winget_layout.addWidget(winget_status)
        
        if self.is_winget_installed():
            winget_indicator = QLabel("✓ Detectado")
            winget_indicator.setFont(QFont("Segoe UI", 11))
            winget_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 10px; background-color: rgba(46, 204, 113, 0.1); padding: 5px;")
        else:
            winget_indicator = QLabel("✕ No detectado")
            winget_indicator.setFont(QFont("Segoe UI", 11))
            winget_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 10px; background-color: rgba(231, 76, 60, 0.1); padding: 5px;")

        winget_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winget_layout.addWidget(winget_indicator)
        
        cards_layout.addWidget(winget_card)
        
        choco_card = QFrame()
        choco_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        choco_layout = QVBoxLayout(choco_card)
        choco_layout.setContentsMargins(20, 20, 20, 20)
        
        choco_header = QHBoxLayout()
        choco_icon = QLabel("🍫")
        choco_icon.setFont(QFont("Segoe UI Emoji", 18))
        choco_header.addWidget(choco_icon)
        
        choco_title = QLabel("Chocolatey")
        choco_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        choco_title.setStyleSheet("color: #2c3e50;")
        choco_header.addWidget(choco_title)
        choco_header.addStretch()
        choco_layout.addLayout(choco_header)
        
        choco_separator = QFrame()
        choco_separator.setFrameShape(QFrame.Shape.HLine)
        choco_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        choco_layout.addWidget(choco_separator)
        
        choco_status = QLabel("Gestor de paquetes")
        choco_status.setFont(QFont("Segoe UI", 12))
        choco_status.setStyleSheet("color: #34495e; padding: 10px 0;")
        choco_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        choco_layout.addWidget(choco_status)
        
        if self.is_chocolatey_installed():
            choco_indicator = QLabel("✓ Detectado")
            choco_indicator.setFont(QFont("Segoe UI", 11))
            choco_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            choco_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 10px; background-color: rgba(46, 204, 113, 0.1); padding: 5px;")
        else:
            choco_indicator = QLabel("✕ No detectado")
            choco_indicator.setFont(QFont("Segoe UI", 11))
            choco_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            choco_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 10px; background-color: rgba(231, 76, 60, 0.1); padding: 5px;")
        
        choco_layout.addWidget(choco_indicator)
        cards_layout.addWidget(choco_card)
        
        layout.addWidget(cards_container)
        
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        button_layout.setSpacing(30)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        search_btn = QPushButton("🔍 Explorar Aplicaciones")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        search_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        button_layout.addWidget(search_btn)

        update_all_btn = QPushButton("⬆️ Actualizar Todo")
        update_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px 16px;
                font-size: 13px;
                font-weight: bold;
                border-radius: 6px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        update_all_btn.clicked.connect(self.update_all_apps)
        button_layout.addWidget(update_all_btn)

        layout.addLayout(button_layout)

        if hasattr(self, "choco_indicator"):
            if self.is_chocolatey_installed():
                self.choco_indicator.setText("✓ Detectado")
                self.choco_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 10px; background-color: rgba(46, 204, 113, 0.1); padding: 5px;")
            else:
                self.choco_indicator.setText("✕ No detectado")
                self.choco_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 10px; background-color: rgba(231, 76, 60, 0.1); padding: 5px;")

        
        return tab


    def create_search_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.addWidget(self.create_title_label("🔍 Buscar e Instalar Aplicaciones"))

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Escribe el nombre de una aplicación...")

        self.search_bar.returnPressed.connect(self.search_apps)

        layout.addWidget(self.search_bar)

        self.search_results = QListWidget()
        layout.addWidget(self.search_results)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button("Instalar", self.install_selected_app))
        buttons_layout.addWidget(self.create_button("Añadir a Agrupación", self.add_to_group))
        self.add_spacer(buttons_layout)
        layout.addLayout(buttons_layout)

        return tab


    def create_group_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(self.create_title_label("Aplicaciones en Agrupación"))
        self.group_list = QListWidget()
        layout.addWidget(self.group_list)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button("Eliminar", self.delete_from_group))
        buttons_layout.addWidget(self.create_button("Exportar", self.export_group))
        buttons_layout.addWidget(self.create_button("Importar", self.import_group))
        self.add_spacer(buttons_layout)
        layout.addLayout(buttons_layout)

        return tab


    def create_manage_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(self.create_title_label("Aplicaciones Instaladas"))
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Buscar aplicación instalada...")
        self.filter_input.textChanged.connect(self.filter_installed_apps)
        layout.addWidget(self.filter_input)

        self.installed_apps = QListWidget()
        layout.addWidget(self.installed_apps)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.create_button("Actualizar", self.update_selected_apps))
        buttons_layout.addWidget(self.create_button("Desinstalar", self.uninstall_selected_apps))
        self.add_spacer(buttons_layout)
        layout.addLayout(buttons_layout)

        self.load_installed_apps()
        return tab


    def create_log_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)

        layout.addWidget(self.create_title_label("Historial de Actividades"))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        return tab
    
    #********************* CARGAR LSISTA DE PAQUETES *******************
    def load_installed_apps(self):
        if self.package_manager == "winget":
            self.load_installed_apps_winget()
        else:
            self.load_installed_apps_choco()

    
    def load_installed_apps_winget(self):
        """Carga la lista de aplicaciones instaladas con WinGet"""
        self.installed_apps.clear()
        self.all_installed = []
        self.installed_apps_dict = {}

        try:
            result = subprocess.run(
                ["winget", "list"],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace"
            )
            output = result.stdout
            lines = output.splitlines()
            data_started = False

            pattern = re.compile(r'^(.+?)\s{2,}(.+?)\s{2,}', re.UNICODE)

            for line in lines:
                if not data_started:
                    if re.match(r'^[-\s]+$', line) and line.strip():
                        data_started = True
                    continue

                if not line.strip():
                    continue

                match = pattern.match(line)
                if match:
                    app_name = match.group(1).strip()
                    app_id = match.group(2).strip()
                    if app_name.lower() == "nombre":
                        continue

                    self.all_installed.append(app_name)
                    self.installed_apps.addItem(app_name)
                    self.installed_apps_dict[app_name] = app_id

        except Exception as e:
            self.log_text.append(f"Error al cargar aplicaciones instaladas: {e}")


    def load_installed_apps_choco(self):
        """Carga la lista de aplicaciones instaladas usando Chocolatey"""
        self.installed_apps.clear()
        self.all_installed = []

        try:
            result = subprocess.run(
                ["choco", "list", "-i"],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                shell=True
            )
            output = result.stdout
            lines = output.splitlines()

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("Chocolatey") or line.endswith("packages installed.") or line.endswith("applications not managed with Chocolatey."):
                    continue

                if "|" in line:
                    app_name = line.split("|")[0].strip()
                else:
                    parts = line.split()
                    if parts:
                        app_name = parts[0].strip()
                    else:
                        continue

                if app_name:
                    self.all_installed.append(app_name)
                    self.installed_apps.addItem(app_name)

        except Exception as e:
            self.log_text.append(f"Error al listar aplicaciones instaladas en Chocolatey: {e}")


    def filter_installed_apps(self):
        """Filtra las aplicaciones instaladas según el texto ingresado"""
        filter_text = self.filter_input.text().lower()
        self.installed_apps.clear()

        for app in self.all_installed:
            if filter_text in app.lower():
                self.installed_apps.addItem(app)

    #********************* BUSCAR PAQUETES *************************
    def search_apps(self):
        if self.package_manager == "winget":
            self.search_apps_winget()
        else:
            self.search_apps_choco()


    def search_apps_winget(self):
        """Busca aplicaciones con WinGet"""
        query = self.search_bar.text()
        if not query:
            self.log_text.append("Por favor, introduce un término de búsqueda.")
            return

        self.log_text.append(f"Buscando aplicaciones en Winget para '{query}'...")
        self.search_bar.clear()
        self.search_results.clear()
        self.app_dict.clear()

        try:
            result = subprocess.run(
                ["winget", "search", query],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace"
            )
            output = result.stdout
            lines = output.splitlines()
            data_started = False

            pattern = re.compile(r'^(.+?)\s{2,}(.+?)\s{2,}', re.UNICODE)


            for line in lines:
                if not data_started:
                    if re.match(r'^[-\s]+$', line) and line.strip():
                        data_started = True
                    continue

                if not line.strip():
                    continue

                match = pattern.match(line)
                if match:
                    app_name = match.group(1).strip()
                    app_id = match.group(2).strip()
                    if app_name.lower() == "nombre":
                        continue

                    item = QListWidgetItem(app_name)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.search_results.addItem(item)

                    self.app_dict[app_name] = app_id

        except Exception as e:
            self.log_text.append(f"Ocurrió un error: {e}")


    def search_apps_choco(self):
        """Busca aplicaciones usando Chocolatey"""
        query = self.search_bar.text()
        if not query:
            self.log_text.append("Por favor, introduce un término de búsqueda.")
            return

        self.log_text.append(f"Buscando aplicaciones en Chocolatey para '{query}'...")
        self.search_bar.clear()
        self.search_results.clear()
        self.app_dict.clear()

        try:
            result = subprocess.run(
                ["choco", "search", query],
                capture_output=True,
                text=True,
                check=False,
                encoding="utf-8",
                errors="replace",
                shell=True
            )
            output = result.stdout
            lines = output.splitlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith("Chocolatey") or line.endswith("packages found."):
                    continue

                parts = line.split()

                if len(parts) >= 2:
                    app_name = parts[0].strip()
                    app_id = app_name

                    item = QListWidgetItem(app_name)
                    item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    item.setCheckState(Qt.CheckState.Unchecked)
                    self.search_results.addItem(item)
                    self.app_dict[app_name] = app_id

        except Exception as e:
            self.log_text.append(f"Ocurrió un error al buscar en Chocolatey: {e}")

    #****************** INSTALAR PAQUETES SELECICONADOS *************************
    def install_selected_app(self):
        if self.package_manager == "winget":
            self.install_selected_app_winget()
        else:
            self.install_selected_app_choco()


    def install_selected_app_winget(self):
        """Instala la aplicación seleccionada usando Winget"""
        selected_item = self.search_results.currentItem()
        if not selected_item:
            self.log_text.append("Por favor, selecciona una aplicación para instalar.")
            return

        app_name = selected_item.text()
        app_id = self.app_dict.get(app_name)

        if not app_id:
            self.log_text.append(f"No se encontró el ID para la app: {app_name}")
            return
        
        self.log_text.append(f"Instalando {app_id} usando Winget...")
        # try:
        #     subprocess.run(["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
        #     self.log_text.append(f"{app_id} instalado correctamente.")
        # except subprocess.CalledProcessError as e:
        #     self.log_text.append(f"Error al instalar {app_id}: {e}")


    def install_selected_app_choco(self):
        """Instala la aplicación seleccionada usando Chocolatey"""
        selected_item = self.search_results.currentItem()
        if not selected_item:
            self.log_text.append("Por favor, selecciona una aplicación para instalar.")
            return

        app_name = selected_item.text()
        app_id = self.app_dict.get(app_name)

        if not app_id:
            self.log_text.append(f"No se encontró el ID para la app: {app_name}")
            return

        self.log_text.append(f"Instalando {app_name} usando Chocolatey...")

        try:
            subprocess.run(["choco", "install", app_id, "-y"], check=True, shell=True)
            self.log_text.append(f"{app_name} instalado correctamente con Chocolatey.")
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al instalar {app_name} con Chocolatey: {e}")


    def update_all_apps(self):
        """Actualiza todas las aplicaciones instaladas"""
        self.log_text.append("Buscando actualizaciones para todas las aplicaciones...")
        try:
            result = subprocess.run(["winget", "upgrade", "--all", "-e", "--accept-package-agreements", "--accept-source-agreements"], capture_output=True, text=True, check=True)
            self.log_text.append(result.stdout)
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al actualizar aplicaciones: {e}")


    def add_to_group(self):
        """Añade aplicaciones seleccionadas (con check) a la agrupación"""
        added = 0

        for i in range(self.search_results.count()):
            item = self.search_results.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                app_name = item.text()
                app_id = self.app_dict.get(app_name)
                if app_id:
                    if not self.is_already_in_group(app_name):
                        self.group_list.addItem(app_name)
                        self.group_dict[app_name] = app_id
                        self.log_text.append(f"{app_name} añadido a la agrupación.")
                        added += 1
                    item.setCheckState(Qt.CheckState.Unchecked)

        self.show_toast("Añadido a la agrupacion")

        if added == 0:
            self.log_text.append("No se seleccionó ninguna aplicación para añadir.")


    def is_already_in_group(self, text):
        """Evita duplicados en la agrupación"""
        for i in range(self.group_list.count()):
            if self.group_list.item(i).text() == text:
                self.log_text.append(f"{self.group_list.item(i).text()} está ya añadido en la Agrupacion")
                return True
        return False


    def delete_from_group(self):
        """Elimina la aplicación seleccionada de la agrupación"""
        selected_item = self.group_list.currentItem()
        if not selected_item:
            self.log_text.append("Selecciona una aplicación para eliminar de la agrupación.")
            return

        app_name = selected_item.text()
        row = self.group_list.row(selected_item)
        self.group_list.takeItem(row)
        self.log_text.append(f"'{app_name}' eliminado de la agrupación.")
        self.show_toast("Eliminado de la agrupacion")


    def export_group(self):
        """Exporta la agrupación a un archivo JSON"""
        if not self.group_dict:
            self.log_text.append("No hay aplicaciones en la agrupación para exportar.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Exportar Agrupación", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "w") as file:
                    json.dump(self.group_dict, file, indent=4)
                self.log_text.append(f"Agrupación exportada a {file_path}.")
                self.show_toast("Agrupacion exportada con éxito")
            except Exception as e:
                self.log_text.append(f"Error al exportar agrupación: {e}")


    def import_group(self):
        """Importa una agrupación desde un archivo JSON"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Importar Agrupación", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, "r") as file:
                    imported = json.load(file)

                self.group_list.clear()
                self.group_dict.clear()

                for name, app_id in imported.items():
                    self.group_list.addItem(name)
                    self.group_dict[name] = app_id

                self.log_text.append(f"Agrupación importada desde {file_path}.")
                self.show_toast("Agrupacion imporada con éxito")

            except Exception as e:
                self.log_text.append(f"Error al importar agrupación: {e}")
        
    #******************** ACTUALIZAR LOS PAQUETES *************************
    def update_selected_apps(self):
        if self.package_manager == "winget":
            self.update_selected_apps_winget()
        else:
            self.update_selected_apps_choco()


    def update_selected_apps_winget(self):
        """Actualiza las aplicaciones seleccionadas usando Winget"""
        selected_items = [self.installed_apps.item(i).text() for i in range(self.installed_apps.count()) if self.installed_apps.item(i).isSelected()]
        if not selected_items:
            self.log_text.append("Por favor, selecciona al menos una aplicación para actualizar.")
            return

        for app_name in selected_items:
            app_id = self.installed_apps_dict.get(app_name)

            if not app_id:
                self.log_text.append(f"No se encontró el ID para la app: {app_name}")
                continue

            self.log_text.append(f"Actualizando '{app_id}' usando Winget...")
            try:
                subprocess.run(["winget", "upgrade", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
                self.log_text.append(f"{app_name} actualizado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al actualizar '{app_name}': {e}")


    def update_selected_apps_choco(self):
        """Actualiza las aplicaciones seleccionadas usando Chocolatey"""
        selected_items = self.installed_apps.selectedItems()
        if not selected_items:
            self.log_text.append("Por favor, selecciona una o más aplicaciones para actualizar.")
            return

        for item in selected_items:
            app_name = item.text()

            self.log_text.append(f"Actualizando {app_name} usando Chocolatey...")
            try:
                subprocess.run(["choco", "upgrade", app_name, "-y", "--accept-license", "--no-progress"], check=True, shell=True)
                self.log_text.append(f"{app_name} actualizado correctamente con Chocolatey.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al actualizar {app_name} con Chocolatey: {e}")

    #******************** DESISNTALAR LOS PAQUETES ****************************
    def uninstall_selected_apps(self):
        if self.package_manager == "winget":
            self.uninstall_selected_apps_winget()
        else:
            self.uninstall_selected_apps_choco()


    def uninstall_selected_apps_winget(self):
        """Desinstala las aplicaciones seleccionadas"""
        selected_items = [self.installed_apps.item(i).text() for i in range(self.installed_apps.count()) if self.installed_apps.item(i).isSelected()]
        if not selected_items:
            self.log_text.append("Por favor, selecciona al menos una aplicación para desinstalar.")
            return

        for app_name in selected_items:
            app_id = self.installed_apps_dict.get(app_name)

            if not app_id:
                self.log_text.append(f"No se encontró el ID para la app: {app_name}")
                continue

            self.log_text.append(f"Desintalando '{app_id}' usando Winget...")
            try:
                subprocess.run(["winget", "uninstall", "--id", app_id, "-e"], check=True)
                self.log_text.append(f"'{app_id}' desinstalado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al desinstalar '{app_id}' con Winget: {e}")


    def uninstall_selected_apps_choco(self):
        """Desinstala las aplicaciones seleccionadas usando Chocolatey"""
        selected_items = self.installed_apps.selectedItems()
        if not selected_items:
            self.log_text.append("Por favor, selecciona una o más aplicaciones para desinstalar.")
            return

        for item in selected_items:
            app_name = item.text()

            self.log_text.append(f"Desinstalando '{app_name}' usando Chocolatey...")
            try:
                subprocess.run(
                    ["choco", "uninstall", app_name, "-y", "--accept-license", "--no-progress"],
                    check=True,
                    shell=True
                )
                self.log_text.append(f"'{app_name}' desinstalado correctamente con Chocolatey.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al desinstalar '{app_name}' con Chocolatey: {e}")


    def show_choco_manual_install_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(" ")
        dialog.setFixedSize(600, 380)
        dialog.setStyleSheet("""
            QDialog {
                background-color: white;
                border: 0;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
                font-weight: normal;
                margin-bottom: 5px;
                padding: 10px 15px;
                border-radius: 8px;
            }
            QLabel#headerLabel {
                font-size: 16px;
                font-weight: bold;
                color: #1a365d;
                margin-bottom: 5px;
                background: transparent;
                padding: 0;
            }
            QTextEdit {
                background-color: #f0f4f8;
                border: 1px solid #dcdfe6;
                border-radius: 5px;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 13px;
                padding: 5px;
                selection-background-color: #3498db;
            }
            QPushButton {
                background-color: #2563eb;
                color: white;
                font-weight: bold;
                padding: 8px 15px;
                border-radius: 5px;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #1d4ed8;
            }
            QPushButton:pressed {
                background-color: #1e40af;
            }
        """)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título principal
        header_label = QLabel("Instalación Manual de Chocolatey")
        header_label.setObjectName("headerLabel")
        layout.addWidget(header_label)
        
        # Instrucciones
        label = QLabel("Chocolatey no está instalado. Para instalarlo, ejecuta el siguiente comando en PowerShell con privilegios de administrador:")
        label.setWordWrap(True)
        layout.addWidget(label)

        command = (
            "Set-ExecutionPolicy Bypass -Scope Process -Force; "
            "[System.Net.ServicePointManager]::SecurityProtocol = "
            "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
            "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
        )

        text_box = QTextEdit()
        text_box.setPlainText(command)
        text_box.setReadOnly(True)
        text_box.setMinimumHeight(80)
        layout.addWidget(text_box)

        # Botones en layout horizontal
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("📋 Copiar comando")
        copy_button.clicked.connect(lambda: self.copy_to_clipboard_and_notify(command))
        button_layout.addWidget(copy_button)
        
        close_button = QPushButton("✖ Cerrar")
        close_button.clicked.connect(dialog.close)
        close_button.setStyleSheet("""
            background-color: #64748b;
            color: white;
        """)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Nota adicional
        note_label = QLabel("Nota: Después de la instalación, es posible que necesites reiniciar PowerShell para usar Chocolatey.")
        note_label.setStyleSheet("font-style: italic; color: #64748b; font-size: 12px;")
        note_label.setWordWrap(True)
        layout.addWidget(note_label)

        dialog.exec()


    def on_package_manager_changed(self):
        self.package_manager = self.package_selector.currentText().lower()
        if self.package_selector.currentText().lower() == "chocolatey":
            if not self.is_chocolatey_installed():
                self.show_choco_manual_install_dialog()
            else:
                if not self.is_running_as_admin():
                    self.package_selector.setCurrentText("WinGet")
                    QMessageBox.warning(
                        self,
                        "Permisos insuficientes",
                        "Chocolatey necesita permisos de administrador para funcionar correctamente.\n\n"
                        "Cierra y vuelve a abrir el programa usando 'Ejecutar como administrador'."
                    )
                    self.package_manager = "winget"
                    return
            self.package_manager = "choco"
        self.log_text.append(f"GESTOR DE PAQUETE SELECCIONADO: {self.package_manager}")
        self.group_list.clear()
        self.group_dict.clear()
        self.search_results.clear()
        self.log_text.append("Agrupaciones limpiadas al cambiar el gestor de paquetes.")
        self.load_installed_apps()


    def copy_to_clipboard_and_notify(self, text):
        QGuiApplication.clipboard().setText(text)
        QMessageBox.information(self, " ", "El comando se ha copiado al portapapeles.")


    # def show_choco_install_dialog(self):
    #     dialog = QDialog(self)
    #     dialog.setWindowTitle(" ")
    #     dialog.setFixedSize(350, 150)
    #     dialog.setStyleSheet("""
    #         QDialog {
    #             background-color: white;
    #         }
    #         QLabel {
    #             color: #2c3e50;
    #             font-size: 14px;
    #             font-weight: bold;
    #             border-radius: 12px;
    #         }
    #         QProgressBar {
    #             border: none;
    #             border-radius: 12px;
    #             background-color: #f0f0f0;
    #             height: 20px;
    #             text-align: center;
    #             margin-top: 10px;
    #             margin-bottom: 10px;
    #             color: white;
    #             font-weight: bold;
    #         }
    #         QProgressBar::chunk {
    #             background-color: qlineargradient(
    #                 spread:pad, x1:0, y1:0, x2:1, y2:0,
    #                 stop:0 #3498db, stop:0.5 #2980b9, stop:1 #1abc9c
    #             );
    #             border-radius: 12px;
    #         }
    #     """)

    #     layout = QVBoxLayout(dialog)
    #     layout.setContentsMargins(20, 20, 20, 20)
    #     layout.setSpacing(15)

    #     label = QLabel("Instalando Chocolatey...")
    #     label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    #     layout.addWidget(label)

    #     progress = QProgressBar()
    #     progress.setRange(0, 0)
    #     layout.addWidget(progress)

    #     thread = InstallChocoThread()

    #     def on_finished():
    #         label.setText("✅ Chocolatey instalado correctamente.")
    #         progress.setRange(0, 1)
    #         progress.setValue(1)

    #         if hasattr(self, "choco_indicator") and self.is_chocolatey_installed():
    #             self.choco_indicator.setText("✓ Detectado")
    #             self.choco_indicator.setStyleSheet(
    #                 "color: #2ecc71; font-weight: bold; border-radius: 10px; "
    #                 "background-color: rgba(46, 204, 113, 0.1); padding: 5px;"
    #             )

    #     thread.finished.connect(on_finished)
    #     thread.start()
    #     dialog.exec()




# class InstallChocoThread(QThread):
#     finished = pyqtSignal()

#     def run(self):
#         ps_script = (
#             "Set-ExecutionPolicy Bypass -Scope Process -Force; "
#             "[System.Net.ServicePointManager]::SecurityProtocol = "
#             "[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
#             "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))"
#         )

#         # Ruta absoluta a PowerShell para evitar confusiones de PATH
#         pwsh = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
#         args = [
#             pwsh,
#             "-NoProfile",
#             "-ExecutionPolicy", "Bypass",
#             "-Command", ps_script
#         ]

#         # shell=False (por defecto), args como lista
#         subprocess.run(args, check=True)
#         self.finished.emit()


if __name__ == "__main__":
    app = QApplication([])
    window = ChocolateyApp()
    window.show()
    app.exec()