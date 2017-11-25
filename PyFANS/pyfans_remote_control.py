import sys
import qrcode
import pyqtgraph as pg
from PyQt4 import QtGui
from PIL import Image
from PIL.ImageQt import ImageQt


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

        #self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('Window')
        self.pix = PILimageToQPixmap(img)
        self.setPixmap(self.pix)

app = QtGui.QApplication(sys.argv)
imageLabel = ImageLabel()
imageLabel.show()
sys.exit(app.exec_())