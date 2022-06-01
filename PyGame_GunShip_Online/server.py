import socket
from _thread import *
import sys
import pickle


PORT = 5060
FORMAT = "utf-8"

SERVER = socket.gethostbyname(socket.gethostname())   #get ip adress of this computer
ADDR = (SERVER, PORT)

staring_Pos = [[100, 200, 0, [], 10, ""], [800, 200, 1, [], 10, ""]]

#create socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
	server.bind(ADDR)
except socket.error as e:
	str(e)

def thread_client(conn, addr, player):
	global do_connect
	conn.send(pickle.dumps(staring_Pos[player])) #1st message send by server after connect succes

	while True:
		try:
			data = pickle.loads(conn.recv(2048*2)) #position of player will be send
			staring_Pos[player][0], staring_Pos[player][1], staring_Pos[player][4], staring_Pos[player][3] = data

			if not data:
				print("DISCONNECT!") #player dis
				break
			else:
				if player == 1:
					if staring_Pos[player][4] <= 0:
						staring_Pos[player][5] = 'RED WIN!'
						staring_Pos[0][5] = 'RED WIN!'
					reply = staring_Pos[0]
				else:
					if staring_Pos[player][4] <= 0:
						staring_Pos[player][5] = 'YELLOW WIN!'
						staring_Pos[1][5] = 'YELLOW WIN!'
					reply = staring_Pos[1]

				#print(f"[{addr}] {data}")
				#print(f"[Sending] {reply}")
			conn.sendall(pickle.dumps(reply))
		except:
			break
	print("CONNECTION LOSS")
	conn.close()

current_player = 0
server.listen(2) #start listen
print(f"[LISTENING] Server is listening on {SERVER}")
while True:
	conn, addr = server.accept()
	print(f"[ACTIVE CONNECTIONS:]", addr)

	start_new_thread(thread_client, (conn,addr,current_player))
	current_player += 1
