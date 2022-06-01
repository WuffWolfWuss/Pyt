import  socket
import pickle

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.server = "192.168.56.1"
        self.server = socket.gethostbyname(socket.gethostname())
        self.port = 5060
        self.addr = (self.server, self.port)
        self.pos = self.connect() #get player position 1st they connect to game
        print(self.pos)

    def getPos(self):
        return self.pos


    def connect(self):
        try:
            self.client.connect(self.addr)
            return pickle.loads(self.client.recv(2048*2))
        except:
            pass

    def send_data(self, data):
        try:
            self.client.send(pickle.dumps(data))
            return pickle.loads(self.client.recv(2048*2))
        except socket.error as e:
            print(e)
