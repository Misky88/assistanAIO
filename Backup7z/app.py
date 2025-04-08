# Backup7z/main.py
import sys
import os
import logging
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QCheckBox, QComboBox, QLineEdit, QMessageBox, QGroupBox, QListWidget,
    QProgressBar, QTabWidget
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
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

        # File selection tab
        file_tab = QWidget()
        file_layout = QVBoxLayout()
        self.file_list = QListWidget()
        self.file_list.setMinimumHeight(100)
        file_layout.addWidget(self.file_list)
        
        btn_add = QPushButton("➕ Agregar archivos")
        btn_add.clicked.connect(self.select_files)
        file_layout.addWidget(btn_add)
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
        files, _ = QFileDialog.getOpenFileNames(
            self, "Seleccionar Archivos", "", "Todos los archivos (*)"
        )
        if files:
            self.files = files
            self.file_list.clear()
            self.file_list.addItems([os.path.basename(f) for f in files])
            self.progress.setValue(0)

    def start_backup(self):
        if not self.files:
            QMessageBox.warning(self, "Error", "Debe seleccionar archivos para respaldar.")
            return

        password = self.passwordField.text() if self.encryptCheckBox.isChecked() else None
        if password and len(password) < 8:
            QMessageBox.warning(self, "Error", "La contraseña debe tener al menos 8 caracteres.")
            return

        frequency = self.scheduleCombo.currentText().split(" ")[0]
        
        self.progress.setVisible(True)
        self.backupButton.setEnabled(False)

        self.thread = BackupThread(self.files, password)
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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec())