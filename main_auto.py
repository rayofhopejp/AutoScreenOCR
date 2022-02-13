#参考:https://fereria.github.io/reincarnation_tech/11_PySide/02_Tips/04_screen_shot/
import sys
from PySide2.QtWidgets import (QWidget, QApplication)
from PySide2.QtGui import (QPixmap, QPainter, QPainterPath, QColor, QBrush, QImage)
from PySide2.QtCore import (Qt, QRect, QBuffer, QPoint, QTimer)
#import tkinter
import time
#import pyautogui
from PIL import Image
from PIL.ImageQt import ImageQt
import pyocr
import io
import time
import signal
import imagehash

def checkifalmostsame(a,b):
    abuffer = QBuffer()
    abuffer.open(QBuffer.ReadWrite)
    a.save(abuffer, "PNG")
    a_pilim = Image.open(io.BytesIO(abuffer.data()))
    bbuffer = QBuffer()
    bbuffer.open(QBuffer.ReadWrite)
    b.save(bbuffer, "PNG")
    b_pilim = Image.open(io.BytesIO(bbuffer.data()))
    ahash = imagehash.average_hash(a_pilim)
    bhash = imagehash.average_hash(b_pilim)
    #print("hash",ahash-bhash)
    return abs( ahash - bhash ) < 3
class OCR():
    def __init__(self):
        engines = pyocr.get_available_tools()
        self.engine = engines[0]
        langs = self.engine.get_available_languages()
        #print("対応言語:",langs) # ['eng', 'jpn', 'osd']
    def run(self,image):
        # 画像の文字を読み込む
        #txt = engine.image_to_string(Image.open('test.png'), lang="jpn") # 修正点：lang="eng" -> lang="jpn"
        txt = self.engine.image_to_string(image, lang="jpn") # 修正点：lang="eng" -> lang="jpn"
        #image.save("test2.png")
        if len(txt)>0:
            print(txt.replace(" ", ""))
class ScreenShot(QWidget):

    def __init__(self, ocr,parent=None):

        super().__init__(parent)
        self.ocr=ocr
        #透明の背景
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        #inactiveに
        #self.setWindowState(self.windowState() & Qt.ApplicationInactive )
        #全画面に
        rectSize = QApplication.desktop().screenGeometry(self)
        self.setGeometry(rectSize)
        self.listpos=   []
        self.stpos=None
        self.endpos=None
        self.befpixs=[]
        self.beftimes=[]
        self.repaint()
        timer = QTimer(self)
        timer.timeout.connect(self.checkChange)
        timer.start()
    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        #p.setPen(Qt.NoPen)
        p.setPen(Qt.green)
        rectSize = QApplication.desktop().screenGeometry(self) #PySide2.QtCore.QRect
        pp = QPainterPath()
        pp.addRect(rectSize)
        for stpos,endpos in self.listpos:
            pp.addRoundedRect(QRect(stpos, endpos), 0, 0)
        p.setBrush(QBrush(QColor(0, 0, 100, 100)))
        #p.drawText(0, 0,500,500,0,"OCR")
        p.drawPath(pp)
        #ウィンドウの位置を取得
        #windowgeometry = self.geometry() #PySide2.QtCore.QRect
        #ratio=screen.devicePixelRatio()
        #windowgeometry2 = QRect(windowgeometry.x()*ratio,windowgeometry.y()*ratio,windowgeometry.width()*ratio,windowgeometry.height()*ratio) #PySide2.QtCore.QRect
        #rectSize = QApplication.desktop().screenGeometry(self) #PySide2.QtCore.QRect
        #p.drawPixmap(self.rect(),self.originalPixmap.copy(windowgeometry2))
        #print(windowgeometry2)
        p.end()
    #def mousePressEvent(self, event):
    #    self.screenShot()
    def keyPressEvent(self,event):
        keynum=event.key()
        #if  keynum == Qt.Key_Space: #space
        #    self.screenShot()
        if keynum == Qt.Key_Escape: #esc
            self.close()
        elif keynum == Qt.Key_Backspace: #backspace
            self.listpos.pop()
            self.beftimes.pop()
            self.befpixs.pop()
            self.repaint()
    def mouseMoveEvent(self, event):
        self.endpos = event.pos()
        self.listpos[-1] = (self.stpos,self.endpos)
        # マウスが動いたときに、再度描画処理を実行する
        self.repaint()
    def mousePressEvent(self, event):
        self.stpos = event.pos()
        self.listpos.append((self.stpos,self.stpos))
    def mouseReleaseEvent(self, event):
        self.endpos = event.pos()
        self.listpos[-1] = (self.stpos,self.endpos)
        self.beftimes.append(time.perf_counter())
        self.befpixs.append(None)
        self.repaint()
    def resizeEvent(self, event):
        self.repaint()
    def moveEvent(self, event):
        self.repaint()
    def checkChange(self):
        screen = QApplication.primaryScreen()
        self.originalPixmap=screen.grabWindow(QApplication.desktop().winId())
        ratio=screen.devicePixelRatio()
        for i in range(len(self.befpixs)):
            stpos,endpos=self.listpos[i]
            windowgeometry = QRect(stpos, endpos) #PySide2.QtCore.QRect
            windowgeometry2 = QRect(windowgeometry.x()*ratio,windowgeometry.y()*ratio,windowgeometry.width()*ratio,windowgeometry.height()*ratio) #PySide2.QtCore.QRect
            pmap = self.originalPixmap.copy(windowgeometry2)
            if self.befpixs[i] is None:
                self.befpixs[i]=pmap
                self.beftimes[i]=time.perf_counter()
                #print("befpixs[{}] is None".format(i))
            elif not checkifalmostsame(self.befpixs[i],pmap): #画面が変わった
                self.befpixs[i]=pmap
                self.beftimes[i]=time.perf_counter()
                #print("change[{}]".format(i))
            elif self.beftimes[i]==None: #すでにOCRした
                pass
            elif time.perf_counter() - self.beftimes[i] > 1.0: #2秒以上同じ画面
                #print(time.perf_counter() - self.beftimes[i])
                self.beftimes[i]=None
                self.ocrShot(pmap)
            
    def ocrShot(self,pmap):
        buffer = QBuffer()
        buffer.open(QBuffer.ReadWrite)
        pmap.save(buffer, "PNG")
        pil_im = Image.open(io.BytesIO(buffer.data()))
        self.ocr.run(pil_im)
        #self.close()
if __name__ == '__main__':
    ocr=OCR()
    app = QApplication(sys.argv)
    window = ScreenShot(ocr)
    window.show()
    sys.exit(app.exec_())