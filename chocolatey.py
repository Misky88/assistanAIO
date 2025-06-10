import subprocess
import json
import re
import os
import ctypes
import time
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QHBoxLayout,
    QLineEdit, QListWidget, QFileDialog, QWidget, QTabWidget, QListWidgetItem,
    QFrame, QSizePolicy, QSpacerItem, QComboBox, QDialog,
    QVBoxLayout, QLabel, QPushButton, QTextEdit, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QGuiApplication
from PyQt6.QtWidgets import QProgressBar

# DEPENDENCIAS NECESARIAS PARA LA OPCION DE INSTALAR CHOCOLATEY AUTOMATICAMENTE
# from PyQt6.QtWidgets import QProgressBar
# from PyQt6.QtCore import QThread, pyqtSignal
# from PyQt6.QtGui import QIcon


class PackageApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Package App Manager")
        self.setGeometry(100, 100, 1210, 800)
        self.setMinimumSize(1210, 700)
        self.setStyleSheet(self.get_styles())
        self.app_dict = {}
        self.group_dict = {}
        self.package_manager = 'winget'
        self.setup_ui()

        self.tabs.currentChanged.connect(self.on_tab_changed)

    def on_tab_changed(self, index):
        if index == 3 and hasattr(self, "filter_input"):
            self.filter_input.clear()
        
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
        QTabBar::tab {
            min-width: 100px;
            min-height: 25px;
            font-size: 15px;
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
        layout.addWidget(self.tabs)


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
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # Header principal con mejor proporción
        header_frame = QFrame()
        header_frame.setFixedHeight(120)  # Altura fija para mejor control
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #2c3e50, stop:0.3 #34495e, stop:0.7 #3498db, stop:1 #5dade2);
                border-radius: 15px;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(40, 20, 40, 20)
        header_layout.setSpacing(25)

        # Sección izquierda - Logo y títulos
        left_section = QHBoxLayout()
        left_section.setSpacing(20)

        # Logo con mejor styling
        logo_label = QLabel("🚀")
        logo_label.setFont(QFont("Segoe UI Emoji", 45))
        logo_label.setStyleSheet("""
            color: white; 
            background: transparent;
            padding: 5px;
            border: 0;
        """)
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_section.addWidget(logo_label)

        # Columna de títulos
        title_column = QVBoxLayout()
        title_column.setSpacing(5)

        title = QLabel("Package App Manager")
        title.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title.setStyleSheet("""
            color: white; 
            background: transparent;
            letter-spacing: 1px;
            border: 0;
        """)
        title_column.addWidget(title)

        subtitle = QLabel("Gestión simplificada de software para Windows")
        subtitle.setFont(QFont("Segoe UI", 14))
        subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9); 
            background: transparent;
            font-weight: 300;
            border: 0;
        """)
        title_column.addWidget(subtitle)

        left_section.addLayout(title_column)
        header_layout.addLayout(left_section)

        # Espaciador flexible
        header_layout.addStretch(1)

        # Sección derecha - Selector de gestor de paquetes
        right_section = QVBoxLayout()
        right_section.setSpacing(8)
        right_section.setAlignment(Qt.AlignmentFlag.AlignTop)

        selector_label = QLabel("GESTOR DE PAQUETES")
        selector_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
        selector_label.setStyleSheet("""
            color: rgba(255, 255, 255, 0.8); 
            background: transparent;
            letter-spacing: 1px;
            border: 0;
        """)
        selector_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_section.addWidget(selector_label)

        self.package_selector = QComboBox()
        self.package_selector.addItems(["WinGet", "Chocolatey"])
        self.package_selector.setCurrentIndex(0)
        self.package_selector.setFixedSize(180, 40)
        self.package_selector.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
                padding: 8px 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 500;
                border: 2px solid rgba(255, 255, 255, 0.3);
            }
            QComboBox:hover {
                background-color: white;
                border: 2px solid rgba(255, 255, 255, 0.6);
                border-radius: 8px;
            }
            QComboBox:focus {
                border: 2px solid #fff;
                outline: none;
                border-radius: 8px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;          
                border-radius: 8px;          
            }
            QComboBox QAbstractItemView {
                background-color: white;
                color: #2c3e50;
                selection-background-color: #e8f4fd;
                selection-color: #2c3e50;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                padding: 5px;
                font-size: 14px;
                outline: none;
            }
            QComboBox QAbstractItemView::item {
                padding: 8px 15px;
                border-radius: 4px;
                margin: 2px;
                border: none;
                outline: none;
            }
            QComboBox QAbstractItemView::item:hover {
                background-color: #e8f4fd;
                border: none;
                outline: none;
                border-radius: 8px;
            }
            QComboBox QAbstractItemView::item:selected {
                background-color: #e8f4fd;
                border: none;
                outline: none;
                border-radius: 8px;
            }
        """)
        self.package_selector.currentIndexChanged.connect(self.on_package_manager_changed)
        right_section.addWidget(self.package_selector)

        header_layout.addLayout(right_section)

        layout.addWidget(header_frame)
        
        cards_main_container = QFrame()
        cards_main_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 0;
            }
        """)
        cards_main_layout = QVBoxLayout(cards_main_container)
        cards_main_layout.setSpacing(20)

        # Primera fila - Sistema y Chocolatey
        top_row_container = QFrame()
        top_row_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 0;
            }
        """)
        top_row_layout = QHBoxLayout(top_row_container)
        top_row_layout.setSpacing(20)

        # Sistema Card
        system_card = QFrame()
        system_card.setFixedHeight(190)
        system_card.setFixedWidth(400)
        system_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        system_layout = QVBoxLayout(system_card)
        system_layout.setContentsMargins(15, 15, 15, 15)
        system_layout.setSpacing(8)

        system_header = QHBoxLayout()
        system_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        system_icon = QLabel("🖥️")
        system_icon.setFont(QFont("Segoe UI Emoji", 16))
        system_title = QLabel("Sistema")
        system_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        system_title.setStyleSheet("color: #2c3e50;")
        system_header.addWidget(system_icon)
        system_header.addWidget(system_title)
        system_layout.addLayout(system_header)
        
        sys_separator = QFrame()
        sys_separator.setFrameShape(QFrame.Shape.HLine)
        sys_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        system_layout.addWidget(sys_separator)

        windows_status = QLabel("Windows 10/11")
        windows_status.setFont(QFont("Segoe UI", 11))
        windows_status.setStyleSheet("color: #34495e; padding: 5px 0;")
        windows_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_layout.addWidget(windows_status)

        self.status_indicator = QLabel("✓ Operativo")
        self.status_indicator.setFont(QFont("Segoe UI", 10))
        self.status_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 8px; background-color: rgba(46, 204, 113, 0.1); padding: 4px 8px;")
        self.status_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        system_layout.addWidget(self.status_indicator)

        top_row_layout.addWidget(system_card)

        # Chocolatey Card
        choco_card = QFrame()
        choco_card.setFixedHeight(190)
        choco_card.setFixedWidth(400)
        choco_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        choco_layout = QVBoxLayout(choco_card)
        choco_layout.setContentsMargins(15, 15, 15, 15)
        choco_layout.setSpacing(8)

        choco_header = QHBoxLayout()
        choco_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        choco_icon = QLabel("🍫")
        choco_icon.setFont(QFont("Segoe UI Emoji", 16))
        choco_title = QLabel("Chocolatey")
        choco_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        choco_title.setStyleSheet("color: #2c3e50;")
        choco_header.addWidget(choco_icon)
        choco_header.addWidget(choco_title)
        choco_layout.addLayout(choco_header)

        choco_separator = QFrame()
        choco_separator.setFrameShape(QFrame.Shape.HLine)
        choco_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        choco_layout.addWidget(choco_separator)

        choco_status = QLabel("Gestor de paquetes")
        choco_status.setFont(QFont("Segoe UI", 11))
        choco_status.setStyleSheet("color: #34495e; padding: 5px 0;")
        choco_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        choco_layout.addWidget(choco_status)

        if self.is_chocolatey_installed():
            choco_indicator = QLabel("✓ Detectado")
            choco_indicator.setFont(QFont("Segoe UI", 10))
            choco_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            choco_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 8px; background-color: rgba(46, 204, 113, 0.1); padding: 4px 8px;")
        else:
            choco_indicator = QLabel("✕ No detectado")
            choco_indicator.setFont(QFont("Segoe UI", 10))
            choco_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
            choco_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 8px; background-color: rgba(231, 76, 60, 0.1); padding: 4px 8px;")

        choco_layout.addWidget(choco_indicator)
        top_row_layout.addWidget(choco_card)

        # Agregar la primera fila al layout principal
        cards_main_layout.addWidget(top_row_container)

        # Segunda fila - WinGet centrado
        bottom_row_container = QFrame()
        bottom_row_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: 0;
            }
        """)
        bottom_row_layout = QHBoxLayout(bottom_row_container)
        bottom_row_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # WinGet Card
        winget_card = QFrame()
        winget_card.setFixedHeight(190)
        winget_card.setFixedWidth(400)  # Ancho fijo para que se vea proporcional
        winget_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: none;
            }
        """)
        winget_layout = QVBoxLayout(winget_card)
        winget_layout.setContentsMargins(15, 15, 15, 15)
        winget_layout.setSpacing(8)

        winget_header = QHBoxLayout()
        winget_header.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        winget_icon = QLabel("📦")
        winget_icon.setFont(QFont("Segoe UI Emoji", 16))
        winget_title = QLabel("WinGet")
        winget_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        winget_title.setStyleSheet("color: #2c3e50;")
        winget_header.addWidget(winget_icon)
        winget_header.addWidget(winget_title)
        winget_layout.addLayout(winget_header)

        win_separator = QFrame()
        win_separator.setFrameShape(QFrame.Shape.HLine)
        win_separator.setStyleSheet("background-color: #ecf0f1; max-height: 1px;")
        winget_layout.addWidget(win_separator)

        winget_status = QLabel("Gestor de paquetes")
        winget_status.setFont(QFont("Segoe UI", 11))
        winget_status.setStyleSheet("color: #34495e; padding: 5px 0;")
        winget_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winget_layout.addWidget(winget_status)

        if self.is_winget_installed():
            winget_indicator = QLabel("✓ Detectado")
            winget_indicator.setFont(QFont("Segoe UI", 10))
            winget_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 8px; background-color: rgba(46, 204, 113, 0.1); padding: 4px 8px;")
        else:
            winget_indicator = QLabel("✕ No detectado")
            winget_indicator.setFont(QFont("Segoe UI", 10))
            winget_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 8px; background-color: rgba(231, 76, 60, 0.1); padding: 4px 8px;")

        winget_indicator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        winget_layout.addWidget(winget_indicator)

        bottom_row_layout.addWidget(winget_card)

        cards_main_layout.addWidget(bottom_row_container)

        layout.addWidget(cards_main_container)

        if hasattr(self, "choco_indicator"):
            if self.is_chocolatey_installed():
                self.choco_indicator.setText("✓ Detectado")
                self.choco_indicator.setStyleSheet("color: #2ecc71; font-weight: bold; border-radius: 8px; background-color: rgba(46, 204, 113, 0.1); padding: 4px 8px;")
            else:
                self.choco_indicator.setText("✕ No detectado")
                self.choco_indicator.setStyleSheet("color: #e74c3c; font-weight: bold; border-radius: 8px; background-color: rgba(231, 76, 60, 0.1); padding: 4px 8px;")

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
        buttons_layout.addWidget(self.create_button("Instalar Agrupación", self.install_group))
        self.add_spacer(buttons_layout)
        layout.addLayout(buttons_layout)

        return tab


    def create_manage_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        self.updates_only_checkbox = QCheckBox("Mostrar solo programas con actualización")
        self.updates_only_checkbox.stateChanged.connect(self.toggle_updates_view)
        top_row_layout = QHBoxLayout()
        self.manage_title_label = self.create_title_label("Aplicaciones Instaladas")
        top_row_layout.addWidget(self.manage_title_label)

        top_row_layout.addStretch()  # empuja el checkbox a la derecha

        self.updates_only_checkbox = QCheckBox("Mostrar solo programas con actualización")
        self.updates_only_checkbox.stateChanged.connect(self.toggle_updates_view)
        top_row_layout.addWidget(self.updates_only_checkbox)

        layout.addLayout(top_row_layout)
        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText("Buscar aplicación instalada...")
        self.filter_input.textChanged.connect(self.filter_installed_apps)
        layout.addWidget(self.filter_input)

        self.installed_apps = QListWidget()
        layout.addWidget(self.installed_apps)

        buttons_layout = QHBoxLayout()
        self.update_button = self.create_button("Actualizar", self.update_selected_apps)
        self.uninstall_button = self.create_button("Desinstalar", self.uninstall_selected_apps)
        buttons_layout.addWidget(self.update_button)
        buttons_layout.addWidget(self.uninstall_button)
        self.update_button.setVisible(False)
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
    
    # ******************* FUNCIONES PARA MOSTRAR BOTONES Y MOSTRAR LISTA DE ACTUALIZABLES ***********************
    def toggle_updates_view(self, state):
        if state == Qt.CheckState.Checked.value:
            self.manage_title_label.setText("Aplicaciones con actualización")
            self.update_button.setVisible(True)
            self.uninstall_button.setVisible(False)
            if self.package_manager == "winget":
                self.load_upgradable_apps()
            elif self.package_manager == "choco":
                self.load_upgradable_apps_choco()
            else:
                self.log_text.append("Este gestor no soporta la vista de actualizaciones.")
                self.updates_only_checkbox.setCheckState(Qt.CheckState.Unchecked)
        else:
            self.manage_title_label.setText("Aplicaciones Instaladas")
            self.update_button.setVisible(False)
            self.uninstall_button.setVisible(True)
            self.load_installed_apps()

    def load_upgradable_apps(self):
        self.installed_apps.clear()
        self.all_installed = []
        self.installed_apps_dict = {}

        try:
            result = subprocess.run(
                ["winget", "upgrade", "--source", "winget"],
                capture_output=True,
                text=True,
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
                    if app_name.lower() == "nombre" or app_id.lower() == "id":
                        continue
                    self.all_installed.append(app_name)
                    self.installed_apps.addItem(app_name)
                    self.installed_apps_dict[app_name] = app_id


            if not self.all_installed:
                mensaje = QListWidgetItem("No hay paquetes actualizables con WinGet.")
                mensaje.setFlags(Qt.ItemFlag.NoItemFlags)
                self.installed_apps.addItem(mensaje)
        except Exception as e:
            self.log_text.append(f"Error al cargar aplicaciones con actualización: {e}")

    def load_upgradable_apps_choco(self):
        self.installed_apps.clear()
        self.all_installed = []
        self.installed_apps_dict = {}

        try:
            result = subprocess.run(
                ["choco", "outdated"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                shell=True
            )
            output = result.stdout
            lines = output.splitlines()
            encontrados = 0

            for line in lines:
                if not line.strip() or line.startswith("Outdated Packages") or line.startswith(" Output") or "|" not in line:
                    continue

                parts = line.split("|")
                if len(parts) >= 3:
                    app_name = parts[0].strip()
                    current_version = parts[1].strip()
                    new_version = parts[2].strip()

                    self.all_installed.append(app_name)
                    self.installed_apps.addItem(app_name)
                    self.installed_apps_dict[app_name] = app_name
                    encontrados += 1

            if encontrados == 0:
                mensaje = QListWidgetItem("No hay paquetes actualizables con Chocolatey.")
                mensaje.setFlags(Qt.ItemFlag.NoItemFlags)
                self.installed_apps.addItem(mensaje)

        except Exception as e:
            self.log_text.append(f"Error al listar paquetes actualizables en Chocolatey: {e}")
    
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
                ["winget", "list", "--source", "winget"],
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
    # def install_selected_app(self):
    #     if self.package_manager == "winget":
    #         self.install_selected_app_winget()
    #     else:
    #         self.install_selected_app_choco()

    def install_selected_app(self):
        selected_item = self.search_results.currentItem()
        if not selected_item:
            self.log_text.append("Por favor, selecciona una aplicación para instalar.")
            return

        app_name = selected_item.text()
        app_id = self.app_dict.get(app_name)

        if not app_id:
            self.log_text.append(f"No se encontró el ID para la app: {app_name}")
            return
        
        if app_name.lower() in [a.lower() for a in self.all_installed]:
            respuesta = QMessageBox.question(
                self,
                "Aplicación ya instalada",
                f"La aplicación '{app_name}' ya está instalada.\n¿Deseas actualizar o desinstalar el paquete?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if respuesta == QMessageBox.StandardButton.Yes:
                self.tabs.setCurrentIndex(3)
                self.filter_input.setText(app_name)
            return

        self.log_text.append(f"Iniciando instalación de '{app_name}'...")

        thread = InstallSingleThread(app_name, app_id, self.package_manager)
        thread.finalizado.connect(self.load_installed_apps)
        dialog = ProgressDialog("Instalando aplicación", thread, self, mensaje_header="¡Instalacion completada!", mensaje_final=f"'{app_name}' se ha instalado correctamente.")
        dialog.exec()


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
        
        self.log_text.append(f"Instalando '{app_id}' usando Winget...")
        try:
            subprocess.run(["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
            self.log_text.append(f"{app_id} instalado correctamente.")
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al instalar {app_id}: {e}")


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


    # def update_all_apps(self):
    #     """Actualiza todas las aplicaciones instaladas"""
    #     self.log_text.append("Buscando actualizaciones para todas las aplicaciones...")
    #     try:
    #         result = subprocess.run(["winget", "upgrade", "--all", "-e", "--accept-package-agreements", "--accept-source-agreements"], capture_output=True, text=True, check=True)
    #         self.log_text.append(result.stdout)
    #     except subprocess.CalledProcessError as e:
    #         self.log_text.append(f"Error al actualizar aplicaciones: {e}")

    def update_all_apps(self):
        self.log_text.append("Iniciando actualización de todas las aplicaciones...")

        thread = UpdateAllThread(self.package_manager)
        thread.finalizado.connect(self.load_installed_apps)
        dialog = ProgressDialog("Actualizando todos los paquetes...", thread, self, mensaje_header="¡Actualizacion completada!", mensaje_final=f"Paquetes actualizados correctamente.", permitir_cancelar=True)
        dialog.exec()


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
        if app_name in self.group_dict:
            del self.group_dict[app_name]
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
                data_to_export = {
                    "package": self.package_manager,
                    "apps": self.group_dict
                }

                with open(file_path, "w", encoding="utf-8") as file:
                    json.dump(data_to_export, file, indent=4)

                self.log_text.append(f"Agrupación exportada a {file_path}.")
                self.show_toast("Agrupación exportada con éxito")
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

                if "apps" in imported and "package" in imported:
                    if imported["package"] != self.package_manager:
                        QMessageBox.warning(
                            self,
                            "Gestor de Paquetes Incompatible",
                            f"La agrupación fue creada usando '{imported['package']}', pero actualmente tienes seleccionado '{self.package_manager}'.\n\nCambia el gestor para poder instalar esta agrupación."
                        )
                        return

                    self.group_list.clear()
                    self.group_dict.clear()

                    for name, app_id in imported["apps"].items():
                        self.group_list.addItem(name)
                        self.group_dict[name] = app_id

                    self.log_text.append(f"Agrupación importada desde {file_path}.")
                    self.show_toast("Agrupacion importada con éxito")
                else:
                    self.log_text.append("El archivo JSON no tiene el formato esperado.")

            except Exception as e:
                self.log_text.append(f"Error al importar agrupación: {e}")

    def install_group(self):
        """Lanza un hilo para instalar la agrupación sin bloquear la interfaz"""
        if not self.group_dict:
            self.log_text.append("No hay paquetes en la agrupación para instalar.")
            return

        self.log_text.append(f"Iniciando instalación de agrupación con {self.package_manager.capitalize()}...")

        thread = InstallGroupThread(self.group_dict, self.package_manager)
        thread.finalizado.connect(self.load_installed_apps)
        dialog = ProgressDialog(
            titulo="Instalando agrupación",
            thread=thread,
            parent=self,
            total=len(self.group_dict),
            mensaje_header="¡Instalación completada!",
            mensaje_final="La instalación de los paquetes ha finalizado.",
            permitir_cancelar=True
        )
        dialog.exec()

    def install_group_winget(self):
        """Instala todos los paquetes de la agrupación usando WinGet"""
        self.log_text.append("Instalando la agrupacion...")

        for app_name, app_id in self.group_dict.items():
            print("Llega aqui")
            self.log_text.append(f"Instalando '{app_name}' (ID: {app_id})...")
            try:
                subprocess.run(
                    ["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"],
                    check=True
                )
                self.log_text.append(f"'{app_name}' instalado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al instalar '{app_name}': {e}")

    def install_group_choco(self):
        """Instala todos los paquetes de la agrupación usando Chocolatey"""
        self.log_text.append("Instalando la agrupacion...")

        for app_name, app_id in self.group_dict.items():
            self.log_text.append(f"Instalando '{app_name}' (ID: {app_id})...")
            try:
                # subprocess.run(["choco", "install", app_id, "-y"], check=True, shell=True)
                self.log_text.append(f"'{app_name}' instalado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al instalar '{app_name}': {e}")
        
    #******************** ACTUALIZAR LOS PAQUETES *************************
    # def update_selected_apps(self):
    #     if self.package_manager == "winget":
    #         self.update_selected_apps_winget()
    #     else:
    #         self.update_selected_apps_choco()

    def update_selected_apps(self):
        selected_items = self.installed_apps.selectedItems()
        if not selected_items:
            self.log_text.append("Por favor, selecciona una o más aplicaciones para actualizar.")
            return

        for item in selected_items:
            app_name = item.text()

            if self.package_manager == "winget":
                app_id = self.installed_apps_dict.get(app_name)
                if not app_id:
                    self.log_text.append(f"No se encontró el ID para la app: {app_name}")
                    continue
            else:
                app_id = app_name

            thread = UpdateSingleThread(app_name, app_id, self.package_manager)
            thread.finalizado.connect(self.load_installed_apps)
            dialog = ProgressDialog("Actualizando aplicación", thread, self, mensaje_header='¡Actualización completada!', mensaje_final=f"'{app_name}' se ha actualizado correctamente.")
            dialog.exec()
            self.updates_only_checkbox.setChecked(False)
            self.filter_input.clear()


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
    # def uninstall_selected_apps(self):
    #     if self.package_manager == "winget":
    #         self.uninstall_selected_apps_winget()
    #     else:
    #         self.uninstall_selected_apps_choco()

    def uninstall_selected_apps(self):
        selected_items = self.installed_apps.selectedItems()
        if not selected_items:
            self.log_text.append("Por favor, selecciona una o más aplicaciones para desinstalar.")
            return

        for item in selected_items:
            app_name = item.text()

            if self.package_manager == "winget":
                app_id = self.installed_apps_dict.get(app_name)
                if not app_id:
                    self.log_text.append(f"No se encontró el ID para la app: {app_name}")
                    continue
            else:
                app_id = app_name

            thread = UninstallSingleThread(app_name, app_id, self.package_manager)
            thread.finalizado.connect(self.load_installed_apps)
            dialog = ProgressDialog("Desinstalando aplicación", thread, self, mensaje_header='¡Desinstalación completada!', mensaje_final=f"'{app_name}' se ha desinstalado correctamente.")
            dialog.exec()
            self.filter_input.clear()


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
        self.updates_only_checkbox.setChecked(False)
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


class ProgressDialog(QDialog):
    def __init__(self, titulo, thread, parent=None, total=None, mensaje_header="Accion completada", mensaje_final="La acción se ha completado correctamente.", permitir_cancelar=False):
        super().__init__(parent)
        self.setWindowTitle("Procesando...")
        self.setFixedSize(480, 220)
        self.setModal(True)
        self.thread = thread
        self.mensaje_final = mensaje_final
        self.mensaje_header = mensaje_header
        self.total = total
        self.pasos = 0

        self.setStyleSheet("""
            QDialog {
                background-color: #f5f7f9;
                border: none;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: #2980b9;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                padding: 15px;
            }
            QLabel#mensajeLabel {
                font-size: 14px;
                padding: 10px 20px;
                color: #2c3e50;
            }
            QProgressBar {
                height: 20px;
                margin: 10px 20px;
                border-radius: 10px;
                background-color: #ecf0f1;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 10px;
            }
            QPushButton {
                padding: 8px 16px;
                margin: 0 20px;
                border-radius: 6px;
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)

        layout = QVBoxLayout(self)

        title = QLabel(f"⚙️ {titulo}")
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        self.mensaje_label = QLabel("Iniciando...")
        self.mensaje_label.setObjectName("mensajeLabel")
        self.mensaje_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.mensaje_label)


        self.progress_bar = QProgressBar()
        if total:
            self.progress_bar.setRange(0, total)
        else:
            self.progress_bar.setRange(0, 0)
        layout.addWidget(self.progress_bar)

        if permitir_cancelar:
            self.cancel_button = QPushButton("Cancelar")
            self.cancel_button.clicked.connect(self.cancelar_instalacion)
            layout.addWidget(self.cancel_button)

        self.thread.progreso.connect(self.actualizar_mensaje)
        self.thread.finalizado.connect(self.finalizar_y_notificar)
        self.thread.cancelado.connect(self.actualizar_mensaje)

        print("🟢 Layout listo, arrancando hilo...")
        QTimer.singleShot(500, self.thread.start)

    def actualizar_mensaje(self, texto):
        self.mensaje_label.setText(texto)
        self.mensaje_label.repaint()
        if self.total:
            self.pasos += 1
            self.progress_bar.setValue(self.pasos)

    def cancelar_instalacion(self):
        self.thread.cancelar()
        if hasattr(self, 'cancel_button'):
            self.cancel_button.setEnabled(False)
        self.mensaje_label.setText("Cancelando...")

    def finalizar_y_notificar(self):
        self.accept()
        SuccessDialog(self.mensaje_header, self.mensaje_final, parent=self.parent()).exec()


class SuccessDialog(QDialog):
    def __init__(self, mensaje_header, mensaje, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Éxito")
        self.setFixedSize(480, 220)
        self.setModal(True)

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
                border-radius: 12px;
            }
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                background-color: #2ecc71;
                padding: 15px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
            }
            QLabel#mensajeLabel {
                font-size: 14px;
                padding: 25px 30px;
                color: #2c3e50;
                background-color: #f2f6f8;
                border-bottom-left-radius: 10px;
                border-bottom-right-radius: 10px;
            }
            QPushButton {
                padding: 10px 24px;
                margin-top: 16px;
                border-radius: 8px;
                background-color: #2ecc71;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        title = QLabel(mensaje_header)
        title.setObjectName("titleLabel")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        body = QLabel(mensaje)
        body.setObjectName("mensajeLabel")
        body.setWordWrap(True)
        body.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(body)

        ok_button = QPushButton("Cerrar")
        ok_button.clicked.connect(self.accept)
        ok_button.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(ok_button, alignment=Qt.AlignmentFlag.AlignCenter)


class InstallGroupThread(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal()
    cancelado = pyqtSignal(str)


    def __init__(self, group_dict, package_manager):
        super().__init__()
        self.group_dict = group_dict
        self.package_manager = package_manager
        self._cancelar = False

    def run(self):
        total = len(self.group_dict)
        actual = 1
        for app_name, app_id in self.group_dict.items():
            if self._cancelar:
                self.cancelado.emit("Instalación cancelada. No se instalarán más paquetes.")
                break

            self.progreso.emit(f"[{actual}/{total}] Instalando '{app_name}'...")

            try:
                if self.package_manager == "winget":
                    cmd = ["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"]
                    subprocess.run(cmd, check=True)
                else:
                    cmd = ["choco", "install", app_id, "-y"]
                    subprocess.run(cmd, check=True, shell=True)

                self.progreso.emit(f"'{app_name}' instalado correctamente.")
                time.sleep(0.5)
            except subprocess.CalledProcessError as e:
                self.progreso.emit(f"Error al instalar '{app_name}': {e}")

            actual += 1

        self.finalizado.emit()

    def cancelar(self):
        self._cancelar = True

class InstallSingleThread(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal()
    cancelado = pyqtSignal(str)

    def __init__(self, app_name, app_id, gestor):
        super().__init__()
        self.app_name = app_name
        self.app_id = app_id
        self.gestor = gestor
        self._cancelar = False

    def run(self):
        if self._cancelar:
            self.cancelado.emit(f"Instalación cancelada antes de empezar.")
            return

        self.progreso.emit(f"Instalando '{self.app_name}'...")

        try:
            if self.gestor == "winget":
                cmd = ["winget", "install", "--id", self.app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"]
                subprocess.run(cmd, check=True)
            else:
                cmd = ["choco", "install", self.app_id, "-y"]
                subprocess.run(cmd, check=True, shell=True)

            if self._cancelar:
                self.cancelado.emit(f"Instalación de '{self.app_name}' cancelada.")
                return

            self.progreso.emit(f"'{self.app_name}' instalado correctamente.")
        except subprocess.CalledProcessError as e:
            self.progreso.emit(f"Error al instalar '{self.app_name}': {e}")
        self.finalizado.emit()

    def cancelar(self):
        self._cancelar = True


class UninstallSingleThread(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal()
    cancelado = pyqtSignal(str)

    def __init__(self, app_name, app_id, gestor):
        super().__init__()
        self.app_name = app_name
        self.app_id = app_id
        self.gestor = gestor
        self._cancelar = False

    def run(self):
        if self._cancelar:
            self.cancelado.emit("Desinstalación cancelada antes de comenzar.")
            return

        self.progreso.emit(f"Desinstalando '{self.app_name}'...")

        try:
            if self.gestor == "winget":
                cmd = ["winget", "uninstall", "--id", self.app_id, "-e"]
                subprocess.run(cmd, check=True)
            else:
                cmd = [
                    "choco", "uninstall", self.app_id,
                    "-y", "--accept-license", "--remove-dependencies", "--no-progress"
                ]
                subprocess.run(cmd, check=True, shell=True)

            if self._cancelar:
                self.cancelado.emit(f"Desinstalación de '{self.app_name}' cancelada.")
                return

            self.progreso.emit(f"'{self.app_name}' desinstalado correctamente.")
        except subprocess.CalledProcessError as e:
            self.progreso.emit(f"Error al desinstalar '{self.app_name}': {e}")
        self.finalizado.emit()

    def cancelar(self):
        self._cancelar = True

class UpdateSingleThread(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal()
    cancelado = pyqtSignal(str)

    def __init__(self, app_name, app_id, gestor):
        super().__init__()
        self.app_name = app_name
        self.app_id = app_id
        self.gestor = gestor
        self._cancelar = False

    def run(self):
        if self._cancelar:
            self.cancelado.emit("Actualización cancelada antes de comenzar.")
            return

        self.progreso.emit(f"Actualizando '{self.app_name}'...")

        try:
            if self.gestor == "winget":
                cmd = ["winget", "upgrade", "--id", self.app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"]
                subprocess.run(cmd, check=True)
            else:
                cmd = ["choco", "upgrade", self.app_id, "-y", "--accept-license", "--no-progress"]
                subprocess.run(cmd, check=True, shell=True)

            if self._cancelar:
                self.cancelado.emit(f"Actualización de '{self.app_name}' cancelada.")
                return

            self.progreso.emit(f"'{self.app_name}' actualizado correctamente.")
        except subprocess.CalledProcessError as e:
            self.progreso.emit(f"Error al actualizar '{self.app_name}': {e}")
        self.finalizado.emit()

    def cancelar(self):
        self._cancelar = True

class UpdateAllThread(QThread):
    progreso = pyqtSignal(str)
    finalizado = pyqtSignal()
    cancelado = pyqtSignal(str)

    def __init__(self, gestor):
        super().__init__()
        self.gestor = gestor
        self._cancelar = False

    def run(self):
        if self._cancelar:
            self.cancelado.emit("Actualización cancelada antes de comenzar.")
            return

        self.progreso.emit("Buscando actualizaciones...")

        try:
            if self.gestor == "winget":
                cmd = ["winget", "upgrade", "--all", "-e", "--accept-package-agreements", "--accept-source-agreements"]
                subprocess.run(cmd, check=True)
            else:
                cmd = ["choco", "upgrade", "all", "-y", "--accept-license", "--no-progress"]
                subprocess.run(cmd, check=True, shell=True)

            if self._cancelar:
                self.cancelado.emit("Actualización cancelada por el usuario.")
                return

            self.progreso.emit("Todas las aplicaciones actualizadas correctamente.")
        except subprocess.CalledProcessError as e:
            self.progreso.emit(f"Error al actualizar: {e}")
        self.finalizado.emit()

    def cancelar(self):
        self._cancelar = True



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
        app = QApplication([])
        window = PackageApp()
        window.show()
        app.exec()


# choco install slack --version=4.43.49