# Backup7z/main.py
import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QCheckBox, QComboBox, QLineEdit, QMessageBox, QListWidget,
    QProgressBar, QTabWidget, QHBoxLayout
)
from PyQt6.QtGui import QIcon
from scheduler import schedule_backup
from backup_thread import BackupThread


# Configurar logging
logging.basicConfig(
    filename='backup.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class BackupApp(QWidget):
    def __init__(self):
        super().__init__()
        self.files = []
        self.setup_ui()
        self.setup_styles()
        self.thread = None

    def setup_ui(self):
        self.setWindowTitle("🛡 Backup Tool Pro")
        self.setWindowIcon(QIcon('icon.png'))
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # New "Nombre de la Copia" tab
        name_tab = QWidget()
        name_layout = QVBoxLayout()

        # Campo para el nombre del archivo comprimido
        self.outputNameField = QLineEdit()
        self.outputNameField.setPlaceholderText("Nombre del archivo comprimido (sin extensión)")
        self.outputNameField.textChanged.connect(self.update_preview)
        name_layout.addWidget(QLabel("Nombre de la Copia:"))
        name_layout.addWidget(self.outputNameField)

        # Vista previa del nombre completo del archivo
        self.previewLabel = QLabel("Vista previa: backup.7z")
        name_layout.addWidget(self.previewLabel)

        # Campo para la descripción del backup
        self.descriptionField = QLineEdit()
        self.descriptionField.setPlaceholderText("Descripción del backup (opcional)")
        name_layout.addWidget(QLabel("Descripción:"))
        name_layout.addWidget(self.descriptionField)

        # Botón para restablecer valores
        btn_reset = QPushButton("🔄 Restablecer")
        btn_reset.clicked.connect(self.reset_name_tab)
        name_layout.addWidget(btn_reset)

        name_tab.setLayout(name_layout)
        tab_widget.addTab(name_tab, "Nombre de la Copia")

        # File selection tab
        file_tab = QWidget()
        file_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(100)
        file_layout.addWidget(self.file_list)
        
        # Layout horizontal para los botones
        button_layout = QHBoxLayout()

        # Botón para agregar archivos
        btn_add_files = QPushButton("➕ Agregar archivos")
        btn_add_files.clicked.connect(self.select_files)
        button_layout.addWidget(btn_add_files)

        # Botón para agregar carpetas
        btn_add_folders = QPushButton("📂 Agregar carpetas")
        btn_add_folders.clicked.connect(self.select_folders)
        button_layout.addWidget(btn_add_folders)

        # Botón para eliminar elementos seleccionados
        btn_remove_selected = QPushButton("❌ Eliminar seleccionado")
        btn_remove_selected.clicked.connect(self.remove_selected_item)
        button_layout.addWidget(btn_remove_selected)

        # Añadir el layout horizontal al layout principal
        file_layout.addLayout(button_layout)

        file_tab.setLayout(file_layout)
        tab_widget.addTab(file_tab, "Archivos a respaldar")

        # Encryption tab
        encrypt_tab = QWidget()
        encrypt_layout = QVBoxLayout()
        self.encryptCheckBox = QCheckBox("🔑 Encriptar archivo")
        self.passwordField = QLineEdit()
        self.passwordField.setPlaceholderText("Contraseña (mínimo 8 caracteres)")
        encrypt_layout.addWidget(self.encryptCheckBox)
        encrypt_layout.addWidget(self.passwordField)
        encrypt_tab.setLayout(encrypt_layout)
        tab_widget.addTab(encrypt_tab, "Configuración de seguridad")

        # Scheduling tab
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout()
        self.scheduleCombo = QComboBox()
        self.scheduleCombo.addItems([
            "Diario (2:00 AM)",
            "Semanal (Lunes 2:00 AM)",
            "Mensual (Día 1 2:00 AM)"
        ])
        schedule_layout.addWidget(self.scheduleCombo)
        schedule_tab.setLayout(schedule_layout)
        tab_widget.addTab(schedule_tab, "Programación")

        # Progress
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Actions
        self.backupButton = QPushButton("🚀 Iniciar backup ahora")
        self.backupButton.clicked.connect(self.start_backup)
        layout.addWidget(self.backupButton)

        self.setLayout(layout)

    def setup_styles(self):
        self.setStyleSheet("""
            QWidget {
                background: #2d2d2d;
                color: #e0e0e0;
                font-family: 'Segoe UI', Arial;
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #3d3d3d;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                color: #88c0d0;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QPushButton {
                background: #5e81ac;
                color: #ffffff;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: #81a1c1;
            }
            QLineEdit {
                background: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                padding: 8px;
                color: #e0e0e0;
            }
            QListWidget {
                background: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                color: #e0e0e0;
            }
            QProgressBar {
                background: #3d3d3d;
                border: 1px solid #4d4d4d;
                border-radius: 4px;
                text-align: center;
                color: #e0e0e0;
            }
            QProgressBar::chunk {
                background: #0078d7;
                width: 10px;
                border-radius: 3px;
            }
            QCheckBox {
                spacing: 8px;
                color: #000000;
            }
        """)

    def select_files(self):
        """Permite al usuario seleccionar archivos para la copia de seguridad."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar Archivos", "", "Todos los archivos (*)"
        )
        if files:
            self.files.extend(files)
            self.update_file_list()

    def select_folders(self):
        """Permite al usuario seleccionar carpetas para la copia de seguridad."""
        folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta")
        if folder:
            self.files.append(folder)
            self.update_file_list()

    def update_file_list(self):
        """Actualiza la lista de archivos y carpetas seleccionados en la interfaz."""
        self.file_list.clear()
        self.file_list.addItems([os.path.basename(f) for f in self.files])

    def start_backup(self):
        if not self.files:
            QMessageBox.warning(self, "Error", "Debe seleccionar archivos para respaldar.")
            return

        password = self.passwordField.text() if self.encryptCheckBox.isChecked() else None
        if password and len(password) < 8:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 8 caracteres.")
            return

        # Obtener el nombre del archivo comprimido
        output_name = self.outputNameField.text().strip()
        if not output_name:
            QMessageBox.warning(self, "Error", "Debe especificar un nombre para el archivo comprimido.")
            return

        frequency = self.scheduleCombo.currentText().split(" ")[0]
        
        self.progress.setVisible(True)
        self.backupButton.setEnabled(False)

        self.thread = BackupThread(self.files, password, output_name)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.backup_finished)
        self.thread.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def backup_finished(self, success, message):
        self.progress.setVisible(False)
        self.backupButton.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
            frequency = self.scheduleCombo.currentText().split(" ")[0]
            schedule_backup(frequency, self.files, self.passwordField.text() or None)
        else:
            QMessageBox.critical(self, "Error", message)

    def update_preview(self):
        """Actualiza la vista previa del nombre completo del archivo comprimido."""
        name = self.outputNameField.text().strip()
        if not name:
            name = "backup"
        self.previewLabel.setText(f"Vista previa: {name}.7z")

    def reset_name_tab(self):
        """Restablece los valores de los campos en la pestaña 'Nombre de la Copia'."""
        self.outputNameField.clear()
        self.descriptionField.clear()
        self.update_preview()

    def remove_selected_item(self):
        """Elimina el elemento seleccionado de la lista de archivos y carpetas."""
        selected_item = self.file_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            # Buscar y eliminar el elemento de la lista interna `self.files`
            for file in self.files:
                if os.path.basename(file) == item_text:
                    self.files.remove(file)
                    break
            # Actualizar la lista visible
            self.update_file_list()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec())