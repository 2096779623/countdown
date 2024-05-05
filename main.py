import sys
import json
import ctypes
import os
import winreg
from PyQt5 import QtCore, QtGui, QtWidgets

class CountdownWindow(QtWidgets.QWidget):
    def __init__(self, settings_manager):
        super().__init__()
        desktop = QtWidgets.QDesktopWidget().screenGeometry()
        self.setMinimumSize(desktop.width()-100, desktop.height()-100) 
        self.setMaximumSize(9999, 9999)  
        self.settings_manager = settings_manager
        self.settings_window = SettingsWindow(settings_manager, self)
        self.settings_window.font_changed.connect(self.update_font)
        self.settings_window = SettingsWindow(self.settings_manager, self)
        wallpaper_path = self.settings_manager.get_setting("wallpaper_path")
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.dragging = False
        self.old_pos = None
        self.settings_window = SettingsWindow(self.settings_manager, self)
        self.settings_window.closed.connect(self.reload_settings)
        self.load_settings()

    def reload_settings(self):
        self.settings_manager.load_settings()
        wallpaper_path = self.settings_manager.get_setting("wallpaper_path")
        self.settings_manager.set_setting("wallpaper_path", wallpaper_path)
        self.load_settings()

    def load_settings(self):
        countdown_date_str = self.settings_manager.get_setting("countdown_date")
        if not countdown_date_str:
            self.countdown_date = QtCore.QDateTime.currentDateTime()  
        else:
            self.countdown_date = QtCore.QDateTime.fromString(countdown_date_str, QtCore.Qt.ISODate)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)



    def closeEvent(self, event):
        self.restore_original_wallpaper()
        event.accept()

    def update_font(self, font):
        self.font = font
        self.update()

    def restore_original_wallpaper(self):
        wallpaper_path = self.settings_manager.get_original_wallpaper_path()
        if wallpaper_path:
            ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        opacity = self.settings_manager.get_setting("opacity") / 100
        painter.setOpacity(opacity)
        remaining_time = QtCore.QDateTime.currentDateTime().secsTo(self.countdown_date)
        days, remainder = divmod(remaining_time, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        display_text = self.settings_manager.get_setting("text").replace("%d", str(days)).replace("%h", str(hours)).replace("%m", str(minutes)).replace("%s", str(seconds))

        font_string = self.settings_manager.get_setting("font")
        font = QtGui.QFont()
        font.fromString(font_string)
        font.setPointSize(self.settings_manager.get_setting("font_size"))  

        painter.setFont(font)
        painter.setPen(QtGui.QColor(self.settings_manager.get_setting("font_color")))
        
        painter.drawText(0, 0, self.width(), self.height(), QtCore.Qt.AlignCenter, display_text)



    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.globalPos() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False

    def update_timer(self):
        self.update()


    closed = QtCore.pyqtSignal()

class SettingsWindow(QtWidgets.QWidget):
    closed = QtCore.pyqtSignal()
    font_changed = QtCore.pyqtSignal(QtGui.QFont)

    def __init__(self, settings_manager, countdown_window):
        super().__init__()
        self.settings_manager = settings_manager
        self.countdown_window = countdown_window
        self.setWindowTitle("设置")
        layout = QtWidgets.QVBoxLayout()

        
        layout.addWidget(QtWidgets.QLabel("倒计时文字："))
        self.text_edit = QtWidgets.QLineEdit(self.settings_manager.get_setting("text"))
        layout.addWidget(self.text_edit)
        layout.addWidget(QtWidgets.QLabel("字体大小："))
        self.font_size_spinbox = QtWidgets.QSpinBox()
        self.font_size_spinbox.setRange(1, 100)
        self.font_size_spinbox.setValue(self.settings_manager.get_setting("font_size"))
        layout.addWidget(self.font_size_spinbox)
        self.font_color_button = QtWidgets.QPushButton("选择字体颜色")
        self.font_color_button.clicked.connect(self.select_font_color)
        layout.addWidget(self.font_color_button)
        self.font_select_button = QtWidgets.QPushButton("选择字体")
        self.font_select_button.clicked.connect(self.select_font)
        layout.addWidget(self.font_select_button)
        self.wallpaper_button = QtWidgets.QPushButton("选择壁纸")
        self.wallpaper_button.clicked.connect(self.select_wallpaper)
        layout.addWidget(self.wallpaper_button)
        layout.addWidget(QtWidgets.QLabel("透明度："))
        self.opacity_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.settings_manager.get_setting("opacity"))
        layout.addWidget(self.opacity_slider)
        self.countdown_date_label = QtWidgets.QLabel("倒计时日期和时间：")
        layout.addWidget(self.countdown_date_label)

        
        countdown_date_str = self.settings_manager.get_setting("countdown_date")
        countdown_date = QtCore.QDateTime.fromString(countdown_date_str, QtCore.Qt.ISODate)
        self.countdown_date_edit = QtWidgets.QDateTimeEdit(countdown_date)
        layout.addWidget(self.countdown_date_edit)

        save_button = QtWidgets.QPushButton("保存")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def select_wallpaper(self):
        options = QtWidgets.QFileDialog.Options()
        wallpaper_path, _ = QtWidgets.QFileDialog.getOpenFileName(self, "选择壁纸", "", "图像文件 (*.png *.jpg *.bmp)", options=options)
        if wallpaper_path:
            self.settings_manager.set_setting("wallpaper_path", wallpaper_path)

    def select_font_color(self):
        color = QtWidgets.QColorDialog.getColor(QtGui.QColor(self.settings_manager.get_setting("font_color")), self)
        if color.isValid():
            self.settings_manager.set_setting("font_color", color.name())

    def select_font(self):
        font_string = self.settings_manager.get_setting("font")
        font = QtGui.QFont()
        font.fromString(font_string)
        selected_font, ok = QtWidgets.QFontDialog.getFont(font, self)
        if ok:
            font_string = selected_font.toString()
            self.settings_manager.set_setting("font", font_string)
            self.text_edit.setFont(selected_font)
            self.font_changed.emit(selected_font)
            self.countdown_window.update_font(selected_font)

    def save_settings(self):
        text = self.text_edit.text()
        font_size = self.font_size_spinbox.value()
        opacity = self.opacity_slider.value()
        wallpaper_path = self.settings_manager.get_setting("wallpaper_path").replace("/", "\\")  
        self.settings_manager.set_setting("text", text)
        self.settings_manager.set_setting("font_size", font_size)
        self.settings_manager.set_setting("opacity", opacity)
        self.settings_manager.set_setting("wallpaper_path", wallpaper_path)  
        countdown_date = self.countdown_date_edit.dateTime().toPyDateTime()
        self.settings_manager.set_setting("countdown_date", countdown_date.isoformat())  
        self.settings_manager.save_settings()

        
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaper_path, 0)

        self.countdown_window.load_settings()
        self.closed.emit()



class TrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, app, settings_manager, countdown_window, parent=None):
        super().__init__(parent)
        self.app = app  
        self.settings_manager = settings_manager
        self.countdown_window = countdown_window
        self.setIcon(QtGui.QIcon(self.app.style().standardIcon(QtWidgets.QStyle.SP_FileIcon)))
        self.menu = QtWidgets.QMenu(parent)
        self.setContextMenu(self.menu)
        settings_action = QtWidgets.QAction("设置", self)
        settings_action.triggered.connect(self.show_settings_window)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        exit_action = QtWidgets.QAction("退出", self)
        exit_action.triggered.connect(self.quit_application)
        self.menu.addAction(exit_action)


    def show_settings_window(self):
        self.settings_window = SettingsWindow(self.settings_manager, self.countdown_window)
        self.settings_window.show()
        self.settings_window.closed.connect(self.reopen_countdown_window)

    def reopen_countdown_window(self):
        self.countdown_window.show()

    def quit_application(self):
        
        self.countdown_window.restore_original_wallpaper()
        QtWidgets.qApp.quit()

class SettingsManager:
    def __init__(self):
        self.original_wallpaper_path = self.get_original_wallpaper_path()
        self.settings_file = "settings.json"
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
                font_string = self.settings.get("font")
                if font_string:
                    if not isinstance(font_string, str):
                        font_string = QtGui.QFont().fromString(font_string).toString()
                        self.settings["font"] = font_string
                
                if "countdown_date" not in self.settings:
                    self.settings["countdown_date"] = QtCore.QDateTime.currentDateTime().toString(QtCore.Qt.ISODate)
        else:
            current_path = os.path.dirname(__file__)
            self.settings = {
                "text": "距离高考还有 %d 天 %h 小时 %m 分 %s 秒",
                "opacity": 100,
                "font_color": "#FFFFFF",
                "font_size": 16,
                "font": QtGui.QFont('Arial', 22).toString(),
                "wallpaper_path": current_path + "\\background.jpg",  # 默认壁纸路径
                "countdown_date": "2025-05-06T13:29:53"  # Default countdown date
            }
            self.save_settings()




    def get_original_wallpaper_path(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop") as key:
                value, _ = winreg.QueryValueEx(key, "Wallpaper")
                return value
        except FileNotFoundError:
            return ""

    def save_settings(self):
        if not isinstance(self.settings["font"], str):
            self.settings["font"] = self.settings["font"].toString()
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key):
        return self.settings.get(key)

    def set_setting(self, key, value):
        self.settings[key] = value

def main():
    app = QtWidgets.QApplication(sys.argv)
    settings_manager = SettingsManager()
    countdown_window = CountdownWindow(settings_manager)
    tray_icon = TrayIcon(app, settings_manager, countdown_window)
    tray_icon.show()
    countdown_window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
