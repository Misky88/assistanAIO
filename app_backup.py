# Backup7z/main.py
import sys
import os
import json
import logging
import random
import string

from PyQt6.QtCore import Qt, QDateTime, QTime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
    QCheckBox, QComboBox, QLineEdit, QMessageBox, QListWidget,
    QProgressBar, QTabWidget, QHBoxLayout, QDateTimeEdit, QSizePolicy
)
from PyQt6.QtGui import QIcon
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
        self.thread = None

    def setup_ui(self):
        header = QLabel("💾 Backup B2C")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2980b9;
        """)
        
        self.setWindowTitle("🛡 Backups B2C")
        self.setWindowIcon(QIcon('icon.png'))
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        layout = QVBoxLayout(self)
        self.setLayout(layout)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.addWidget(header, alignment=Qt.AlignmentFlag.AlignCenter)

        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)

        # Tab "Nombre de la Copia"
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
        self.descriptionField.setMinimumHeight(50)
        name_layout.addWidget(QLabel("Descripción:"))
        name_layout.addWidget(self.descriptionField)

        # Tipo de Respaldo
        self.backupTypeCombo = QComboBox()
        self.backupTypeCombo.addItems(["Respaldo Completo", "Respaldo Incremental"])
        name_layout.addWidget(QLabel("Tipo de Respaldo:"))
        name_layout.addWidget(self.backupTypeCombo)

        # Botón para restablecer valores
        btn_reset = QPushButton("🔄 Restablecer")
        btn_reset.clicked.connect(self.reset_name_tab)
        name_layout.addWidget(btn_reset)

        name_tab.setLayout(name_layout)
        tab_widget.addTab(name_tab, "Nombre de la Copia")

        # Tab de selección de archivos
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

        file_layout.addLayout(button_layout)
        file_tab.setLayout(file_layout)
        tab_widget.addTab(file_tab, "Archivos a respaldar")

        # Tab de seguridad
        encrypt_tab = QWidget()
        encrypt_layout = QVBoxLayout()

        # Checkbox para habilitar encriptación
        self.encryptCheckBox = QCheckBox("🔑 Encriptar archivo")
        self.encryptCheckBox.stateChanged.connect(self.update_security_preview)
        encrypt_layout.addWidget(self.encryptCheckBox)

        # Campo para la contraseña
        password_layout = QHBoxLayout()
        self.passwordField = QLineEdit()
        self.passwordField.setPlaceholderText("Contraseña (Longitud mínima de 12 caracteres.)")
        self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)
        self.passwordField.textChanged.connect(self.validate_password)
        password_layout.addWidget(self.passwordField)

        # Botón para mostrar/ocultar contraseña
        self.togglePasswordButton = QPushButton("Mostrar")
        self.togglePasswordButton.setCheckable(True)
        self.togglePasswordButton.clicked.connect(self.toggle_password_visibility)
        password_layout.addWidget(self.togglePasswordButton)

        # Botón para generar contraseña
        self.generatePasswordButton = QPushButton("Generar")
        self.generatePasswordButton.clicked.connect(self.generate_random_password)
        password_layout.addWidget(self.generatePasswordButton)

        encrypt_layout.addLayout(password_layout)

        # Indicador de fortaleza de la contraseña
        self.passwordStrengthLabel = QLabel("Fortaleza: N/A")
        encrypt_layout.addWidget(self.passwordStrengthLabel)

        # Opciones de algoritmo de encriptación
        self.encryptionAlgorithmCombo = QComboBox()
        self.encryptionAlgorithmCombo.addItems(["AES-256"])
        self.encryptionAlgorithmCombo.currentIndexChanged.connect(self.update_security_preview)
        encrypt_layout.addWidget(QLabel("Algoritmo de encriptación:"))
        encrypt_layout.addWidget(self.encryptionAlgorithmCombo)

        # Encriptación de metadatos
        self.metadataEncryptionCheckBox = QCheckBox("🔒 Encriptar nombre de ficheros")
        self.metadataEncryptionCheckBox.stateChanged.connect(self.update_security_preview)
        encrypt_layout.addWidget(self.metadataEncryptionCheckBox)

        # Creación de copias inmutables
        self.immutableBackupCheckBox = QCheckBox("🛡 Crear copia inmutable (no modificable)")
        self.immutableBackupCheckBox.stateChanged.connect(self.toggle_immutability_options)
        encrypt_layout.addWidget(self.immutableBackupCheckBox)

        # Opciones de tiempo de inmutabilidad
        immutability_time_layout = QHBoxLayout()

        self.immutabilityTimeUnitCombo = QComboBox()
        self.immutabilityTimeUnitCombo.addItems(["Días", "Semanas", "Meses", "Años"])
        self.immutabilityTimeUnitCombo.setEnabled(False)
        immutability_time_layout.addWidget(QLabel("Duración de inmutabilidad:"))
        immutability_time_layout.addWidget(self.immutabilityTimeUnitCombo)

        self.immutabilityTimeValueCombo = QComboBox()
        self.immutabilityTimeValueCombo.addItems([str(i) for i in range(1, 11)])
        self.immutabilityTimeValueCombo.setEnabled(False)
        immutability_time_layout.addWidget(self.immutabilityTimeValueCombo)

        encrypt_layout.addLayout(immutability_time_layout)

        # Tamaño de las partes
        self.partSizeCombo = QComboBox()
        self.partSizeCombo.addItems([
            "Sin dividir",
            "10M", "100M", "1000M",
            "650M - CD", "700M - CD",
            "4092M - FAT", "4480M - DVD",
            "8128M - DVD DL", "23040M - BD"
        ])
        encrypt_layout.addWidget(QLabel("Tamaño de las partes:"))
        encrypt_layout.addWidget(self.partSizeCombo)

        # Vista previa de seguridad
        self.securityPreviewLabel = QLabel("Vista previa de seguridad: Encriptación deshabilitada")
        encrypt_layout.addWidget(self.securityPreviewLabel)

        encrypt_tab.setLayout(encrypt_layout)
        tab_widget.addTab(encrypt_tab, "Configuración de seguridad")

        # Tab de registro de actividad
        log_tab = QWidget()
        log_layout = QVBoxLayout()

        self.activityLog = QListWidget()
        log_layout.addWidget(QLabel("Registro de actividad:"))
        log_layout.addWidget(self.activityLog)

        log_tab.setLayout(log_layout)
        tab_widget.addTab(log_tab, "Registro de actividad")

        # Tab de programación
        schedule_tab = QWidget()
        schedule_layout = QVBoxLayout()

        # Tipo de horario
        self.scheduleTypeCombo = QComboBox()
        self.scheduleTypeCombo.addItems([
            "Una vez", "Diario", "Semanal", "Mensual", "Anual", "Temporizador", "Manual", "Al inicio"
        ])
        schedule_layout.addWidget(QLabel("Tipo de horario:"))
        schedule_layout.addWidget(self.scheduleTypeCombo)

        # Selección de días de la semana
        week_days_layout = QHBoxLayout()
        week_days_layout.addWidget(QLabel("Días de la semana:"))

        self.weekDaysCheckBoxes = []
        week_days = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for day in week_days:
            checkbox = QCheckBox(day)
            self.weekDaysCheckBoxes.append(checkbox)
            week_days_layout.addWidget(checkbox)

        schedule_layout.addLayout(week_days_layout)

        # Grupo de CheckBoxes para "En el día"
        day_position_layout = QHBoxLayout()
        day_position_layout.addWidget(QLabel("En el día:"))

        self.dayPositionCheckBoxes = []
        day_positions = ["Primero", "Segundo", "Tercero", "Cuarto", "Último"]
        for position in day_positions:
            checkbox = QCheckBox(position)
            self.dayPositionCheckBoxes.append(checkbox)
            day_position_layout.addWidget(checkbox)

        schedule_layout.addLayout(day_position_layout)

        # Opciones de fecha
        date_options_layout = QHBoxLayout()

        self.dateTimePicker = QDateTimeEdit()
        self.dateTimePicker.setCalendarPopup(True)
        self.dateTimePicker.setDateTime(QDateTime.currentDateTime())
        date_options_layout.addWidget(QLabel("Fecha/hora:"))
        date_options_layout.addWidget(self.dateTimePicker)

        self.dayCombo = QComboBox()
        self.dayCombo.addItems(["Ninguno"] + [str(i) for i in range(1, 32)])
        date_options_layout.addWidget(QLabel("Días:"))
        date_options_layout.addWidget(self.dayCombo)

        self.monthCombo = QComboBox()
        self.monthCombo.addItems([
            "Ninguno", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
            "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
        ])
        date_options_layout.addWidget(QLabel("Meses:"))
        date_options_layout.addWidget(self.monthCombo)

        schedule_layout.addLayout(date_options_layout)

        # Botones para exportar/importar programación
        export_import_layout = QHBoxLayout()
        self.exportScheduleButton = QPushButton("Exportar programación")
        self.exportScheduleButton.clicked.connect(self.export_schedule)
        export_import_layout.addWidget(self.exportScheduleButton)

        self.importScheduleButton = QPushButton("Importar programación")
        self.importScheduleButton.clicked.connect(self.import_schedule)
        export_import_layout.addWidget(self.importScheduleButton)
        schedule_layout.addLayout(export_import_layout)

        # Historial de programaciones
        self.scheduleHistoryList = QListWidget()
        schedule_layout.addWidget(QLabel("Historial de programaciones:"))
        schedule_layout.addWidget(self.scheduleHistoryList)

        # Notificaciones
        self.notificationLabel = QLabel("Notificaciones: No programadas")
        schedule_layout.addWidget(self.notificationLabel)

        schedule_tab.setLayout(schedule_layout)
        tab_widget.addTab(schedule_tab, "Programación")

        # Barra de progreso
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)

        # Botón de acción principal
        self.backupButton = QPushButton("🚀 Iniciar backup ahora")
        self.backupButton.clicked.connect(self.start_backup)
        layout.addWidget(self.backupButton)

    def setup_styles(self):
        self.setStyleSheet("""
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
            QComboBox {
                background-color: white;
                border: 1px solid #ccc;
                padding: 5px;
                font-size: 14px;
                border-radius: 4px;
            }
            QCheckBox {
                font-size: 14px;
            }
        """)

    # def select_destination(self):
    #     """Permite al usuario seleccionar la carpeta de destino."""
    #     folder = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta de Destino")
    #     if folder:
    #         self.destination = folder
    #         self.destinationField.setText(folder)

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
            QMessageBox.warning(self, "Error", "Selecciona archivos para respaldar.")
            return
        name = self.outputNameField.text().strip()
        output_name = name if name else "backup"
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.backupButton.setEnabled(False)
        self.thread = BackupThread(self.files, output_name)
        self.thread.progress.connect(self.progress.setValue)
        self.thread.finished.connect(self.backup_finished)
        self.thread.start()

    def backup_finished(self, success, message):
        self.progress.setVisible(False)
        self.backupButton.setEnabled(True)
        if success:
            QMessageBox.information(self, "Éxito", message)
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
        self.destinationField.clear()
        self.destination = ""
        self.backupTypeCombo.setCurrentIndex(0)
        self.update_preview()

    def remove_selected_item(self):
        """Elimina el elemento seleccionado de la lista de archivos y carpetas."""
        selected_item = self.file_list.currentItem()
        if selected_item:
            item_text = selected_item.text()
            # Buscar y eliminar el elemento de la lista interna
            for file in self.files:
                if os.path.basename(file) == item_text:
                    self.files.remove(file)
                    break
            self.update_file_list()

    def validate_password(self):
        """Valida la fortaleza de la contraseña ingresada."""
        password = self.passwordField.text()
        has_digit = any(c.isdigit() for c in password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_special = any(not c.isalnum() for c in password)

        if len(password) < 8:
            self.passwordStrengthLabel.setText("Fortaleza: Débil")
            self.passwordStrengthLabel.setStyleSheet("color: red;")
        elif len(password) >= 12 and has_digit and has_upper and has_lower and has_special:
            self.passwordStrengthLabel.setText("Fortaleza: Fuerte")
            self.passwordStrengthLabel.setStyleSheet("color: green;")
        elif len(password) >= 8:
            self.passwordStrengthLabel.setText("Fortaleza: Media")
            self.passwordStrengthLabel.setStyleSheet("color: orange;")
        else:
            self.passwordStrengthLabel.setText("Fortaleza: Débil")
            self.passwordStrengthLabel.setStyleSheet("color: red;")

    def update_security_preview(self):
        """Actualiza la vista previa de las configuraciones de seguridad."""
        if self.encryptCheckBox.isChecked():
            algorithm = self.encryptionAlgorithmCombo.currentText()
            metadata = " y metadatos" if self.metadataEncryptionCheckBox.isChecked() else ""
            self.securityPreviewLabel.setText(f"Vista previa de seguridad: Encriptación habilitada ({algorithm}{metadata})")
        else:
            self.securityPreviewLabel.setText("Vista previa de seguridad: Encriptación deshabilitada")

    def toggle_immutability_options(self):
        """Habilita o deshabilita las opciones de tiempo de inmutabilidad."""
        is_checked = self.immutableBackupCheckBox.isChecked()
        self.immutabilityTimeUnitCombo.setEnabled(is_checked)
        self.immutabilityTimeValueCombo.setEnabled(is_checked)

    def log_activity(self, message: str):
        """Registra una actividad en el log de la interfaz."""
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        self.activityLog.addItem(formatted_message)
        logging.info(message)

    def toggle_password_visibility(self):
        """Alterna entre mostrar y ocultar la contraseña."""
        if self.togglePasswordButton.isChecked():
            self.passwordField.setEchoMode(QLineEdit.EchoMode.Normal)
            self.togglePasswordButton.setText("Ocultar")
        else:
            self.passwordField.setEchoMode(QLineEdit.EchoMode.Password)
            self.togglePasswordButton.setText("Mostrar")

    def generate_random_password(self):
        """Genera una contraseña aleatoria y la establece en el campo de contraseña."""
        length = 16
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_+-="
        password = ''.join(random.choice(characters) for i in range(length))
        self.passwordField.setText(password)
        self.validate_password()  # Actualizar indicador de fuerza

    def export_schedule(self):
        """Exporta la configuración de programación a un archivo JSON."""
        file_path, _ = QFileDialog.getSaveFileName(self, "Exportar programación", "", "JSON Files (*.json)")
        if file_path:
            schedule_data = {
                "schedule_type": self.scheduleTypeCombo.currentText(),
                "datetime": self.dateTimePicker.dateTime().toString(),
                "selected_weekdays": [cb.isChecked() for cb in self.weekDaysCheckBoxes],
                "selected_positions": [cb.isChecked() for cb in self.dayPositionCheckBoxes],
                "day": self.dayCombo.currentText(),
                "month": self.monthCombo.currentText()
            }
            try:
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(schedule_data, file, indent=2)
                QMessageBox.information(self, "Éxito", "Programación exportada con éxito.")
                self.log_activity(f"Programación exportada a: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al exportar: {str(e)}")
                self.log_activity(f"Error al exportar programación: {str(e)}")

    def import_schedule(self):
        """Importa la configuración de programación desde un archivo JSON."""
        file_path, _ = QFileDialog.getOpenFileName(self, "Importar programación", "", "JSON Files (*.json)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    schedule_data = json.load(file)
                
                # Aplicar configuración importada
                self.scheduleTypeCombo.setCurrentText(schedule_data.get("schedule_type", "Manual"))
                
                if "datetime" in schedule_data:
                    self.dateTimePicker.setDateTime(QDateTime.fromString(schedule_data["datetime"]))
                
                # Restaurar checkboxes de días de la semana
                weekdays = schedule_data.get("selected_weekdays", [])
                for i, checked in enumerate(weekdays):
                    if i < len(self.weekDaysCheckBoxes):
                        self.weekDaysCheckBoxes[i].setChecked(checked)
                
                # Restaurar checkboxes de posiciones
                positions = schedule_data.get("selected_positions", [])
                for i, checked in enumerate(positions):
                    if i < len(self.dayPositionCheckBoxes):
                        self.dayPositionCheckBoxes[i].setChecked(checked)
                
                self.dayCombo.setCurrentText(schedule_data.get("day", "Ninguno"))
                self.monthCombo.setCurrentText(schedule_data.get("month", "Ninguno"))
                
                QMessageBox.information(self, "Éxito", "Programación importada con éxito.")
                self.log_activity(f"Programación importada desde: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al importar: {str(e)}")
                self.log_activity(f"Error al importar programación: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BackupApp()
    window.show()
    sys.exit(app.exec())