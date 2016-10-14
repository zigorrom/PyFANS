import sys
import time

from PyQt4.QtCore import (QCoreApplication, QObject, QRunnable, QThread,
                          QThreadPool, pyqtSignal)


# Subclassing QThread
# http://qt-project.org/doc/latest/qthread.html
class AThread(QThread):

    def run(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print("A Increasing")
            count += 1

# Subclassing QObject and using moveToThread
# http://blog.qt.digia.com/blog/2007/07/05/qthreads-no-longer-abstract
class SomeObject(QObject):

    finished = pyqtSignal()

    def long_running(self):
        count = 0
        while count < 5:
            time.sleep(1)
            print("B Increasing")
            count += 1
        self.finished.emit()

# Using a QRunnable
# http://qt-project.org/doc/latest/qthreadpool.html
# Note that a QRunnable isn't a subclass of QObject and therefore does
# not provide signals and slots.
class Runnable(QRunnable):
    def __init__(self,num):
        super().__init__()
        self.num = num

    def run(self):
        count = 0
        app = QCoreApplication.instance()
        while count < 5:
            print("{0}-C Increasing\n".format(self.num))
            time.sleep(self.num*0.5)
            count += 1
        app.quit()


def using_q_thread():
    app = QCoreApplication([])
    thread = AThread()
    thread.finished.connect(app.exit)
    thread.start()
    sys.exit(app.exec_())

def using_move_to_thread():
    app = QCoreApplication([])
    objThread = QThread()
    obj = SomeObject()
    obj.moveToThread(objThread)
    obj.finished.connect(objThread.quit)
    objThread.started.connect(obj.long_running)
    objThread.finished.connect(app.exit)
    objThread.start()
    sys.exit(app.exec_())

def using_q_runnable():
    app = QCoreApplication([])
    runnable1 = Runnable(1)
    runnable2 = Runnable(2)
    QThreadPool.globalInstance().start(runnable1)
    QThreadPool.globalInstance().start(runnable2)
    sys.exit(app.exec_())

if __name__ == "__main__":
    using_q_thread()
##    using_move_to_thread()
##    using_q_runnable()
