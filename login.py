from PyQt5.uic import *
from PyQt5 import uic, QtWidgets, QtCore, QtGui
import sys
import socket,pickle
from test import Vadap
TCP_IP="192.168.188.74"
#TCP_IP = socket.gethostname()
TCP_PORT = 5005
BUFFER_SIZE = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))
Ui_MainWindow, QtBaseClass = uic.loadUiType("login.ui")


class pencere(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(pencere, self).__init__()
        loadUi("login.ui", self)
        self.user = b''
        self.password = b''
        self.setWindowTitle('title')
        self.loginButton.clicked.connect(self.tiklanma)


    def tiklanma(self):

        self.user = self.userInput.text()
        uzun = len(self.user)
        self.password = self.userPass.text()
        self.hostname = socket.gethostname()
        self.IP = socket.gethostbyname(self.hostname)
        message = str(uzun) + '/' + self.user + self.password +self.IP
        s.send(message.encode())


        data = s.recv(BUFFER_SIZE)
        data_arr = pickle.loads(data)


        if data_arr[0][0]== 0  and data_arr[0][1]!= 'false':
            print(data_arr)

            self.window().close()

            window2.giveName(self.user)
            window2.addUser(data_arr)
            window2.show()



        if data_arr[0][0] == 1:


            self.label_3.setText("KULLANICI ADI VEYA SİFRE YANLIS")


        #print(self.user,self.password)

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = pencere()
    window2 = Vadap(TCP_IP)
    window.show()
    sys.exit(app.exec_())


