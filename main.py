#参考:https://fereria.github.io/reincarnation_tech/11_PySide/02_Tips/04_screen_shot/
import sys
from PySide2.QtWidgets import (QWidget, QApplication)
from PySide2.QtGui import (QPixmap, QPainter, QPainterPath, QColor, QBrush, QImage)
from PySide2.QtCore import (Qt, QRect, QBuffer, QPoint)
#import tkinter
import time
#import pyautogui
from PIL import Image
from PIL.ImageQt import ImageQt
import pyocr
import io

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
        self.stpos=QPoint(0,0)
        self.endpos=QPoint(rectSize.width(),rectSize.height())
        self.repaint()
    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        #p.setPen(Qt.NoPen)
        p.setPen(Qt.green)
        rectSize = QApplication.desktop().screenGeometry(self) #PySide2.QtCore.QRect
        pp = QPainterPath()
        pp.addRect(rectSize)
        pp.addRoundedRect(QRect(self.stpos, self.endpos), 0, 0)
        p.setBrush(QBrush(QColor(0, 0, 100, 100)))
        p.drawText(0, 0,500,500,0,"OCR")
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
        if  keynum == Qt.Key_Space: #enter
            self.screenShot()
        elif keynum == Qt.Key_Escape: #esc
            self.close()
    def mouseMoveEvent(self, event):
        self.endpos = event.pos()
        # マウスが動いたときに、再度描画処理を実行する
        self.repaint()
    def mousePressEvent(self, event):
        self.stpos = event.pos()
    def mouseReleaseEvent(self, event):
        self.endpos = event.pos()
    def resizeEvent(self, event):
        self.repaint()
    def moveEvent(self, event):
        self.repaint()
    def screenShot(self):
        screen = QApplication.primaryScreen()
        self.originalPixmap = screen.grabWindow(QApplication.desktop().winId())
        screen = QApplication.primaryScreen()
        windowgeometry = QRect(self.stpos, self.endpos) #PySide2.QtCore.QRect
        ratio=screen.devicePixelRatio()
        windowgeometry2 = QRect(windowgeometry.x()*ratio,windowgeometry.y()*ratio,windowgeometry.width()*ratio,windowgeometry.height()*ratio) #PySide2.QtCore.QRect
        pmap = self.originalPixmap.copy(windowgeometry2)
        #pmap.save("test1.png")
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