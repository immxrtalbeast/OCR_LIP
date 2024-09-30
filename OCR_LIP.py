import sys
import ast
import pytesseract
from PyQt5.QtGui import QFont
from googleapiclient.discovery import build
import creds
import httplib2
from oauth2client.service_account import ServiceAccountCredentials
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QMenuBar, QMenu, QFileDialog
import os, glob

sys.path.insert(0, '')


# Файл с ключом API у созданного Service Account
api_key = 'onyx-course-399120-a13c7a471ab1.json'


def get_service_simple():
    return build('sheets', 'v4', developerKey=creds.api_key)


def get_service_sacc():
    creds_json = "onyx-course-399120-a13c7a471ab1.json"
    scopes = ['https://www.googleapis.com/auth/spreadsheets']

    creds_service = ServiceAccountCredentials.from_json_keyfile_name(creds_json, scopes).authorize(httplib2.Http())
    return build('sheets', 'v4', http=creds_service)


sheet = get_service_sacc()
sheet_id = '1uQlPjK6SIPJnizXHmBVZ77fKfLFtVuCj2lYOCFu9Tbs'

pytesseract.pytesseract.tesseract_cmd = r'Tesseract-OCR\tesseract.exe'#C:\Program Files\Tesseract-OCR\tesseract.exe
config = r'--oem 3 --psm 6 '

a = [] #фамилии
b = [] #оценки
l = [] #для конфига

own_list = 'Свой список'

service = get_service_sacc()
sheet = service.spreadsheets()


class Window(QMainWindow):  # класс для работы внутри окна. В скобках указывать от какой функции наследуем всё
    def __init__(self):  # Конструктор
        super(Window, self).__init__()  # вызываем конструктор из класса В скобках выше

        # вырезаем всё из def application



        self.setWindowTitle('OCR_LIP')  # название окна. Был window. стал self потому что класс наследует из QMainWindow
        self.setGeometry(770, 400, 350, 200)  # разрешение окна

        self.text = QtWidgets.QLabel(self)  # создание переменной текста
        self.text.setText('Выберите файл')
        self.text.move(120, 100)
        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        self.text.setFont(font)
        self.text.adjustSize()  # калибровка ширины

        self.box = QtWidgets.QComboBox(self)
        self.box.addItem(own_list)
        self.box.move(123, 140)
        self.box.adjustSize()
        self.box.hide()

        self.sectext = QtWidgets.QLabel(self)  # создание переменной текста
        self.sectext.setText('Файл выбрал успешно! Выберите конфиг')
        self.sectext.setFont(font)
        self.sectext.move(30, 70)
        self.sectext.adjustSize()
        self.sectext.hide()

        self.but = QtWidgets.QPushButton(self)
        self.but.setText('Выбрать')
        self.but.move(122, 164)
        self.but.hide()
        self.but.clicked.connect(self.pressed)

        self.conf = QtWidgets.QLineEdit(self)
        self.conf.setGeometry(120, 50, 100, 20)
        self.conf.hide()

        self.preset = QtWidgets.QLineEdit(self)
        self.preset.setGeometry(120, 50, 100, 20)
        self.preset.hide()

        self.createMenuBar()

        self.conf_text = QtWidgets.QLabel(self)
        self.conf_text.setText('Вводите фамилии в поле по одной, нажимая "Ввести"')
        self.conf_text.move(20, 100)
        self.conf_text.adjustSize()
        self.conf_text.hide()

        self.preset_text = QtWidgets.QLabel(self)
        self.preset_text.setText('Вводите фамилии в поле по одной, нажимая "Ввести"')
        self.preset_text.move(20, 100)
        self.preset_text.adjustSize()
        self.preset_text.hide()

        self.dwn_preset_text = QtWidgets.QLabel(self)
        self.dwn_preset_text.setText('Введите название конфига,')
        self.dwn_preset_text.move(100, 80)
        self.dwn_preset_text.adjustSize()
        self.dwn_preset_text.hide()

        self.reload_text = QtWidgets.QLabel(self)
        self.reload_text.setText('далее перезагрузите приложение')
        self.reload_text.move(80, 100)
        self.reload_text.adjustSize()
        self.reload_text.hide()


        self.conf_but = QtWidgets.QPushButton(self)
        self.conf_but.setText('Ввести')
        self.conf_but.move(60, 164)
        self.conf_but.hide()
        self.conf_but.clicked.connect(self.conf_clicked)

        self.preset_but = QtWidgets.QPushButton(self)
        self.preset_but.setText('Ввести')
        self.preset_but.move(60, 164)
        self.preset_but.adjustSize()
        self.preset_but.hide()
        self.preset_but.clicked.connect(self.new_preset_clicked)

        self.preset_ready_but = QtWidgets.QPushButton(self)
        self.preset_ready_but.setText('Продолжить-->')
        self.preset_ready_but.move(160, 164)
        self.preset_ready_but.adjustSize()
        self.preset_ready_but.hide()
        self.preset_ready_but.clicked.connect(self.preset_ready_clicked)

        self.preset_dwn_but = QtWidgets.QPushButton(self)
        self.preset_dwn_but.setText('Загрузить')
        self.preset_dwn_but.move(160, 164)
        self.preset_dwn_but.adjustSize()
        self.preset_dwn_but.hide()
        self.preset_dwn_but.clicked.connect(self.preset_dwn_clicked)

        self.name_preset_but = QtWidgets.QPushButton(self)
        self.name_preset_but.setText('Ввести имя файла')
        self.name_preset_but.move(45, 164)
        self.name_preset_but.hide()
        self.name_preset_but.adjustSize()
        self.name_preset_but.clicked.connect(self.name_preset_create)

        self.ready_but = QtWidgets.QPushButton(self)
        self.ready_but.setText('Загрузить')
        self.ready_but.move(175, 164)
        self.ready_but.hide()
        self.ready_but.clicked.connect(self.ready_clicked)

        for filename in glob.glob('*.rtf'):
            with open(os.path.join(os.getcwd(), filename), 'r') as f:
                for line in f:
                    self.box.addItem(filename.removesuffix('.rtf'))


    def createMenuBar(self):
        self.menuBar = QMenuBar(self)
        self.setMenuBar(self.menuBar)

        self.fileMenu = QMenu("&Файл", self)
        self.menuBar.addMenu(self.fileMenu)

        self.SettingsMenu = QMenu("Настройки", self)
        self.menuBar.addMenu(self.SettingsMenu)

        self.SettingsMenu.addAction('&Создать конфиг', self.preset_clicked)

        self.fileMenu.addAction('&Открыть', self.action_clicked)


    @QtCore.pyqtSlot()
    def action_clicked(self):
        action = self.sender()
        if action.text() == '&Открыть':
            fname = QFileDialog.getOpenFileName(self)[0]
            data = pytesseract.image_to_data(fname, lang='train', config=config, output_type=pytesseract.Output.DICT)
            digit_rows = [row for row, text in enumerate(data["text"])]
            for row in digit_rows:
                text = data['text'][row]
                if text != '':
                    b.append(text)

            self.text.hide()
            self.box.show()
            self.sectext.show()
            self.but.show()
            self.menuBar.hide()

    def preset_clicked(self):
        action = self.sender()
        if action.text() == '&Создать конфиг':
            self.preset.show()
            self.preset_text.show()
            self.text.hide()
            self.preset_ready_but.show()
            self.preset_but.show()

    def new_preset_clicked(self):
        l.append(self.preset.displayText())
        self.preset.setText('')


    def preset_ready_clicked(self):
        self.preset.hide()
        self.preset_text.hide()
        self.preset_ready_but.hide()
        self.preset_but.hide()

        self.name_preset_but.show()


        self.dwn_preset_text.show()
        self.reload_text.show()
        self.preset.show()
        self.preset_dwn_but.show()


    def name_preset_create(self):
        self.name_of_conf = self.preset.displayText()
        self.preset.setText('')
        self.name_of_conf = str(self.name_of_conf)+'.rtf'
        print(self.name_of_conf)


    def preset_dwn_clicked(self):
        with open(self.name_of_conf, 'w') as name_preset:
            name_preset.write(str(l))
            name_preset.close()

        self.dwn_preset_text.hide()
        self.preset.hide()
        self.preset_dwn_but.hide()
        self.text.show()
        self.name_preset_but.hide()
        self.reload_app()

    def reload_app(self):
        QtCore.QCoreApplication.quit()
        status = QtCore.QProcess.startDetached(sys.executable, sys.argv)
        print(status)


    def pressed(self):
        if self.box.currentText() == own_list:
            self.names()
            self.box.hide()
            self.sectext.hide()
            self.but.hide()

        else:
            self.klass()
            self.box.hide()
            self.sectext.hide()
            self.but.hide()

    def names(self):
        self.conf.show()
        self.ready_but.show()
        self.conf_text.show()   
        self.conf_but.show()

    def conf_clicked(self):
        a.append(self.conf.displayText())
        self.conf.setText('')

    def ready_clicked(self):
        self.ready_but.hide()
        self.conf.hide()
        self.conf_text.hide()
        self.conf_but.hide()
        c = [list(y) for y in zip(a, b)]
        # отправляем данные в гугл таблицу
        resp = sheet.values().update(
            spreadsheetId=sheet_id,
            range='A1:C20',
            valueInputOption='RAW',
            body={'values': c}).execute()
        exit()

    def klass(self):
        with open(self.box.currentText()+'.rtf', 'r') as f:
            my_list = ast.literal_eval(f.read())
            for elem in my_list:
                a.append(elem)
                print(a)

        c = [list(y) for y in zip(a, b)]
        # отправляем данные в гугл таблицу
        resp = sheet.values().update(
            spreadsheetId=sheet_id,
            range='A1:C20',
            valueInputOption='RAW',
            body={'values': c}).execute()
        exit()


def application():
    app = QApplication(sys.argv)  # создает приложение
    window = Window()  # создает окно

    window.show()  # выводит окно на экран
    sys.exit(app.exec_())  # дефолт для нормального закрытия программы


if __name__ == "__main__":
    application()
