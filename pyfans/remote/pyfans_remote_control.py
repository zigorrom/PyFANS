import sys
import time
import datetime
import qrcode
import json
import numpy as np
import pyqtgraph as pg
from PyQt4 import QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt
from flask import Flask, jsonify, request
from flask import render_template
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import socket

from PyQt4 import QtCore, QtGui, uic


# import  pyfans_v2 as pyf

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

def get_file(filename):
    with open(filename, "r") as file:
        return file.read()

class FANS_ControlWebView(FlaskForm):
    measurement_name = StringField("MeasurementName", validators=[DataRequired()])
    experiment_name = StringField("ExperimentName", validators=[DataRequired()])
    start_experiment = SubmitField("Start Experiment")



class FANS_RemoteController:
    def __init__(self, fans_ui_controller = None):
        #assert isinstance(fans_ui_controller, pyf.FANS_UI_Controller)
        self.flask_app = None # Flask("FANS controller")
        self._app_thread = None
        self._test_var = {"a":0, "b":1, "c":2} #"test_var"
        self._ip_addresses = None
        self._hostname = None
        
        self.initialize_list_of_ip_addresses() 
        self.app_thread = None # FlaskQThread(self.flask_app)

        #self.initialize_flask_app()

    @property
    def ip_addresses(self):
        return self._ip_addresses

    def index(self):
        # form  = FANS_ControlWebView()
        # return render_template("index.html", form = form)
        #content = get_file("index.html")
        #return content
        #string = json.dumps(self._test_var, indent=4)
        return jsonify(self._test_var)

    def data(self):
        a = np.arange(100).tolist()
        return jsonify(a)

    def initialize_flask_app(self):
        self.flask_app = Flask("FANS controller") 
        self.flask_app.config['SECRET_KEY'] = 'any secret string'
        self.flask_app.add_url_rule("/", "index", self.index)
        self.flask_app.add_url_rule("/data", "data", self.data)



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


class FANS_FlaskServerSignals(QtCore.QObject):
    sigServerStarted = QtCore.pyqtSignal()
    sigServetStopped = QtCore.pyqtSignal()
    sigRemoteEnabled = QtCore.pyqtSignal(bool)
    sigTextArrived = QtCore.pyqtSignal(str)


class FANS_FlaskServer(QtCore.QRunnable):
    def __init__(self, **kwargs):
        super().__init__()
        self._signals = FANS_FlaskServerSignals()
        self._ip_address = kwargs.get("ip_address")
        self._port = kwargs.get("port")
        self._flask_app = None
        self.init_server()

    def init_server(self):
        self._flask_app = Flask("FANS controller")  
        self._flask_app.config['SECRET_KEY'] = 'any secret string'
        self._flask_app.add_url_rule("/remote_enabled", "remote_enabled", self.on_remote_enabled)
        #self._flask_app.add_url_rule("/remote_enabled/<remote_enabled>", "remote_enabled", self.on_remote_enabled)
        self._flask_app.add_url_rule("/text", "text", self.on_text_arrived)
        #self._flask_app.add_url_rule("/text/<text>", "text", self.on_text_arrived)

    def on_remote_enabled(self):
        print("remote_requested")
        result = request.args.get("enabled")
        remote_enabled = result in ["True", "1"]
        self._signals.sigRemoteEnabled.emit(remote_enabled)
        return "Remote operation is set to: {0}".format(remote_enabled)

    def on_text_arrived(self):
        print("text_requested")
        text = request.args.get("text")
        self._signals.sigTextArrived.emit(text)
        return "Text Appended:\n {0}".format(text)

    @QtCore.pyqtSlot()
    def run(self):
        self._flask_app.run(host=self._ip_address, port=self._port)
        
    def shutdown(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()



mainViewBase, mainViewForm = uic.loadUiType("test.ui")
class FANS_UI_Remote(mainViewBase,mainViewForm):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setupUi()
        self._thread = QtCore.QThreadPool()
        self._server = FANS_FlaskServer(ip_address="0.0.0.0", port=5000)
        self._server._signals.sigTextArrived.connect(self.on_text_requested)
        self._server._signals.sigRemoteEnabled.connect(self.on_remote_enabled)
        self._thread.start(self._server)

    def setupUi(self):
        super().setupUi(self)

    def startServer(self):
        pass

    def stopServer(self):
        pass

    def restartServer(self):
        pass

    def on_text_requested(self, text):
        print("from UI: text requested")
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.ui_remote_text.appendPlainText(current_time)
        self.ui_remote_text.appendPlainText(text)

    def on_remote_enabled(self, enabled):
        print("from UI: remote enabled")
        self.ui_remote_enabled.setChecked(enabled)
    
    def closeEvent(self, event):
        self._server.shutdown()
        self._thread.waitForDone()




def test_ui_remote():
    app = QtGui.QApplication(sys.argv)
    wnd = FANS_UI_Remote()
    wnd.show()
    return app.exec_()



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
    else:
        return
    
    
    
    
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
    # test_flask()
    #test_ip_addresses()
    test_ui_remote()

