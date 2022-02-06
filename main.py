
"""

추가적으로 업데이트 되어야할 사항
예외처리
label표시
코드정리(필요없는 코드 삭제 및 합치기)
etc...

추가된 기능
북마크 (resume)
bbox없을 시 xml, image 삭제
last update : 22.02.04 by ysjo
"""

#import
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import xml.etree.ElementTree as ET

#전역변수
WIDTH = 1000
HEIGHT = 800
flag = False
dirName = "./a"
num = []
Resume_image = ".test.jpg"


class Thread(QThread):
    threadEvent_check = pyqtSignal(int)
    threadEvent_reset = pyqtSignal()
    threadEvent_exit = pyqtSignal()

    def __init__(self, parent, lbl):
        super().__init__(parent)
        self.parent = parent
        self.lbl = lbl
        self.power = True
        self.check = 0
        self.resume = 0

    def run(self):
        global dirName
        global flag
        global num
        global Resume_image
        #image dir
        image_dir = dirName+ "/image/"
        xml_dir =  dirName + "/xml/"

        #check dir exist
        if not os.path.isdir(image_dir):
            print("No image dir")

        if not os.path.isdir(xml_dir):
            print("No xml dir")

        #image file list
        image_list = os.listdir(image_dir)

        #for resume
        if os.path.isfile("resume.txt"):
            f = open("resume.txt", "r")
            Resume_image = f.readline()
            self.resume = 1
            f.close()

        for image in image_list:
            #resume
            if image == Resume_image and self.check == 0 and self.resume == 1:
                self.check = 1
                num = []
                image_file = image_dir + image
                xml_file = xml_dir + image[:-3] + "xml"
                qPixmapFileVar = self.loadImageFromFile(image_file)

                #draw rectangle
                self.painterInstance = QPainter(qPixmapFileVar)
                self.penRectangle = QPen(Qt.red)
                self.penRectangle.setWidth(1)
                self.painterInstance.setPen(self.penRectangle)

                number = self.parse_xml(xml_file,image_file)

                self.lbl.setPixmap(self.qPixmapFileVar)
                self.lbl.setAlignment(Qt.AlignCenter)
                while(self.power):
                    if flag is True:
                        self.threadEvent_check.emit(int(number))
                        self.parse_xml(xml_file,image_file, num)
                        break
                self.threadEvent_reset.emit()
                flag = False
                if self.power == False:
                    #exit thread
                    #for resume
                    f = open("resume.txt", "w")
                    f.write(image)
                    f.close()
                    break
            elif self.check == 0 and self.resume == 1:
                pass
            else:
                num = []
                image_file = image_dir + image
                xml_file = xml_dir + image[:-3] + "xml"
                qPixmapFileVar = self.loadImageFromFile(image_file)

                #draw rectangle
                self.painterInstance = QPainter(qPixmapFileVar)
                self.penRectangle = QPen(Qt.red)
                self.penRectangle.setWidth(1)
                self.painterInstance.setPen(self.penRectangle)

                number = self.parse_xml(xml_file,image_file)

                self.lbl.setPixmap(self.qPixmapFileVar)
                self.lbl.setAlignment(Qt.AlignCenter)
                while(self.power):
                    if flag is True:
                        self.threadEvent_check.emit(int(number))
                        self.parse_xml(xml_file,image_file, num)
                        break
                self.threadEvent_reset.emit()
                flag = False
                if self.power == False:
                    #exit thread
                    #for resume
                    f = open("resume.txt", "w")
                    f.write(image)
                    f.close()
                    break

        #done
        print("Done")
        qPixmapFileVar = self.loadImageFromFile("eyenix.png")
        self.lbl.setPixmap(self.qPixmapFileVar)
        self.lbl.setAlignment(Qt.AlignCenter)



    def loadImageFromFile(self,image_file):

        #QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load(image_file)
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(WIDTH, HEIGHT)
        print(image_file)
        return self.qPixmapFileVar

    def parse_xml(self,xml_file, image_file, num=[-1]):
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

        #delete if no label in here
        print(number)
        if len(num) >= number:
            print("Delete file",xml_file,image_file)
            os.remove(xml_file)
            os.remove(image_file)
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


        #delete resume file
        btn2 = QPushButton('Delete resume', self)
        btn2.setToolTip('This is a <b>delete resume information button</b> widget')
        btn2.move(1300, 850)
        btn2.resize(200,100)
        btn2.clicked.connect(self.delete_resume)

        ##status bar
        self.statusBar().showMessage('Ready')

        #QLabel - for loading image
        self.lbl = QLabel(self)
        self.lbl.setGeometry(30,30,WIDTH,HEIGHT)
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("eyenix.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(WIDTH,HEIGHT)
        self.lbl.setPixmap(self.qPixmapFileVar)
        self.lbl.setAlignment(Qt.AlignCenter)

        #button for save & next
        btn = QPushButton('SAVE & NEXT', self)
        btn.setToolTip('This is a <b>SAVE & Next button</b> widget')
        btn.move(30, HEIGHT + 50)
        btn.resize(WIDTH,100)
        btn.clicked.connect(self.flag)

        #for warning
        label1 = QLabel('체크하면 해당 라벨은 삭제됩니다.', self)
        label1.move(1200,30)
        label1.resize(300,20)

        #for thread
        self.x = Thread(self, self.lbl)

        #for checkbox(label)
        for i in range(0, 22):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(1200, 50 + i * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)
        for i in range(22, 40):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(1300, 50 + (i-22) * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)

        #for qthread signal
        self.x.threadEvent_check.connect(self.threadEventHandler_check)
        self.x.threadEvent_reset.connect(self.threadEventHandler_reset)
        self.x.threadEvent_exit.connect(self.threadEventHandler_exit)

        #for main GUI
        self.setWindowTitle('xml_tool')
        self.setWindowIcon(QIcon('eyenix.png'))
        self.setFixedSize(1600, 1000)
        self.center()
        self.show()

    def flag(self):
        global flag
        flag = True

    def delete_resume(self):
        if os.path.isfile("resume.txt"):
            os.remove("resume.txt")

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

    def threadEventHandler_exit(self):
        if self.x.isRunning():
            self.x.stop()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def pushButtonClicked(self):
        global dirName
        global Resume_image
        dirName = QFileDialog.getExistingDirectory(self, self.tr("Open Data files"), "./", QFileDialog.ShowDirsOnly)
        Resume_image = dirName
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