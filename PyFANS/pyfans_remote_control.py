import sys
import qrcode
import pyqtgraph as pg
from PyQt4 import QtGui
from PIL import Image
from PIL.ImageQt import ImageQt
import pyfans_v2 as pyf
from flask import Flask

qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data('https://www.google.com/')
qr.make(fit=True)

img = qr.make_image()
#img.show()

def PILimageToQImage(pilimage):
    """converts a PIL image to QImage"""
    imageq = ImageQt(pilimage) #convert PIL image to a PIL.ImageQt object
    qimage = QtGui.QImage(imageq) #cast PIL.ImageQt object to QImage object -that?s the trick!!!
    return qimage


def PILimageToQPixmap(pilimage):
    """converts a PIL image to QImage"""
    imageq = ImageQt(pilimage) #convert PIL image to a PIL.ImageQt object
    qpixmap = QtGui.QPixmap.fromImage(imageq)#cast PIL.ImageQt object to QImage object -that?s the trick!!!
    return qpixmap

def GetQImageFromPILimage(pil_image):
    
    return QtGui.QImage.loadFromData(pil_image, "PNG")


class ImageLabel(QtGui.QLabel):
    def __init__(self, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.setWindowTitle('Window')
        #self.pix = PILimageToQPixmap(img)
        #self.setPixmap(self.pix)

    def create_qr_code(self, text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image()
        self.pix = PILimageToQPixmap(img)
        self.setPixmap(self.pix)


class FANS_RemoteController:
    def __init__(self, fans_ui_controller = None):
        #assert isinstance(fans_ui_controller, pyf.FANS_UI_Controller)
        self.flask_app = Flask("FANS controller")
        self._app_thread = None
        self._test_var = "test_var"
        self.flask_app.add_url_rule("/", "index", self.index)

    def index(self):
        
        return self._test_var

    def create_remote_app(self):
        pass

    def run(self):
        self.flask_app.run(host = "0.0.0.0")
    

    

def test_ui():
    app = QtGui.QApplication(sys.argv)
    imageLabel = ImageLabel()
    imageLabel.create_qr_code("https://google.com/")
    imageLabel.show()
    return app.exec_()

def test_flask():
    ip = ""
    app = QtGui.QApplication(sys.argv)
    imageLabel = ImageLabel()
    imageLabel.create_qr_code(ip)
    imageLabel.show()
    app.exec_()
    
    c = FANS_RemoteController()
    c.run()

if __name__ == "__main__":
    #test_ui()
    test_flask()


