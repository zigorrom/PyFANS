from PyQt4 import QtCore, QtGui
import sys, signal, time
from ui_channelsettings import Ui_ChannelSettings

class ChannelSettings(QtGui.QDialog, Ui_ChannelSettings):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setupUi(self)

##        Load settings
    def load_dialod(self):
        pass
        
    


def main():
    app = QtGui.QApplication(sys.argv)
    window = ChannelSettings()
    window.show()
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()    
