import sys
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtNetwork import QUdpSocket, QHostAddress, QTcpSocket
from PyQt5.QtCore import QThread
from threading import Thread
import socket
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal
#from LoginScreen import pencere
from PyQt5.QtWidgets import QListWidgetItem
import pickle
import time

qtCreatorFile = "vadap.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Sender():
    def __init__(self, name, port):
        # super().__init__()
        # QtCore.QThread.__init__(self)
        self.udp_port = port
        self.sock = QUdpSocket()
        self.remote_ip = QHostAddress('255.255.255.255')
        # self.remote_ip = QHostAddress('192.168.188.207')
        self.connected = False
        self.name = name

        self.sock.connectToHost(self.remote_ip, int(self.udp_port))
        self.sock.waitForConnected()
        flag = self.sock.isOpen()
        print(flag)
        self.connected = True
        print('Connected')

    def send(self, s):
        s = self.name + ': ' + s
        s = s.encode()
        self.sock.writeDatagram(s, self.remote_ip, int(self.udp_port))

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name


class Receiver(QObject):
    signal = pyqtSignal(str)

    def __init__(self, port):
        # super().__init__()
        QtCore.QObject.__init__(self)
        self.sock = QUdpSocket()
        self.udp_port = port
        self.sock.bind(int(self.udp_port))
        print('Connected to port: ' + str(self.udp_port))

        self.sock.readyRead.connect(self.receive)

    def receive(self):
        # print('Yes')
        message = '0'
        while self.sock.hasPendingDatagrams():
            message = self.sock.readDatagram(1000)
            # print(message)
            message = message[0].decode()
            print(message)
            self.signal.emit(message)
        return message

class ReceiverServer(QObject):
    signalServer = pyqtSignal(list)

    def __init__(self, port):
        # super().__init__()
        QtCore.QObject.__init__(self)
        self.sock = QUdpSocket()
        self.udp_port = port
        self.sock.bind(int(self.udp_port))
        print('Connected to port: ' + str(self.udp_port))

        self.sock.readyRead.connect(self.receive)

    def receive(self):
        # print('Yes')
        message = []
        while self.sock.hasPendingDatagrams():
            data_arr = self.sock.readDatagram(1000)
            message = pickle.loads(data_arr[0])
            print(message)
            self.signalServer.emit(message)
        return message


class TcpSender(QThread):
    signalServer = pyqtSignal(list)

    def __init__(self, port, ip):
        QtCore.QThread.__init__(self)
        self.ip = ip
        self.port = port
        self.BUFFER_SIZE = 1024
        self.hearth = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hearth.connect((ip, port))

    def run(self):
        while True:
            time.sleep(5.0)
            self.hearth.send(b'A')
            packet = self.hearth.recv(1040)
            upt = pickle.loads(packet)
            print(upt)
            self.signalServer.emit(upt)

class PrivateMessaging(QObject): #Request ip
    signal = pyqtSignal(str)

    def __init__(self, port, ip):
        QtCore.QObject.__init__(self)
        self.ip = ip
        self.port = port
        self.BUFFER_SIZE = 1024
        self.priv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.priv.connect((ip, port))

    def request(self, s):
        s = s.text()
        self.priv.send(s.encode())
        print(s)
        receiver_ip = self.priv.recv(1040)
        yes = receiver_ip.decode()
        print(receiver_ip.decode())
        self.signal.emit(yes)


class PrivateChat(QThread):
    signal = pyqtSignal(str)

    def __init__(self, port, ip, isReceiver, name):
        QtCore.QThread.__init__(self)
        self.name = name
        self.__ip = ip
        self.__port = port
        self.BUFFER_SIZE = 1024
        self.priv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if not isReceiver:
            self.priv.connect((self.__ip, self.__port))
        else:
            self.__ip = ''
            print('receiver')
            self.priv.bind((self.__ip, self.__port))
            self.priv.listen(1)
            self.priv, self.addr = self.priv.accept()

    def sendOwn(self, mesg):
        self.signal.emit(mesg.decode())

    def send(self, message):
        mes = self.name + ': ' + message
        self.priv.send(mes.encode())
        self.sendOwn(mes)

    def run(self):
        print('waiting')
        while True:
            mesg = self.priv.recv(self.BUFFER_SIZE)
            print('waited')
            if not mesg:
                self.priv.close()
                break
            self.sendOwn(mesg)

class PrivateWait(QThread):
    signal = pyqtSignal(str)

    def __init__(self, port):
        QtCore.QThread.__init__(self)
        self.ip = ''
        self.port = port
        self.BUFFER_SIZE = 1024
        self.wait = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.wait.bind((self.ip, self.port))
        self.wait.listen(1)

    def run(self):
        while True:
            conn, addres = self.wait.accept()
            data = conn.recv(200)
            print(data) #The ip address and name of someone wanting private chat
            self.signal.emit(data.decode())


class Vadap(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, ip):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self.mes = ''
        self.private_mes = ''
        #self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.hostname = socket.gethostname()
        self.IP = socket.gethostbyname(self.hostname)
        self.send = Sender(self.IP, 8842)
        #self.private_send = TcpSender(self.name)
        self.get = Receiver(8842)
        self.heart_beat = TcpSender(5006, ip)
        self.private_message = PrivateMessaging(5007, ip)
        self.wait_private = PrivateWait(5008)
        #self.serverGet = ReceiverServer(8850)
        self.widgetLayout = QtWidgets.QHBoxLayout()

        # self.send.start()
        # self.get.start()

        self.send_button.clicked.connect(self.sending)
        self.send_button2.clicked.connect(self.sending2)
        #self.send_button2.clicked.connect(self.sending2)
        self.get.signal.connect(self.receiving)
        #self.serverGet.signalServer.connect(self.receivingServer)
        self.listWidget.itemClicked.connect(self.priv_user)
        self.heart_beat.signalServer.connect(self.receivingServer)
        self.private_message.signal.connect(self.createChat)
        self.wait_private.signal.connect(self.createChat2)

        self.heart_beat.start()
        self.wait_private.start()

    @pyqtSlot(str)
    def createChat(self, ip):
        time.sleep(2)
        print('created')
        self.privChat = PrivateChat(5009, ip, False, self.send.getName())
        self.privChat.signal.connect(self.recPrivate)
        self.privChat.start()

    @pyqtSlot(str)
    def createChat2(self, ip):
        print('created2')
        self.privChat = PrivateChat(5009, ip, True, self.send.getName())
        self.privChat.signal.connect(self.recPrivate)
        self.privChat.start()

    def priv_user(self, s):
        self.private_message.request(s)

    def sending(self):
        self.mes = self.input_text.toPlainText()
        self.input_text.clear()
        self.send.send(self.mes)

    def sending2(self):
        self.private_mes = self.input_text2.toPlainText()
        self.input_text2.clear()
        self.privChat.send(self.private_mes)

    def giveName(self, name):
        self.send.setName(name)

    def addUser(self, names):
        #self.listWidget.addItem(names)
        self.listWidget.clear()
        for name in names:
            self.listWidget.addItem(name[1])

    @pyqtSlot(str)
    def receiving(self, message):
        # message_label = QtWidgets.QLabel()
        self.message_box_widget.append(message)
        # self.message_box.setWidget(message_label)

    @pyqtSlot(list)
    def receivingServer(self, names):
        self.addUser(names)

    @pyqtSlot(str)
    def recPrivate(self, mes):
        self.message_box_widget2.append(mes)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    # nam = input('Who are you: ')
    #log = pencere()
    #log.show()
    window = Vadap()
    window.show()
    sys.exit(app.exec_())