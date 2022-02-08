
"""

추가적으로 업데이트 되어야할 사항
예외처리 (잘못 디렉토리 열었을 때 꺼지는 현상) etc,,
label수정 가능하도록?
코드정리(필요없는 코드 삭제 및 합치기)
global변수 제거
얼마나 진행되었는지 check용도
etc...

추가된 기능
북마크 (resume)
bbox없을 시 xml, image 삭제
last update : 22.02.07 by ysjo
"""

#import
import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import xml.etree.ElementTree as ET
import time

#전역변수
WIDTH = 2560 #1920
HEIGHT = 1440 #1080
TEXT = "None"
flag = False
before_flag = False
dirName = "./a"
num = []
Resume_image = ".test.jpg"
BOOK_MARK = False
TOTAL = 0
i = 0

class Thread(QThread):
    threadEvent_processbar = pyqtSignal(int)
    threadEvent_check = pyqtSignal(int)
    threadEvent_reset = pyqtSignal(int)
    threadEvent_exit = pyqtSignal()
    threadEvent_processbar_check = pyqtSignal(str)
    threadEvent_processbar_check2 = pyqtSignal()

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
        global before_flag
        global num
        global Resume_image
        global BOOK_MARK
        global TEXT
        global TOTAL
        #image dir
        self.image_dir = dirName+ "/image/"
        self.xml_dir =  dirName + "/xml/"

        #check dir exist
        if not os.path.isdir(self.image_dir):
            print("No image dir")

        if not os.path.isdir(self.xml_dir):
            print("No xml dir")

        #image file list
        self.image_list = os.listdir(self.image_dir)
        self.threadEvent_processbar.emit(int(len(self.image_list)))

        #for resume
        if os.path.isfile("resume.txt"):
            f = open("resume.txt", "r")
            Resume_image = f.readline()
            self.resume = 1
            f.close()

        while(self.power):
            for image in self.image_list:
                #resume
                if image == Resume_image and self.check == 0 and self.resume == 1:
                    self.check = 1
                    num = []
                    image_file = self.image_dir + image
                    xml_file = self.xml_dir + image[:-3] + "xml"
                    qPixmapFileVar = self.loadImageFromFile(image_file)

                    #draw rectangle
                    self.painterInstance = QPainter(qPixmapFileVar)
                    self.penRectangle = QPen(Qt.red)
                    self.penRectangle.setWidth(3)
                    self.painterInstance.setPen(self.penRectangle)

                    number = self.parse_xml(xml_file,image_file)
                    self.threadEvent_reset.emit(int(number))

                    self.lbl.setPixmap(self.qPixmapFileVar)
                    self.lbl.setAlignment(Qt.AlignCenter)
                    while(self.power):
                        if BOOK_MARK is True:
                            result = self.check_bookmark()
                            if result == True:
                                self.resume = 1
                                self.check = 0
                                Resume_image = TEXT
                                break
                            else:
                                BOOK_MARK = False
                        if flag is True:
                            self.threadEvent_check.emit(int(number))
                            time.sleep(0.1) #for sync global variable
                            self.parse_xml(xml_file,image_file,num)
                            TOTAL = TOTAL + 1
                            self.threadEvent_processbar_check.emit(str(image))
                            break
                    BOOK_MARK = False
                    #self.threadEvent_reset.emit()
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
                    image_file = self.image_dir + image
                    xml_file = self.xml_dir + image[:-3] + "xml"
                    qPixmapFileVar = self.loadImageFromFile(image_file)

                    #draw rectangle
                    self.painterInstance = QPainter(qPixmapFileVar)
                    self.penRectangle = QPen(Qt.red)
                    self.penRectangle.setWidth(3)
                    self.painterInstance.setPen(self.penRectangle)

                    number = self.parse_xml(xml_file,image_file)
                    self.threadEvent_reset.emit(int(number))

                    self.lbl.setPixmap(self.qPixmapFileVar)
                    self.lbl.setAlignment(Qt.AlignCenter)
                    while(self.power):
                        if BOOK_MARK is True:
                            result = self.check_bookmark()
                            if result == True:
                                self.resume = 1
                                self.check = 0
                                Resume_image = TEXT
                                break
                            else:
                                BOOK_MARK = False
                        if flag is True:
                            self.threadEvent_check.emit(int(number))
                            time.sleep(0.1)#for sync global variable
                            self.parse_xml(xml_file,image_file,num)
                            TOTAL = TOTAL + 1
                            self.threadEvent_processbar_check2.emit()
                            break
                    BOOK_MARK = False
                    #self.threadEvent_reset.emit()
                    flag = False
                    if self.power == False:
                        #exit thread
                        #for resume
                        f = open("resume.txt", "w")
                        f.write(image)
                        f.close()
                        break
            if self.check == 1:
                break

        #done
        print("Done")
        qPixmapFileVar = self.loadImageFromFile("eyenix.png")
        self.lbl.setPixmap(self.qPixmapFileVar)
        self.lbl.setAlignment(Qt.AlignCenter)

    def check_bookmark(self):
        image_list = os.listdir(self.image_dir)
        for image in image_list:
            if image == TEXT:
                print("pass")
                return True
        print("no that image")
        return False


    def loadImageFromFile(self,image_file):

        #QPixmap 객체 생성 후 이미지 파일을 이용하여 QPixmap에 사진 데이터 Load하고, Label을 이용하여 화면에 표시
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load(image_file)
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(int(WIDTH*0.75), int(HEIGHT*0.75))
        print(image_file)
        return self.qPixmapFileVar

    def parse_xml(self,xml_file, image_file, num = []):
        # parsing xml file in object inform
        tree = ET.parse(xml_file)
        root = tree.getroot()
        size = root.find('size')
        width = size.find('width').text
        height = size.find('height').text
        scaled_w = WIDTH*0.75 / float(width)
        scaled_h = HEIGHT*0.75 / float(height)
        objs = root.findall('object')
        number = 0
        if not num == [-1]:
            print("delete label:", num)
        for bboxs in objs:
            if number in num:
                root.remove(bboxs)
                number += 1
            else:
                box = bboxs.findall('bndbox')
                label = bboxs.find('name').text  #추후에 update label표시

                for k in box:
                    self.painterInstance.setPen(self.penRectangle)
                    x_min = float(k.find("xmin").text)
                    y_min = float(k.find("ymin").text)
                    x_max = float(k.find("xmax").text)
                    y_max = float(k.find("ymax").text)
                    self.painterInstance.drawRect(int(x_min * scaled_w), int(y_min * scaled_h), int((x_max - x_min) * scaled_w),
                                              int((y_max - y_min) * scaled_h))
                    self.painterInstance.setPen(QColor(0,0,255))
                    self.painterInstance.setFont(QFont('Arial',15))
                    self.painterInstance.drawText(QPoint(int(x_min * scaled_w)+1, int(((y_min * scaled_h)+(y_max * scaled_h))/2)), str(number)) #number
                    self.painterInstance.drawText(
                        QPoint(int(x_min * scaled_w), int(y_max * scaled_h)), str(label))  # class

                    number += 1

        self.painterInstance.end()
        tree.write(xml_file)

        #delete if no label in here
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
        self.image_list = 0
        ##MENU BAR
        loadingAction = QAction(QIcon('load.png'), 'load', self)
        loadingAction.setShortcut('Ctrl+L')
        loadingAction.setStatusTip('Load file')
        loadingAction.triggered.connect(self.pushButtonClicked)
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')
        filemenu.addAction(loadingAction)

        #bookmark
        label2 = QLabel('이동하고싶은 이미지 제목을 입력하시오.', self)
        label2.move(int(WIDTH*0.88), int(HEIGHT*0.8))
        label2.resize(int(WIDTH*0.12), int(HEIGHT*0.02))
        self.result = QLabel('', self)
        self.result.move(int(WIDTH*0.88), int(HEIGHT*0.85))
        self.result.resize(int(WIDTH*0.1), int(HEIGHT*0.05))
        self.bookmark_line = QLineEdit(self)
        self.bookmark_line.move(int(WIDTH*0.88), int(HEIGHT*0.82))
        self.bookmark_line.resize(int(WIDTH*0.1) ,int(HEIGHT*0.03))
        self.button = QPushButton(self)
        self.button.move(int(WIDTH*0.98), int(HEIGHT*0.82))
        self.button.setText('go')
        self.button.resize(int(WIDTH*0.02), int(HEIGHT*0.03))
        self.button.clicked.connect(self.button_event)

        #delete resume file
        btn2 = QPushButton('Delete resume', self)
        btn2.setToolTip('This is a <b>delete resume information button</b> widget')
        btn2.move(int(WIDTH*0.88), int(HEIGHT*0.88))
        btn2.resize(int(WIDTH*0.1), int(HEIGHT*0.05))
        btn2.clicked.connect(self.delete_resume)

        ##status bar
        self.statusBar().showMessage('Ready')

        #QLabel - for loading image
        self.lbl = QLabel(self)
        self.lbl.setGeometry(30, 30, int(WIDTH*0.75), int(HEIGHT*0.8))
        self.qPixmapFileVar = QPixmap()
        self.qPixmapFileVar.load("eyenix.png")
        self.qPixmapFileVar = self.qPixmapFileVar.scaled(int(WIDTH*0.75), int(HEIGHT*0.8))
        self.lbl.setPixmap(self.qPixmapFileVar)
        self.lbl.setAlignment(Qt.AlignCenter)

        #button for save & next
        btn = QPushButton('SAVE & NEXT', self)
        btn.setToolTip('This is a <b>SAVE & Next button</b> widget')
        btn.move(30, int(HEIGHT*0.85))
        btn.resize(int(WIDTH*0.75), int(HEIGHT*0.05))
        btn.clicked.connect(self.flag)

        #for warning
        label1 = QLabel('체크하면 해당 라벨은 삭제됩니다.', self)
        label1.move(int(WIDTH*0.8), 30)
        label1.resize(300,20)

        #for thread
        self.x = Thread(self, self.lbl)

        #for checkbox(label)
        for i in range(0, 22):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(int(WIDTH*0.8), 50 + i * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)
        for i in range(22, 40):
            globals()['self.cb_{}'.format(i)] = QCheckBox("label: " + str(i), self)
            globals()['self.cb_{}'.format(i)].move(int(WIDTH*0.9), 50 + (i-22) * 40)
            globals()['self.cb_{}'.format(i)].resize(100, 30)
        globals()['self.cb_all'] = QCheckBox("all deleted", self)
        globals()['self.cb_all'].move(int(WIDTH * 0.8), 50 + 23 * 40)
        globals()['self.cb_all'].resize(100, 30)

        #for progress bar
        self.pbar = QProgressBar(self)
        self.pbar.move(30, int(HEIGHT*0.91))
        self.pbar.resize(int(WIDTH*0.75), int(HEIGHT*0.02))

        #for qthread signal
        self.x.threadEvent_check.connect(self.threadEventHandler_check)
        self.x.threadEvent_processbar.connect(self.threadEventHandler_progress)
        self.x.threadEvent_reset.connect(self.threadEventHandler_reset)
        self.x.threadEvent_exit.connect(self.threadEventHandler_exit)
        self.x.threadEvent_processbar_check.connect(self.threadEventHandler_progress_check)
        self.x.threadEvent_processbar_check2.connect(self.threadEventHandler_progress_check2)

        #for main GUI
        self.setWindowTitle('xml_tool')
        self.setWindowIcon(QIcon('eyenix.png'))
        self.setFixedSize(WIDTH, HEIGHT)
        self.center()
        self.show()

    def button_event(self):
        global BOOK_MARK
        global TEXT
        TEXT = self.bookmark_line.text()  # line_edit text 값 가져오기
        self.result.setText(TEXT)
        BOOK_MARK = True

    def flag(self):
        global flag
        flag = True

    def before(self):
        global before_flag
        before_flag = True

    def delete_resume(self):
        if os.path.isfile("resume.txt"):
            os.remove("resume.txt")

    @pyqtSlot(int)
    def threadEventHandler_check(self, number):
        global num
        for i in range(0, number + 1):
            if globals()['self.cb_{}'.format(i)].isChecked() and i not in num:
                num.append(i)
            elif globals()['self.cb_{}'.format(i)].isChecked() and i in num:
                pass
            elif not globals()['self.cb_{}'.format(i)].isChecked() and i in num:
                num.remove(i)
            else:
                pass
        if globals()['self.cb_all'].isChecked():
            for i in range(0, number + 1):
                num.append(i)

    def threadEventHandler_progress_check(self,name):
        #progress bar
        global i
        image_dir = self.dir + "/image/"
        if self.image_list == 0:
            self.image_list = os.listdir(image_dir)
        i = 0
        for image in self.image_list:
            if image == name:
                print(i)
                self.pbar.setValue(i)
                break
            i += 1

    def threadEventHandler_progress_check2(self):
        #progress bar
        global i
        i += 1
        self.pbar.setValue(i)


    def threadEventHandler_reset(self, number):
        for i in range(0, 40):
            if(globals()['self.cb_{}'.format(i)].isChecked() == True):
                globals()['self.cb_{}'.format(i)].toggle()
            if(globals()['self.cb_all'].isChecked() == True):
                globals()['self.cb_all'].toggle()
        for i in range(0,number):
            globals()['self.cb_{}'.format(i)].setEnabled(True)
        for i in range(number,40):
            globals()['self.cb_{}'.format(i)].setEnabled(False)


    def threadEventHandler_progress(self,number):
        self.max = number
        self.pbar.setRange(0,self.max)

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
        self.dir = dirName
        Resume_image = dirName
        self.statusBar().showMessage(dirName)
        self.x.start()

    def mousePressEvent(self, e): # e ; QMouseEvent
        print("CLICK")

    def closeEvent(self, event):
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)

        if reply == QMessageBox.Yes:
            global TOTAL
            print("TOTAL: ",TOTAL)
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