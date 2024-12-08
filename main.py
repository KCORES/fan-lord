import sys
import os
import ctypes
import subprocess
from datetime import datetime
import locale
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QSlider,
    QTextEdit,
    QMenuBar,
    QMenu,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QColor, QAction, QActionGroup

VERSION = "v0.1.3"


# Keep original helper functions
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    try:
        if not is_admin():
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
    except Exception as e:
        print(f"Failed to get admin rights: {str(e)}")
        sys.exit(1)


class CustomSlider(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Create progress bar display area
        self.progress_bar = QFrame(self)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setStyleSheet("background-color: #D3D3D3;")

        # Create slider
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.valueChanged.connect(self.update_progress)
        self.slider.sliderReleased.connect(self.on_slider_released)

        layout.addWidget(self.progress_bar)
        layout.addWidget(self.slider)
        layout.setSpacing(5)

        # Add variable to store last value
        self.last_value = 0

    def update_progress(self, value):
        threshold = 30
        if value < threshold:
            color = "#D3D3D3"  # Gray
        else:
            color = "#90EE90"  # Light green
        self.progress_bar.setStyleSheet(f"background-color: {color};")

    def value(self):
        return self.slider.value()

    def on_slider_released(self):
        """Triggered when slider is released"""
        current_value = self.slider.value()
        if current_value != self.last_value:
            self.last_value = current_value
            # Emit custom signal
            if hasattr(self, "value_changed_on_release"):
                self.value_changed_on_release(current_value)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Set application icon
        icon_path = self.get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        # Initialize language configuration
        self.init_languages()
        # Initialize IPMI tool path
        self.init_ipmi_tool()
        self.init_ui()

    def get_icon_path(self):
        """Get icon path"""
        if getattr(sys, "frozen", False):
            # If running as executable
            base_path = sys._MEIPASS
        else:
            # If running as Python script
            base_path = os.path.dirname(os.path.abspath(__file__))

        icon_path = os.path.join(base_path, "fan-lord.ico")
        return icon_path if os.path.exists(icon_path) else None

    def init_languages(self):
        """Initialize language configuration"""
        self.languages = {
            "中文": {
                "window_title": "Fan Lord for Supermicro X-Series",
                "preset_modes": "预设模式",
                "silent_mode": "静音模式",
                "performance_mode": "性能模式",
                "full_speed_mode": "全速模式",
                "manual_control": "手动控制",
                "cpu_fan_speed": "CPU风扇转速",
                "peripheral_fan_speed": "外设风扇转速",
                "warning_text": "注意：如果数值小于30%，BMC可能会自动重置风扇转速为全速",
                "reset_auto": "重置为自动控制",
                "status_info": "状态信息",
                "created_by": "Created by: ",
                "this_is_a": " | This is a ",
                "project": " opensource project",
                "language_menu": "语言",
                "execute_command": "执行命令",
                "command_success": "命令执行成功！",
                "command_failed": "命令执行失败：",
                "command_error": "执行出错：",
            },
            "English": {
                "window_title": "Fan Lord for Supermicro X-Series",
                "preset_modes": "Preset Modes",
                "silent_mode": "Silent Mode",
                "performance_mode": "Performance Mode",
                "full_speed_mode": "Full Speed Mode",
                "manual_control": "Manual Control",
                "cpu_fan_speed": "CPU Fan Speed",
                "peripheral_fan_speed": "Peripheral Fan Speed",
                "warning_text": "Note: If the value is less than 30%, BMC may automatically reset fan speed to full speed",
                "reset_auto": "Reset to Auto Control",
                "status_info": "Status Information",
                "created_by": "Created by: ",
                "this_is_a": " | This is a ",
                "project": " opensource project",
                "language_menu": "Language",
                "execute_command": "Execute command",
                "command_success": "Command executed successfully!",
                "command_failed": "Command execution failed:",
                "command_error": "Error executing command:",
            },
            "日本語": {
                "window_title": "Fan Lord for Supermicro X-Series",
                "preset_modes": "プリセットモード",
                "silent_mode": "サイレントモード",
                "performance_mode": "パフォーマンスモード",
                "full_speed_mode": "フルスピードモード",
                "manual_control": "手動制御",
                "cpu_fan_speed": "CPUファン速度",
                "peripheral_fan_speed": "周辺機器ファン速度",
                "warning_text": "注意：値が30%未満の場合、BMCが自動的にファン速度をフルスピードにリセットする可能性があります",
                "reset_auto": "自動制御にリセット",
                "status_info": "ステータス情報",
                "created_by": "作成者: ",
                "this_is_a": " | これは ",
                "project": " オープンソースプロジェクトです",
                "language_menu": "言語",
                "execute_command": "コマンドを実行",
                "command_success": "コマンドが正常に実行されました！",
                "command_failed": "コマンド実行に失敗しました：",
                "command_error": "コマンドの実行中にエラーが発生しました：",
            },
        }
        self.current_language = self.get_system_language()

    def get_system_language(self):
        """Get system language"""
        try:
            system_lang = locale.getdefaultlocale()[0]
            lang_mapping = {
                "zh": "中文",
                "ja": "日本語",
                "en": "English",
            }
            system_lang_prefix = system_lang.split("_")[0].lower()
            return lang_mapping.get(system_lang_prefix, "English")
        except:
            return "English"

    def change_language(self, language):
        """Switch interface language"""
        try:
            self.current_language = language
            self.update_texts()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to change language: {str(e)}")

    def update_texts(self):
        """Update all interface texts"""
        lang = self.languages[self.current_language]

        # Update window title
        self.setWindowTitle(lang["window_title"])

        # Update menu bar - use class attributes directly
        self.language_menu.setTitle(lang["language_menu"])

        # Update preset modes area
        preset_frame = self.findChild(QFrame, "preset_frame")
        if preset_frame:
            preset_frame.findChild(QLabel, "preset_title").setText(lang["preset_modes"])
            preset_frame.findChild(QPushButton, "silent_btn").setText(
                lang["silent_mode"]
            )
            preset_frame.findChild(QPushButton, "performance_btn").setText(
                lang["performance_mode"]
            )
            preset_frame.findChild(QPushButton, "full_speed_btn").setText(
                lang["full_speed_mode"]
            )

        # Update manual control area
        manual_frame = self.findChild(QFrame, "manual_frame")
        if manual_frame:
            manual_frame.findChild(QLabel, "manual_title").setText(
                lang["manual_control"]
            )
            manual_frame.findChild(QLabel, "cpu_label").setText(lang["cpu_fan_speed"])
            manual_frame.findChild(QLabel, "peripheral_label").setText(
                lang["peripheral_fan_speed"]
            )
            manual_frame.findChild(QLabel, "warning_label").setText(
                lang["warning_text"]
            )
            manual_frame.findChild(QPushButton, "reset_btn").setText(lang["reset_auto"])

        # Update status information area
        status_frame = self.findChild(QFrame, "status_frame")
        if status_frame:
            status_frame.findChild(QLabel, "status_title").setText(lang["status_info"])

    def init_ipmi_tool(self):
        """Initialize IPMI tool path"""
        if getattr(sys, "frozen", False):
            # If running as executable
            base_path = sys._MEIPASS
        else:
            # If running as Python script
            base_path = os.path.dirname(os.path.abspath(__file__))

        self.ipmi_exe = os.path.join(base_path, "IPMICFG-Win.exe")

        # Check if IPMI tool exists
        if not os.path.exists(self.ipmi_exe):
            QMessageBox.critical(
                self, "Error", f"IPMICFG-Win.exe not found at: {self.ipmi_exe}"
            )
            sys.exit(1)

    def execute_command(self, command):
        """Execute IPMI command and update status"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.update_status(
                    f"[{current_time}] Execute command: {command}\nCommand executed successfully!\n",
                    "success",
                )
            else:
                self.update_status(
                    f"[{current_time}] Execute command: {command}\nCommand execution failed:\n{result.stderr}\n",
                    "error",
                )
        except Exception as e:
            self.update_status(
                f"[{current_time}] Execute command: {command}\nError executing command:\n{str(e)}\n",
                "error",
            )

    def update_status(self, message, status_type):
        """Update status information display"""
        color = "red" if status_type == "error" else "green"
        self.status_text.setTextColor(QColor(color))
        self.status_text.append(message)
        # Scroll to bottom
        self.status_text.verticalScrollBar().setValue(
            self.status_text.verticalScrollBar().maximum()
        )

    def init_ui(self):
        # Set window basic properties
        self.setWindowTitle("Fan Lord for Supermicro X-Series")
        self.setMinimumSize(800, 600)

        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Create menu bar
        self.create_menu_bar()

        # Create preset modes area
        self.create_preset_modes()

        # Create manual control area
        self.create_manual_control()

        # Create status information area
        self.create_status_area()

        # Create footer
        self.create_footer()

    def create_menu_bar(self):
        menubar = self.menuBar()

        # Create language menu and save as class attribute
        self.language_menu = QMenu(
            self.languages[self.current_language]["language_menu"], self
        )
        self.language_menu.setObjectName("language_menu")
        menubar.addMenu(self.language_menu)

        # Add language options
        languages = ["中文", "English", "日本語"]
        language_group = QActionGroup(self)
        for lang in languages:
            action = QAction(lang, self, checkable=True)
            language_group.addAction(action)
            self.language_menu.addAction(action)
            if lang == self.current_language:  # Set default based on system language
                action.setChecked(True)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))

    def create_preset_modes(self):
        # Create preset modes frame
        preset_frame = QFrame()
        preset_frame.setObjectName("preset_frame")
        preset_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        preset_layout = QVBoxLayout(preset_frame)

        # Title
        title = QLabel(self.languages[self.current_language]["preset_modes"])
        title.setObjectName("preset_title")
        title.setStyleSheet("font-weight: bold;")
        preset_layout.addWidget(title)

        # Button container
        button_layout = QHBoxLayout()

        # Create preset mode buttons and set object names
        silent_btn = QPushButton(self.languages[self.current_language]["silent_mode"])
        silent_btn.setObjectName("silent_btn")
        performance_btn = QPushButton(
            self.languages[self.current_language]["performance_mode"]
        )
        performance_btn.setObjectName("performance_btn")
        full_speed_btn = QPushButton(
            self.languages[self.current_language]["full_speed_mode"]
        )
        full_speed_btn.setObjectName("full_speed_btn")

        # Connect signals
        silent_btn.clicked.connect(self.silent_mode)
        performance_btn.clicked.connect(self.performance_mode)
        full_speed_btn.clicked.connect(self.full_speed_mode)

        # Add buttons to layout
        button_layout.addWidget(silent_btn)
        button_layout.addWidget(performance_btn)
        button_layout.addWidget(full_speed_btn)
        button_layout.addStretch()

        preset_layout.addLayout(button_layout)
        self.centralWidget().layout().addWidget(preset_frame)

    def create_manual_control(self):
        # Create manual control frame
        manual_frame = QFrame()
        manual_frame.setObjectName("manual_frame")
        manual_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        manual_layout = QVBoxLayout(manual_frame)

        # Title
        title = QLabel(self.languages[self.current_language]["manual_control"])
        title.setObjectName("manual_title")
        title.setStyleSheet("font-weight: bold;")
        manual_layout.addWidget(title)

        # CPU fan control
        cpu_control_layout = QHBoxLayout()
        cpu_label = QLabel(self.languages[self.current_language]["cpu_fan_speed"])
        cpu_label.setObjectName("cpu_label")
        self.cpu_percentage = QLabel("0%")  # Add percentage label
        cpu_control_layout.addWidget(cpu_label)
        cpu_control_layout.addWidget(self.cpu_percentage)
        cpu_control_layout.addStretch()

        self.cpu_slider = CustomSlider()
        self.cpu_slider.value_changed_on_release = self.on_cpu_slider_release
        self.cpu_slider.slider.valueChanged.connect(
            lambda value: self.cpu_percentage.setText(f"{value}%")
        )

        # Peripheral fan control
        peripheral_control_layout = QHBoxLayout()
        peripheral_label = QLabel(
            self.languages[self.current_language]["peripheral_fan_speed"]
        )
        peripheral_label.setObjectName("peripheral_label")
        self.peripheral_percentage = QLabel("0%")  # Add percentage label
        peripheral_control_layout.addWidget(peripheral_label)
        peripheral_control_layout.addWidget(self.peripheral_percentage)
        peripheral_control_layout.addStretch()

        self.peripheral_slider = CustomSlider()
        self.peripheral_slider.value_changed_on_release = (
            self.on_peripheral_slider_release
        )
        self.peripheral_slider.slider.valueChanged.connect(
            lambda value: self.peripheral_percentage.setText(f"{value}%")
        )

        # Warning text
        warning_label = QLabel(self.languages[self.current_language]["warning_text"])
        warning_label.setObjectName("warning_label")
        warning_label.setStyleSheet("color: red;")
        warning_label.setWordWrap(True)

        # Reset button
        reset_btn = QPushButton(self.languages[self.current_language]["reset_auto"])
        reset_btn.setObjectName("reset_btn")
        reset_btn.clicked.connect(self.reset_fan_control)

        # Add components to layout
        manual_layout.addLayout(cpu_control_layout)
        manual_layout.addWidget(self.cpu_slider)
        manual_layout.addLayout(peripheral_control_layout)
        manual_layout.addWidget(self.peripheral_slider)
        manual_layout.addWidget(warning_label)
        manual_layout.addWidget(reset_btn)

        self.centralWidget().layout().addWidget(manual_frame)

    def create_status_area(self):
        # Create status information frame
        status_frame = QFrame()
        status_frame.setObjectName("status_frame")
        status_frame.setFrameStyle(QFrame.Shape.Box | QFrame.Shadow.Sunken)
        status_layout = QVBoxLayout(status_frame)

        # Title
        title = QLabel(self.languages[self.current_language]["status_info"])
        title.setObjectName("status_title")
        title.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(title)

        # Status text box
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        status_layout.addWidget(self.status_text)

        self.centralWidget().layout().addWidget(status_frame)

    def create_footer(self):
        footer_frame = QFrame()
        footer_layout = QHBoxLayout(footer_frame)

        # Author information
        author_label = QLabel("Created by: ")
        author_link = QLabel('<a href="https://github.com/karminski">karminski</a>')
        author_link.setOpenExternalLinks(True)

        # Project information
        project_label = QLabel(" | This is a ")
        project_link = QLabel('<a href="https://github.com/kcores">KCORES</a>')
        project_link.setOpenExternalLinks(True)
        project_suffix = QLabel(" opensource project")

        # Version information
        version_link = QLabel(
            f'<a href="https://github.com/KCORES/fan-lord">{VERSION}</a>'
        )
        version_link.setOpenExternalLinks(True)

        # Add components to layout
        footer_layout.addWidget(author_label)
        footer_layout.addWidget(author_link)
        footer_layout.addWidget(project_label)
        footer_layout.addWidget(project_link)
        footer_layout.addWidget(project_suffix)
        footer_layout.addStretch()
        footer_layout.addWidget(version_link)

        self.centralWidget().layout().addWidget(footer_frame)

    # Implement control function slots
    def silent_mode(self):
        """Silent mode: Set CPU and peripheral fans to 40% speed"""
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x28')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x28')
        # Update slider positions
        self.cpu_slider.slider.setValue(40)
        self.peripheral_slider.slider.setValue(40)

    def performance_mode(self):
        """Performance mode: CPU fan 50%, peripheral fan 100%"""
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x32')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x64')
        # Update slider positions
        self.cpu_slider.slider.setValue(50)
        self.peripheral_slider.slider.setValue(100)

    def full_speed_mode(self):
        """Full speed mode: All fans 100%"""
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x64')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x64')
        # Update slider positions
        self.cpu_slider.slider.setValue(100)
        self.peripheral_slider.slider.setValue(100)

    def on_cpu_slider_release(self, value):
        """CPU fan speed control - only triggered when slider is released"""
        cpu_value = format(value, "x").zfill(2)
        self.execute_command(
            f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x{cpu_value}'
        )

    def on_peripheral_slider_release(self, value):
        """Peripheral fan speed control - only triggered when slider is released"""
        peripheral_value = format(value, "x").zfill(2)
        self.execute_command(
            f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x{peripheral_value}'
        )

    def reset_fan_control(self):
        """Reset to automatic control mode"""
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x45 0x01 0x01')
        # Reset slider positions
        self.cpu_slider.slider.setValue(0)
        self.peripheral_slider.slider.setValue(0)


if __name__ == "__main__":
    # Check administrator privileges
    try:
        if not is_admin():
            # Request administrator privileges and restart program
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()

        # If already has administrator privileges, start program normally
        app = QApplication(sys.argv)
        # Set application icon (shown in start menu and taskbar)
        icon_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "fan-lord.ico"
        )
        if os.path.exists(icon_path):
            app.setWindowIcon(QIcon(icon_path))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        # If failed to get administrator privileges, show error message
        if QApplication.instance() is None:
            app = QApplication(sys.argv)
        QMessageBox.critical(
            None, "Error", f"Failed to get administrator privileges:\n{str(e)}"
        )
        sys.exit(1)
