from PyQt4 import uic
import pyfans.utils.ui_helper as uih

emailAuthBase, emailAuthForm = uic.loadUiType("UI/UI_email_auth.ui")
class EmailAuthForm(emailAuthBase, emailAuthForm):
    #email_cfg = "em.cfg"

    username = uih.bind("ui_login", "text", str)
    password = uih.bind("ui_password", "text", str)

    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender:
    email_cfg = "em.cfg"
    #message_format = """
    #From: {f}
    #To: {t}
    #Subject: {s}
    #{msg}
    #"""
    def __init__(self):
        self._server = ""
        self._my_address = ""
        self._login = ""
        self._password = ""
        self._login_successful = False
        
        with open("em.cfg") as cfg:
            self._server = cfg.readline().rstrip()
            self._my_address = cfg.readline().rstrip()

    def initialize(self, login, password):
        assert isinstance(login, str)
        assert isinstance(password, str)
        try:
            server = smtplib.SMTP(self._server)
            res_code, res_message = server.starttls()
            assert res_code == 220, "SMTP is not ready"
            res_code, res_message = server.login(login, password)
            assert res_code == 235, "Authentication unseccessful"
            res_code, res_message = server.quit()
            assert res_code == 221, "Quit error"
            self._login_successful = True
            self._login = login
            self._password = password
            print("email login successful")

        except Exception as e:
            print(str(e))
            self._login_successful = False
            print("email login failed")
        finally:
            return self._login_successful 

    def logoff(self):
        self._login_successful = False
        self._login = ""
        self._password = ""
        print("logoff successful")

    def send_message(self, subject, message):
        try:
            assert self._login_successful, "Initialize first"
            server = smtplib.SMTP(self._server)
            res_code, res_message = server.starttls()
            assert res_code == 220, "SMTP is not ready"
            res_code, res_message = server.login(self._login, self._password)
            assert res_code == 235, "Authentication unseccessful"
            res_code, res_message = server.mail(self._my_address)
            assert res_code == 250, "Sender FAILURE"
            res_code, res_message = server.rcpt(self._my_address)
            assert res_code == 250, "Sender FAILURE"

            my_address = self._my_address.format(login = self._login)
            msg = MIMEMultipart()
            msg['From'] = my_address
            msg['To'] = my_address
            msg['Subject'] = subject
            msg.attach(MIMEText(message))

            #message = self.message_format.format(f = self._my_address, t = self._my_address.format(login = self._login), s = subject, msg = message)
            message = msg.as_string()

            res_code, res_message = server.data(message)
            assert res_code == 250, "Message sending error"
            res_code, res_message = server.quit()
            assert res_code == 221, "Quit error"
            print("message is queued")
            return True
            
        except Exception as e:
            print(str(e))
            return False

        
