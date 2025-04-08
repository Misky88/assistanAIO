import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QTextEdit, QFileDialog, QWidget, QTabWidget
)


class WinGetApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Aplicaciones - WinGet")
        self.setGeometry(100, 100, 800, 600)
        self.setup_ui()

    def setup_ui(self):
        # Configurar pestañas principales
        self.tabs = QTabWidget()
        self.tabs.addTab(self.create_home_tab(), "Inicio")
        self.tabs.addTab(self.create_search_tab(), "Buscar e Instalar")
        self.tabs.addTab(self.create_group_tab(), "Agrupaciones")
        self.tabs.addTab(self.create_manage_tab(), "Actualizar/Desinstalar")
        self.tabs.addTab(self.create_log_tab(), "Historial")
        self.setCentralWidget(self.tabs)

    def create_home_tab(self):
        """Crea la pestaña de inicio"""
        tab = QWidget()
        layout = QVBoxLayout()

        welcome_label = QLabel("Bienvenido al Gestor de Aplicaciones - WinGet")
        welcome_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(welcome_label)

        system_info = QLabel("Versión de Windows: 10/11\nEstado de WinGet: Disponible")
        system_info.setStyleSheet("font-size: 14px; color: #34495e;")
        layout.addWidget(system_info)

        quick_actions_label = QLabel("Acciones Rápidas:")
        quick_actions_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-top: 10px;")
        layout.addWidget(quick_actions_label)

        quick_actions_layout = QHBoxLayout()
        search_button = QPushButton("Buscar Aplicaciones")
        search_button.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        quick_actions_layout.addWidget(search_button)

        update_all_button = QPushButton("Actualizar Todo")
        update_all_button.clicked.connect(self.update_all_apps)
        quick_actions_layout.addWidget(update_all_button)

        layout.addLayout(quick_actions_layout)
        tab.setLayout(layout)
        return tab

    def create_search_tab(self):
        """Crea la pestaña de búsqueda e instalación"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Buscar aplicaciones con WinGet...")
        self.search_bar.returnPressed.connect(self.search_apps)
        layout.addWidget(self.search_bar)

        self.search_results = QListWidget()
        layout.addWidget(self.search_results)

        install_button = QPushButton("Instalar Aplicación Seleccionada")
        install_button.clicked.connect(self.install_selected_app)
        layout.addWidget(install_button)

        tab.setLayout(layout)
        return tab

    def create_group_tab(self):
        """Crea la pestaña de agrupaciones"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.group_list = QListWidget()
        layout.addWidget(self.group_list)

        button_layout = QHBoxLayout()
        add_button = QPushButton("Añadir a Agrupación")
        add_button.clicked.connect(self.add_to_group)
        button_layout.addWidget(add_button)

        export_button = QPushButton("Exportar Agrupación")
        export_button.clicked.connect(self.export_group)
        button_layout.addWidget(export_button)

        import_button = QPushButton("Importar Agrupación")
        import_button.clicked.connect(self.import_group)
        button_layout.addWidget(import_button)

        layout.addLayout(button_layout)
        tab.setLayout(layout)
        return tab

    def create_manage_tab(self):
        """Crea la pestaña de actualización y desinstalación"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.installed_apps = QListWidget()
        layout.addWidget(self.installed_apps)

        button_layout = QHBoxLayout()
        update_button = QPushButton("Actualizar Seleccionadas")
        update_button.clicked.connect(self.update_selected_apps)
        button_layout.addWidget(update_button)

        uninstall_button = QPushButton("Desinstalar Seleccionadas")
        uninstall_button.clicked.connect(self.uninstall_selected_apps)
        button_layout.addWidget(uninstall_button)

        layout.addLayout(button_layout)
        tab.setLayout(layout)
        return tab

    def create_log_tab(self):
        """Crea la pestaña de historial"""
        tab = QWidget()
        layout = QVBoxLayout()

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        tab.setLayout(layout)
        return tab

    def search_apps(self):
        """Busca aplicaciones con WinGet"""
        query = self.search_bar.text()
        if not query:
            self.log_text.append("Por favor, introduce un término de búsqueda.")
            return

        self.log_text.append(f"Buscando aplicaciones para '{query}'...")
        self.search_results.clear()

        try:
            result = subprocess.run(["winget", "search", query], capture_output=True, text=True, check=True)
            for line in result.stdout.splitlines()[2:]:
                if line.strip():
                    self.search_results.addItem(line.split()[0])  # Añadir el ID de la aplicación
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al buscar aplicaciones: {e}")

    def install_selected_app(self):
        """Instala la aplicación seleccionada de los resultados de búsqueda"""
        selected_item = self.search_results.currentItem()
        if not selected_item:
            self.log_text.append("Por favor, selecciona una aplicación para instalar.")
            return

        app_id = selected_item.text()
        self.log_text.append(f"Instalando {app_id}...")
        try:
            subprocess.run(["winget", "install", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
            self.log_text.append(f"{app_id} instalado correctamente.")
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al instalar {app_id}: {e}")

    def update_all_apps(self):
        """Actualiza todas las aplicaciones instaladas"""
        self.log_text.append("Buscando actualizaciones para todas las aplicaciones...")
        try:
            result = subprocess.run(["winget", "upgrade", "--all", "-e", "--accept-package-agreements", "--accept-source-agreements"], capture_output=True, text=True, check=True)
            self.log_text.append(result.stdout)
        except subprocess.CalledProcessError as e:
            self.log_text.append(f"Error al actualizar aplicaciones: {e}")

    def add_to_group(self):
        """Añade una aplicación a la agrupación"""
        selected_item = self.search_results.currentItem()
        if not selected_item:
            self.log_text.append("Por favor, selecciona una aplicación para añadir a la agrupación.")
            return

        app_id = selected_item.text()
        self.group_list.addItem(app_id)
        self.log_text.append(f"{app_id} añadido a la agrupación.")

    def export_group(self):
        """Exporta la agrupación a un archivo JSON"""
        group = [self.group_list.item(i).text() for i in range(self.group_list.count())]
        if not group:
            self.log_text.append("No hay aplicaciones en la agrupación para exportar.")
            return

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, "Exportar Agrupación", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "w") as file:
                json.dump(group, file)
            self.log_text.append(f"Agrupación exportada a {file_path}.")

    def import_group(self):
        """Importa una agrupación desde un archivo JSON"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Importar Agrupación", "", "JSON Files (*.json)")
        if file_path:
            with open(file_path, "r") as file:
                group = json.load(file)
            self.group_list.clear()
            for app_id in group:
                self.group_list.addItem(app_id)
            self.log_text.append(f"Agrupación importada desde {file_path}.")

    def update_selected_apps(self):
        """Actualiza las aplicaciones seleccionadas"""
        selected_items = [self.installed_apps.item(i).text() for i in range(self.installed_apps.count()) if self.installed_apps.item(i).isSelected()]
        if not selected_items:
            self.log_text.append("Por favor, selecciona al menos una aplicación para actualizar.")
            return

        for app_id in selected_items:
            self.log_text.append(f"Actualizando {app_id}...")
            try:
                subprocess.run(["winget", "upgrade", "--id", app_id, "-e", "--accept-package-agreements", "--accept-source-agreements"], check=True)
                self.log_text.append(f"{app_id} actualizado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al actualizar {app_id}: {e}")

    def uninstall_selected_apps(self):
        """Desinstala las aplicaciones seleccionadas"""
        selected_items = [self.installed_apps.item(i).text() for i in range(self.installed_apps.count()) if self.installed_apps.item(i).isSelected()]
        if not selected_items:
            self.log_text.append("Por favor, selecciona al menos una aplicación para desinstalar.")
            return

        for app_id in selected_items:
            self.log_text.append(f"Desinstalando {app_id}...")
            try:
                subprocess.run(["winget", "uninstall", "--id", app_id, "-e"], check=True)
                self.log_text.append(f"{app_id} desinstalado correctamente.")
            except subprocess.CalledProcessError as e:
                self.log_text.append(f"Error al desinstalar {app_id}: {e}")

class ChocolateyUI(QWidget):
    def __init__(self):
        super().__init__()
        # Configuración de la interfaz

if __name__ == "__main__":
    app = QApplication([])
    window = WinGetApp()
    window.show()
    app.exec()