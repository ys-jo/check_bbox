
"""

추가적으로 업데이트 되어야할 사항
resume기능 (책갈피 기능)
label표시

last update : 22.02.04 by ysjo
"""


import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import xml.etree.ElementTree as ET


WIDTH = 1000
HEIGHT = 800
flag = False
dirName = "./a"
num = []


class Thread(QThread):
    threadEvent_check = pyqtSignal(int)
    threadEvent_reset = pyqtSignal()

    def __init__(self, parent, lbl):
        super().__init__(parent)
        self.parent = parent
        self.lbl = lbl
        self.power = True

    def run(self):
        global dirName
        global flag
        global num

        #image dir
        image_dir = dirName+ "/image/"
        xml_dir =  dirName + "/xml/"
        #image file list
        image_list = os.listdir(image_dir)
        for image in image_list:
            num = []
            image_file = image_dir + image
            xml_file = xml_dir + image[:-3] + "xml"
            qPixmapFileVar = self.loadImageFromFile(image_file)

            #draw rectangle
            self.painterInstance = QPainter(qPixmapFileVar)
            self.penRectangle = QPen(Qt.red)
            self.penRectangle.setWidth(1)
            self.painterInstance.setPen(self.penRectangle)

            number = self.parse_xml(xml_file)

            self.lbl.setPixmap(self.qPixmapFileVar)
            self.lbl.setAlignment(Qt.AlignCenter)
            while(self.power):
                if flag is True:
                    self.threadEvent_check.emit(int(number))
                    self.parse_xml(xml_file, num)
                    break
            self.threadEvent_reset.emit()
            flag = False
            if self.power == False:
                break

    def loadImageFromFile(self,image_file):

        #QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load(image_file)
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(WIDTH, HEIGHT)
        print(image_file)
        return self.qPixmapFileVar

    def parse_xml(self,xml_file,num=[-1]):
        # parsing xml file in object inform
        tree = ET.parse(xml_file)
        root = tree.getroot()
        size = root.find('size')
        width = size.find('width').text
        height = size.find('height').text
        scaled_w = WIDTH / float(width)
        scaled_h = HEIGHT / float(height)
        objs = root.findall('object')
        number = 0
        for bboxs in objs:
            if number in num:
                root.remove(bboxs)
                number += 1
            else:
                box = bboxs.findall('bndbox')
                label = bboxs.find('name').text  #추후에 update label표시

                for k in box:
                    x_min = float(k.find("xmin").text)
                    y_min = float(k.find("ymin").text)
                    x_max = float(k.find("xmax").text)
                    y_max = float(k.find("ymax").text)
                    self.painterInstance.drawRect(x_min * scaled_w, y_min * scaled_h, (x_max - x_min) * scaled_w,
                                              (y_max - y_min) * scaled_h)
                    self.painterInstance.drawText(QPoint(x_min * scaled_w, y_min * scaled_h), str(number))

                    number += 1

        self.painterInstance.end()
        tree.write(xml_file)
        return number

    def stop(self):
        self.power = False
        # 멀티쓰레드를 종료하는 메소드
        self.quit()
        self.wait(3000)  # 3초 대기 (바로 안꺼질수도)

class MyApp(QMainWindow):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        ##MENU BAR
        loadingAction = QAction(QIcon('load.png'), 'load', self)
        loadingAction.setShortcut('Ctrl+L')
        loadingAction.setStatusTip('Load file')
        loadingAction.triggered.connect(self.pushButtonClicked)

        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(loadingAction)


        ##status bar
        self.statusBar().showMessage('Ready')

        self.lbl = QLabel(self)
        self.lbl.setGeometry(30,30,WIDTH,HEIGHT)
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("eyenix.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(WIDTH,HEIGHT)
        self.lbl.setPixmap(self.qPixmapFileVar)
        self.lbl.setAlignment(Qt.AlignCenter)

        btn = QPushButton('SAVE & NEXT', self)
        btn.setToolTip('This is a <b>SAVE & Next button</b> widget')
        btn.move(30, HEIGHT + 50)
        btn.resize(WIDTH,100)
        btn.clicked.connect(self.flag)

        label1 = QLabel('체크하면 해당 라벨은 삭제됩니다.', self)
        label1.move(1200,30)
        label1.resize(300,20)
        self.x = Thread(self, self.lbl)

        for i in range(0, 22):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(1200, 50 + i * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)
        for i in range(22, 40):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(1300, 50 + (i-22) * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)
        self.x.threadEvent_check.connect(self.threadEventHandler_check)
        self.x.threadEvent_reset.connect(self.threadEventHandler_reset)

        self.setWindowTitle('xml_tool')
        self.setWindowIcon(QIcon('eyenix.png'))
        self.setFixedSize(1600, 1000)
        self.center()
        self.show()

    def flag(self):
        global flag
        flag = True


    @pyqtSlot(int)
    def threadEventHandler_check(self, number):
        for i in range(0, number + 1):
            if globals()['self.cb_{}'.format(i)].isChecked() and i not in num:
                num.append(i)
            elif globals()['self.cb_{}'.format(i)].isChecked() and i in num:
                pass
            elif not globals()['self.cb_{}'.format(i)].isChecked() and i in num:
                num.remove(i)
            else:
                pass
        print("delete label:", num)

    def threadEventHandler_reset(self):
        for i in range(0, 40):
            if(globals()['self.cb_{}'.format(i)].isChecked() == True):
                globals()['self.cb_{}'.format(i)].toggle()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def pushButtonClicked(self):
        global dirName
        dirName = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)
        self.statusBar().showMessage(dirName)
        self.x.start()

    def mousePressEvent(self, e): # e ; QMouseEvent
        print("CLICK")

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # 멀티쓰레드를 종료하는 stop 메소드를 실행함
            if self.x.isRunning():
                self.x.stop()
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())