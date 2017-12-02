import sys
import time
import qrcode
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
import pyfans_v2 as pyf
from flask import Flask
import socket

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
        self.flask_app = None # Flask("FANS controller")
        self._app_thread = None
        self._test_var = "test_var"
        self._ip_addresses = None
        self._hostname = None
        
        self.initialize_list_of_ip_addresses() 
        self.app_thread = None # FlaskQThread(self.flask_app)

        #self.initialize_flask_app()

    @property
    def ip_addresses(self):
        return self._ip_addresses

    def index(self):
        return """
        <!DOCTYPE html>
<head>
	<title>HTML and CSS "Hello World"</title>
	<style>		
		h1 {
			color: #C26356;
			font-size: 60px;
			font-family: Menlo, Monaco, fixed-width;
		}
	</style>
</head>
<body>
	<h1>Hello World Example</h1>
</body>
</html>
        """

        return self._test_var

    def initialize_flask_app(self):
        self.flask_app = Flask("FANS controller") 
        self.flask_app.add_url_rule("/", "index", self.index)

    def initialize_list_of_ip_addresses(self):
        hostname=socket.gethostname()   
        self._hostname, alias, self._ip_addresses = socket.gethostbyname_ex(hostname)
        #print(self._hostname)
        #print(self._ip_addresses)

    def run(self):
        self.flask_app.run(host = "0.0.0.0")
        
    def run_in_qthread(self):
        self.initialize_flask_app()
        self.app_thread = FlaskQThread(self.flask_app)
        self.app_thread.start()
        
    def stop_app(self):
        self.app_thread.terminate()
        

PORT = 5000


class FlaskQThread(QtCore.QThread):
    def __init__(self, flask_application, **kwargs):
        super().__init__(**kwargs)
        self.application = flask_application

    def run(self):
        self.application.run(host = "0.0.0.0", port = PORT)
        #self.application.run(host = "", port = PORT)

    def __del__(self):
        self.wait()



def test_ui():
    app = QtGui.QApplication(sys.argv)
    imageLabel = ImageLabel()
    imageLabel.create_qr_code("https://google.com/")
    imageLabel.show()
    return app.exec_()

#def getItem(self):
#    items = ("C", "C++", "Java", "Python")
		
#    item, ok = QtGui.QInputDialog.getItem(self, "select input dialog", 
#       "list of languages", items, 0, False)
	
#    if ok and item:
#       self.le.setText(item)

def test_flask():
    #ip = ""
    app = QtGui.QApplication(sys.argv)

    c = FANS_RemoteController()
    ip_addr = c.ip_addresses
    print("available ip addresses")
    print(ip_addr)
    c.run_in_qthread() 
    #qtapp.aboutToQuit.connect(webapp.terminate)
    app.aboutToQuit.connect(c.stop_app)

    imageLabel = ImageLabel()

    item, ok = QtGui.QInputDialog.getItem(imageLabel, "select input dialog", 
       "list of ip addresses", ip_addr, 0, False)

    if ok and item:
        imageLabel.create_qr_code("{0}:{1}".format(item, PORT))
        imageLabel.show()
        
    app.exec_()
    
    
    #c.get_list_of_ip_addresses()
    #c.run()
    
    
    #c.stop_app()

    #time.sleep(5)

    print("stopped")
    time.sleep(2)
    #print("started again")
    #c.run_in_qthread() 
    #time.sleep(10)
    #c.stop_app()
    #print("stopped")
   

def test_ip_addresses():
    import socket
    
    
    hostname=socket.gethostname()   
    hostname, alias, ipaddresses = socket.gethostbyname_ex(hostname)
    print(hostname)
    print(ipaddresses)
    IPAddr=socket.gethostbyname(hostname)   
    print("Your Computer Name is:"+hostname)   
    print("Your Computer IP Address is:"+IPAddr)  
    

    #import socket
    #print((([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["no IP found"])[0])


if __name__ == "__main__":
    #test_ui()
    test_flask()
    #test_ip_addresses()

