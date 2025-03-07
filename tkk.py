"""
pyinstaller --noconsole --onefile --icon=soixam.png --add-data "soixam.png;."  tkk.py
"""

from PyQt5.QtWidgets import QApplication, QLabel, QSystemTrayIcon, QMenu, QAction,QTextEdit,QColorDialog,QInputDialog, QSlider,QPushButton,QDialog, QVBoxLayout
from PyQt5.QtGui import  QIcon,  QPainter, QColor, QKeyEvent,QTextCursor,QTextOption,QFontMetrics
from PyQt5.QtCore import Qt
import sys
import json
import os

class file_json:
    def __init__(self, file):
        self.file = file
        self.data1 = ''
    def read_json_file(self):
        try:
            with open(self.file, 'r', encoding='utf-8') as file:
                self.data = json.load(file)
                return self.data
        except (FileNotFoundError, json.JSONDecodeError):
            if os.path.exists(self.file):
                backup_path = self.file + ".bak"
                os.replace(self.file, backup_path)
            
            self.data = {}
            self.write_json_file()
            return self.data

    def write_json_file(self):
        with open(self.file, 'w', encoding='utf-8') as file:
            json.dump(self.data, file, indent=4, ensure_ascii=False)

class Read_file:
    def __init__(self,file_path):
        self.file_path = file_path
    def read_file(self):
        value = ''
        with open(self.file_path, 'r' , encoding="utf-8") as file:
            for line in file:
               value += line
        return value
        
    def write_file(self,data):
        with open(self.file_path, 'w') as file:
            file.write(f"{data}")
    
class TransparentWindow(QLabel):
    def link(self, link):
        folder = os.getcwd()#os.path.dirname(sys.executable)
        return os.path.join(folder, link)
    def __init__(self):
        super().__init__()
        self.lock1 = False
        self.file_data = self.link('data.txt')
        self.file_json = self.link('data.json')
    
        self.json = file_json(self.file_json)
        self.data_json = self.json.read_json_file()
        
        list = [["x", 0], ["y", 0], ["pin_to_top", True], ["r", 0], ["g", 255], ["b", 255], ["a", 1], ["color_r", 255], ["color_g", 255], ["color_b", 255], ["color_a", 1], ["size", 30]]
        
        for i in list:
            if i[0] not in self.data_json:
                self.data_json[f"{i[0]}"] = i[1]
                self.json.write_json_file() 
        
        self.data = ''
        
        try:
            o = Read_file(self.file_data)
            self.data =  o.read_file()
                
            if not self.data:
                self.data = 'not data'
                
        except FileNotFoundError:
            
            with open(self.file_data, "w", encoding="utf-8") as file:
                file.write("")
            self.data = 'not data'
        
        self.label = QLabel(self.data, self)
        self.label.setStyleSheet(f"""                
            font-size: {self.data_json['size']}px;
            color:rgba({self.data_json['color_r']}, {self.data_json['color_g']}, {self.data_json['color_b']}, {self.data_json['color_a']});
            padding: 0px;
            margin: 0px;
            border: none;
            
        """)
        
        QApplication.processEvents()
        
        width = self.get_longest_line(self.label, self.data)
        height = self.calculate_text_height(self.label, self.data)
        
        self.label.resize(width, height)
        self.resize(width+10, height)
        self.move(self.data_json['x'],self.data_json['y'])
        
        #khoi tao input
        self.input_box = QTextEdit(self)
        self.input_box.setStyleSheet(f"""
        color:rgba({self.data_json['color_r']}, {self.data_json['color_g']}, {self.data_json['color_b']}, {self.data_json['color_a']});
        font-size: {self.data_json['size']}px;
        border: none;
        outline: none;
        margin: 0px;
        padding: 0px 0px 0px,0px;
        background-color: rgba(100, 100, 100, 0); 
    """)
        
        QApplication.processEvents()        
        self.input_box.installEventFilter(self)
       #tat cuon input
        self.input_box.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_box.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.input_box.textChanged.connect(self.on_text_change)#nhan su kien thay doi text tron input
        self.input_box.hide()#hide
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.dragging = False
         
        
        if self.data_json['pin_to_top'] == False:
            self.unpin_from_top()
        else:
            self.unpin_from_top()
    def on_text_change(self):
        text = self.input_box.toPlainText()
        width = self.get_longest_line(self.input_box, text)
        height = self.calculate_text_height(self.input_box, text)
        self.resize(width+10, height)
        self.input_box.resize(width+10, height)
        self.label.resize(width, height)
        
        self.save_text()
        
    def get_longest_line(self, oj, data):
        lines = data.split('\n')
        max_width = oj.fontMetrics().boundingRect(lines[0]).width()
        for i in range(len(lines)):
            width = oj.fontMetrics().boundingRect(lines[i]).width()
            if width > max_width:
                max_width = width
        return  max_width
    def calculate_text_height(self, oj, data):
        total_line = len(data.split('\n'))
        size_font = QFontMetrics(oj.font()).lineSpacing()
        height = total_line * size_font
        return height
    
    def eventFilter(self, obj, event):
        if obj == self.input_box and event.type() == QKeyEvent.KeyPress:
            if event.key() == Qt.Key_Return and not event.modifiers() & Qt.ShiftModifier:
                width = self.get_longest_line(self.input_box, self.data)
                height = self.calculate_text_height(self.input_box, self.data)
                self.resize(width+10, height)
                self.input_box.resize(width+10, height)
                self.label.resize(width, height)
                
                self.input_box.hide()
                self.label.show()
                return True
        return super().eventFilter(obj, event)
    def save_text(self):
        text = self.input_box.toPlainText()
        self.label.setText(text if text else 'not data')    
        if not text:
            text = 'not data'
        try:
            o = Read_file(self.file_data)
            o.write(text)
        except:
            with open(self.file_data, "w", encoding="utf-8") as file:
                file.write(text)
        self.data = text
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setBrush(QColor(self.data_json["r"],self.data_json["g"],self.data_json["b"], self.data_json["a"]))
        painter.setPen(Qt.NoPen)
        painter.drawRect(self.rect())
        super().paintEvent(event)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.lock1 == False:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
        if event.button() == Qt.RightButton:
            self.showContextMenu(event.globalPos())
        
    def showContextMenu(self, position):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #333;  
                border: 1px solid #555;
            }
            QMenu::item {
                color: white;
                padding: 8px 20px;
                font-size:30px;
            }
            QMenu::item:selected { 
                background-color: #555;  /* Màu nền khi hover */
                color: yellow; /* Màu chữ khi hover */
            }
        """)
        
        action = QAction("edit text", self)
        action2 = QAction("color", self)
        action3 = QAction("size", self)
        action4 = QAction("background", self)
        action5 = QAction("alpha background", self)
        action6 = QAction("lock", self)
        exit_action = QAction("exit", self)
        
        action.triggered.connect(self.edit_text)
        if self.data_json['pin_to_top'] == True:
            action1 = QAction("unpin from top", self)
            action1.triggered.connect(self.unpin_from_top)
        else:
            action1 = QAction("pin to top", self)
            action1.triggered.connect(self.pin_to_top)
        action2.triggered.connect(self.change_color)
        action3.triggered.connect(lambda: self.change_size(position))
        action4.triggered.connect(self.change_background)
        # action5.triggered.connect(self.alpha_background(position))
        action5.triggered.connect(lambda: self.alpha_background(position))
        action6.triggered.connect(self.lock)
        exit_action.triggered.connect(QApplication.quit)
        
        menu.addAction(action)
        menu.addAction(action1)
        menu.addAction(action2)
        menu.addAction(action3)
        menu.addAction(action4)
        menu.addAction(action5)
        menu.addAction(action6)
        menu.addAction(exit_action)
        menu.exec_(position)

    def edit_text(self):
        
        self.input_box.setText(self.label.text())
        self.input_box.setWordWrapMode(QTextOption.NoWrap)
        self.input_box.document().adjustSize()

        self.input_box.show()
        self.label.hide()

        cursor = self.input_box.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.input_box.setTextCursor(cursor)
        self.input_box.setFocus()

    def unpin_from_top(self):
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()
        self.data_json['pin_to_top'] = False
        self.json.write_json_file()
        
    def pin_to_top(self):
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        self.show()
        self.data_json['pin_to_top'] = True
        self.json.write_json_file()
        
    def change_color(self):
        color = QColorDialog.getColor(initial=Qt.white, title="Chọn màu", parent=self)
        self.data_json["color_r"], self.data_json["color_g"], self.data_json["color_b"], a = color.red(), color.green(), color.blue(), color.alpha()
        self.json.write_json_file()
        r,g,b = self.data_json["color_r"], self.data_json["color_g"], self.data_json["color_b"]
        if color.isValid():
            current_style = self.label.styleSheet()
            new_style = current_style + f" color: rgba({r},{g},{b},1);"
            self.label.setStyleSheet(new_style)
            self.input_box.setStyleSheet(new_style)
    def change_size(self,position):
        
        x = position.x()
        y = position.y()
        
        dialog = QDialog()
        dialog.setWindowTitle("Chọn độ trong suốt")
        dialog.setGeometry(x, y, 300, 50)

        slider = QSlider(Qt.Horizontal, dialog)
        slider.setMinimum(10)
        slider.setMaximum(100)
        slider.setValue(self.label.font().pixelSize())
        slider.setGeometry(0,20,dialog.width()-10,20)
        
        size_min = QLabel('10', dialog) 
        size_min.setGeometry(0,0,20,10)
        
        size = QLabel(str(self.label.font().pixelSize()), dialog) 
        size.setGeometry(int((dialog.width()-10)/2),0,20,10)
        
        size_max = QLabel('100', dialog)
        size_max.setGeometry(dialog.width()-30,0,20,10)
        
        def update_size(value):
            self.data_json["size"] = value
            self.json.write_json_file()
            
            size.setText(str(value))
            size.adjustSize()
            self.update()
            
            style_label = self.label.styleSheet()
            style_input_box = self.input_box.styleSheet()
            new_style = f"""
                font-size: {value}px;
            """
            self.label.setStyleSheet(style_label + new_style)
            self.input_box.setStyleSheet(style_input_box + new_style)
            QApplication.processEvents()
            text = self.data
            width = self.get_longest_line(self.input_box, text)
            height = self.calculate_text_height(self.input_box, text)
            
            self.resize(width+10, height)
            self.input_box.resize(width+10, height)
            self.label.resize(width, height)
            
        slider.valueChanged.connect(update_size)       
        dialog.exec_()
    
    def change_background(self):
        color =  QColorDialog.getColor(initial=Qt.white, title="Chọn màu", parent=self)
        if color.isValid():
            self.data_json["r"], self.data_json["g"], self.data_json["b"], a = color.red(), color.green(), color.blue(), color.alpha()
    
    def alpha_background(self, position):
        x = position.x()
        y = position.y()
        
        dialog = QDialog()
        dialog.setWindowTitle("Chọn độ trong suốt")
        dialog.setGeometry(x, y, 300, 50)

        slider = QSlider(Qt.Horizontal, dialog)
        slider.setMinimum(1)
        slider.setMaximum(255)
        slider.setValue(self.data_json["a"])
        slider.setGeometry(0,20,dialog.width()-10,20)
        
        alpha_min = QLabel('1', dialog) 
        alpha_min.setGeometry(0,0,10,10)
        
        alpha = QLabel(str(self.data_json["a"]), dialog) 
        alpha.setGeometry(int((dialog.width()-10)/2),0,20,10)
        
        alpha_max = QLabel('255', dialog)
        alpha_max.setGeometry(dialog.width()-30,0,20,10)
        
        def update_alpha(value):

            self.data_json["a"]= value
            self.json.write_json_file()
            
            alpha.setText(str(value))
            alpha.adjustSize()
            self.update()
            
        slider.valueChanged.connect(update_alpha)       
        dialog.exec_()
    def lock(self, event):
        self.lock1 = True
    def mouseMoveEvent(self, event):
        if self.dragging and event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.offset)
        self.data_json['x'] = self.x()
        self.data_json['y'] = self.y()
        self.json.write_json_file()
    def mouseReleaseEvent(self, event):
        self.dragging = False
        
    def closeEvent(self, event):
        event.ignore()
        
class SystemTrayApp:
    def __init__(self, app, window):
        self.app = app
        self.window = window
        self.tray_icon = QSystemTrayIcon(QIcon("soixam.png"), parent=app)
        self.tray_icon.setToolTip("u")
        menu = QMenu()
        restore_action = QAction("Hiện cửa sổ", triggered=self.show_window)
        exit_action = QAction("Thoát", triggered=self.exit_app)
        menu.addAction(restore_action)
        menu.addAction(exit_action)
        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()
    def show_window(self):
        self.window.show()
    def exit_app(self):
        self.tray_icon.hide()
        self.app.quit()  
app = QApplication(sys.argv)
window = TransparentWindow()
tray_app = SystemTrayApp(app, window)
sys.exit(app.exec_())