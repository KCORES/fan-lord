import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import sys
import ctypes
from datetime import datetime
import locale

# 在文件顶部添加版本常量
VERSION = "v0.1.1"


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def run_as_admin():
    try:
        if not is_admin():
            # Restart program with admin privileges
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
            sys.exit()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to get admin rights:\n{str(e)}")
        sys.exit(1)


def get_resource_path(relative_path):
    """Get absolute path to resource file"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # If not packaged, use current folder
        base_path = os.path.abspath(os.path.dirname(__file__))

    return os.path.join(base_path, relative_path)


def get_system_language():
    """Get system language and match it with available languages"""
    try:
        system_lang = locale.getdefaultlocale()[0]

        # Map system language codes to our available languages
        lang_mapping = {
            "zh": "中文",  # Chinese
            "ja": "日本語",  # Japanese
            "en": "English",  # English
        }

        # Get the first two letters of language code (e.g., 'zh_CN' -> 'zh')
        system_lang_prefix = system_lang.split("_")[0].lower()

        # Return matched language or default to English
        return lang_mapping.get(system_lang_prefix, "English")
    except:
        return "English"


class CustomScale(tk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.canvas = tk.Canvas(self, height=20, highlightthickness=0)
        self.canvas.pack(fill="x", pady=(0, 5))
        self.scale = tk.Scale(self, **kwargs)
        self.scale.pack(fill="x")

        self.update_background()
        self.scale.configure(command=self.update_background)

    def update_background(self, *args):
        self.canvas.delete("all")
        width = self.canvas.winfo_width()
        if width == 0:  # Width may be 0 during window initialization
            self.canvas.after(10, self.update_background)
            return

        value = self.scale.get()
        threshold = 30
        threshold_x = width * (threshold / 100)
        current_x = width * (value / 100)

        # Draw gray part (0-30)
        if threshold_x > 0:
            self.canvas.create_rectangle(
                0, 0, min(threshold_x, current_x), 5, fill="#D3D3D3", outline=""
            )

        # Draw green part (30-100)
        if current_x > threshold_x:
            self.canvas.create_rectangle(
                threshold_x, 0, current_x, 5, fill="#90EE90", outline=""
            )

    def bind(self, sequence=None, func=None, add=None):
        self.scale.bind(sequence, func, add)

    def get(self):
        return self.scale.get()


class IPMIGui:
    def __init__(self, root):
        self.root = root

        # Add language configuration
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
                "command_error": "执行命令时出错：",
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
                "command_failed": "コマンドの実行に失敗しました：",
                "command_error": "コマンドの実行中にエラーが発生しました：",
            },
        }

        # Initialize language based on system settings
        self.current_language = get_system_language()
        # Create a class variable to store StringVar
        self.language_var = tk.StringVar(value=self.current_language)

        # Create menu bar
        self.menubar = tk.Menu(root)
        self.root.config(menu=self.menubar)

        # Create language menu
        self.language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="语言", menu=self.language_menu)

        # Add language options
        for lang in self.languages.keys():
            self.language_menu.add_radiobutton(
                label=lang,
                variable=self.language_var,  # Use class variable
                value=lang,  # Set option value
                command=lambda l=lang: self.change_language(l),
            )

        # Set window icon
        if getattr(sys, "frozen", False):
            # If running as packaged executable
            icon_path = os.path.join(sys._MEIPASS, "fan-lord.ico")
        else:
            # If running as Python script
            icon_path = "fan-lord.ico"

        self.root.iconbitmap(icon_path)

        # Get executable directory
        if getattr(sys, "frozen", False):
            # If running as packaged executable
            self.current_dir = os.path.dirname(sys.executable)
        else:
            # If running as Python script
            self.current_dir = os.path.dirname(os.path.abspath(__file__))

        # Modify this part
        # Use get_resource_path to get IPMI tool path
        self.ipmi_exe = get_resource_path("IPMICFG-Win.exe")

        # Add debug info
        print(f"IPMI exe path: {self.ipmi_exe}")
        print(f"File exists: {os.path.exists(self.ipmi_exe)}")

        # Check if IPMI tool exists
        if not os.path.exists(self.ipmi_exe):
            messagebox.showerror(
                "Error", f"IPMICFG-Win.exe not found at: {self.ipmi_exe}"
            )
            root.destroy()
            return

        # Set window size and position
        window_width = 800
        window_height = 600
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        center_x = int(screen_width / 2 - window_width / 2)
        center_y = int(screen_height / 2 - window_height / 2)
        self.root.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")

        # Create mode selection frame
        mode_frame = tk.LabelFrame(root, text="预设模式", padx=10, pady=5)
        mode_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(mode_frame, text="静音模式", command=self.silent_mode).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(mode_frame, text="性能模式", command=self.performance_mode).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(mode_frame, text="全速模式", command=self.full_speed_mode).pack(
            side=tk.LEFT, padx=5
        )

        # Create manual control frame
        manual_frame = tk.LabelFrame(root, text="手动控制", padx=10, pady=5)
        manual_frame.pack(fill="x", padx=10, pady=5)

        # CPU fan control
        tk.Label(manual_frame, text="CPU风扇转速").pack()
        self.cpu_scale = CustomScale(
            manual_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
        )
        self.cpu_scale.bind("<ButtonRelease-1>", self.on_cpu_scale_release)
        self.cpu_scale.pack(fill="x")

        # Peripheral fan control
        tk.Label(manual_frame, text="外设风扇转速").pack()
        self.peripheral_scale = CustomScale(
            manual_frame,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
        )
        self.peripheral_scale.bind(
            "<ButtonRelease-1>", self.on_peripheral_scale_release
        )
        self.peripheral_scale.pack(fill="x")

        # Add warning label
        warning_label = tk.Label(
            manual_frame,
            text="注意：如果数值小于30%，BMC可能会自动重置风扇转速为全速",
            fg="red",
            wraplength=600,  # Text auto wrap width
        )
        warning_label.pack(pady=5)

        # Add reset button
        tk.Button(
            manual_frame, text="重置为自动控制", command=self.reset_fan_control
        ).pack(pady=5)

        # Create status display area
        status_frame = tk.LabelFrame(root, text="状态信息", padx=10, pady=5)
        status_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Add scrollbar
        scrollbar = tk.Scrollbar(status_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.status_text = tk.Text(
            status_frame, height=10, wrap=tk.WORD, yscrollcommand=scrollbar.set
        )
        self.status_text.pack(fill="both", expand=True)
        scrollbar.config(command=self.status_text.yview)

        # Add credits frame
        credits_frame = tk.Frame(root)
        credits_frame.pack(fill="x", padx=10, pady=5)

        # Add version label with link (修改)
        version_label = tk.Label(
            credits_frame, text=f"{VERSION}", fg="blue", cursor="hand2"
        )
        version_label.pack(side=tk.RIGHT)
        version_label.bind(
            "<Button-1>", lambda e: self.open_url("https://github.com/KCORES/fan-lord")
        )

        project_suffix = tk.Label(credits_frame, text=" opensource project")
        project_suffix.pack(side=tk.RIGHT)

        project_link = tk.Label(credits_frame, text="KCORES", fg="blue", cursor="hand2")
        project_link.pack(side=tk.RIGHT)
        project_link.bind(
            "<Button-1>", lambda e: self.open_url("https://github.com/kcores")
        )

        project_label = tk.Label(credits_frame, text=" | This is a ")
        project_label.pack(side=tk.RIGHT)

        author_link = tk.Label(
            credits_frame, text="karminski", fg="blue", cursor="hand2"
        )
        author_link.pack(side=tk.RIGHT)
        author_link.bind(
            "<Button-1>", lambda e: self.open_url("https://github.com/karminski")
        )

        author_label = tk.Label(credits_frame, text="Created by: ")
        author_label.pack(side=tk.RIGHT)

        # Update all text to current language
        self.update_texts()

    def update_texts(self):
        """Update all interface text to currently selected language"""
        lang = self.languages[self.current_language]

        # Update window title
        self.root.title(lang["window_title"])

        # Update menu bar text
        self.menubar.entryconfigure(1, label=lang["language_menu"])

        # Update frames and their components
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.LabelFrame):
                # Update LabelFrame titles
                if (
                    "预设模式" in widget.cget("text")
                    or "Preset" in widget.cget("text")
                    or "プリセット" in widget.cget("text")
                ):
                    widget.configure(text=lang["preset_modes"])
                elif (
                    "手动控制" in widget.cget("text")
                    or "Manual" in widget.cget("text")
                    or "手動" in widget.cget("text")
                ):
                    widget.configure(text=lang["manual_control"])
                elif (
                    "状态信息" in widget.cget("text")
                    or "Status" in widget.cget("text")
                    or "ステータス" in widget.cget("text")
                ):
                    widget.configure(text=lang["status_info"])

                # Update components inside frames
                for child in widget.winfo_children():
                    # Update button text
                    if isinstance(child, tk.Button):
                        if any(
                            x in child.cget("text")
                            for x in ["静音模式", "Silent", "サイレント"]
                        ):
                            child.configure(text=lang["silent_mode"])
                        elif any(
                            x in child.cget("text")
                            for x in ["性能模式", "Performance", "パフォーマンス"]
                        ):
                            child.configure(text=lang["performance_mode"])
                        elif any(
                            x in child.cget("text")
                            for x in ["全速模式", "Full Speed", "フルスピード"]
                        ):
                            child.configure(text=lang["full_speed_mode"])
                        elif any(
                            x in child.cget("text")
                            for x in ["重置为自动控制", "Reset", "自動制御"]
                        ):
                            child.configure(text=lang["reset_auto"])

                    # Update label text
                    elif isinstance(child, tk.Label):
                        if any(
                            x in child.cget("text")
                            for x in ["CPU风扇转速", "CPU Fan", "CPUファン"]
                        ):
                            child.configure(text=lang["cpu_fan_speed"])
                        elif any(
                            x in child.cget("text")
                            for x in ["外设风扇转速", "Peripheral Fan", "周辺機器"]
                        ):
                            child.configure(text=lang["peripheral_fan_speed"])
                        elif (
                            "注意" in child.cget("text")
                            or "Note" in child.cget("text")
                            or "注意" in child.cget("text")
                        ):
                            child.configure(text=lang["warning_text"])

                    # Recursively process nested components
                    if hasattr(child, "winfo_children"):
                        for grandchild in child.winfo_children():
                            if isinstance(grandchild, tk.Label):
                                if any(
                                    x in grandchild.cget("text")
                                    for x in ["CPU风扇转速", "CPU Fan", "CPUファン"]
                                ):
                                    grandchild.configure(text=lang["cpu_fan_speed"])
                                elif any(
                                    x in grandchild.cget("text")
                                    for x in [
                                        "外设风扇转速",
                                        "Peripheral Fan",
                                        "周辺機器",
                                    ]
                                ):
                                    grandchild.configure(
                                        text=lang["peripheral_fan_speed"]
                                    )

    def change_language(self, new_language):
        """Switch interface language"""
        self.current_language = new_language
        self.update_texts()

    def execute_command(self, command):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lang = self.languages[self.current_language]

        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.update_status(
                    f"[{current_time}] {lang['execute_command']}: {command} {lang['command_success']}\n",
                    "success",
                )
            else:
                self.update_status(
                    f"[{current_time}] {lang['execute_command']}: {command} {lang['command_failed']}\n{result.stderr}\n",
                    "error",
                )
        except Exception as e:
            self.update_status(
                f"[{current_time}] {lang['execute_command']}: {command} {lang['command_error']}\n{str(e)}\n",
                "error",
            )

    def update_status(self, message, status_type):
        if status_type == "error":
            tag = "error"
            color = "red"
        else:
            tag = "success"
            color = "green"

        self.status_text.tag_config(tag, foreground=color)
        self.status_text.insert(tk.END, message, tag)
        self.status_text.see(tk.END)  # Auto scroll to latest content
        self.root.update()

    def silent_mode(self):
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x28')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x28')

    def performance_mode(self):
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x32')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x64')

    def full_speed_mode(self):
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x64')
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x64')

    def on_cpu_scale_release(self, event):
        value = self.cpu_scale.get()
        cpu_value = format(int(value), "x").zfill(2)
        self.execute_command(
            f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x00 0x{cpu_value}'
        )

    def on_peripheral_scale_release(self, event):
        value = self.peripheral_scale.get()
        peripheral_value = format(int(value), "x").zfill(2)
        self.execute_command(
            f'"{self.ipmi_exe}" -raw 0x30 0x70 0x66 0x01 0x01 0x{peripheral_value}'
        )

    def reset_fan_control(self):
        self.execute_command(f'"{self.ipmi_exe}" -raw 0x30 0x45 0x01 0x01')

    # Add method to open URL
    def open_url(self, url):
        import webbrowser

        webbrowser.open(url)


if __name__ == "__main__":
    # Check admin privileges
    run_as_admin()

    root = tk.Tk()
    app = IPMIGui(root)
    root.mainloop()
