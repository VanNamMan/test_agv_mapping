
import socket
from threading import Thread
from PyQt5.QtCore import QObject, pyqtSignal

class Server(QObject):
    dataSignal = pyqtSignal(str)
    def __init__(self, host="localhost", port=8000) -> None:
        super().__init__()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.error = ""
        try:
            self.server.bind((host, port))
        except Exception as ex:
            self.error = str(ex)

        self._host = host
        self._port = port
        self._b_run = False

    def loop(self):
        while True:
            self.server.listen()
            conn, addr = self.server.accept()
            if self._b_run:
                Thread(target=self.recv_client, args=(conn, )).start()
            if not self._b_run:
                break

    def recv_client(self, conn:socket.socket):
        data:bytes = None

        data = conn.recv(1024)
        if data:
            self.dataSignal.emit(data.decode())
    
    def run(self):
        self._b_run = True
        Thread(target=self.loop).start()

    def stop(self):
        self._b_run = False

    def close(self) -> None:
        self.stop()
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((self._host, self._port))
        self.server.close()
