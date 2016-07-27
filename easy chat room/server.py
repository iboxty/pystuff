#!/usr/bin/env python
# -*- coding:utf-8 -*-
import socket,select,sys


SOCKET_LIST = []
BUF_SIZE = 1024  #设置缓冲区大小
PORT = 8888
HOST = '127.0.0.1'

def broadcast(server_sock, main_sock, message):
	for sock in SOCKET_LIST:
		if sock!=server_sock and sock!=main_sock:
			try:
				sock.send(message)
			except:
				sock.close()
				if sock in SOCKET_LIST:
					SOCKET_LIST.remove(sock)


def chat_server():
	server_addr = (HOST, PORT)  #IP和端口构成表示地址
	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  #生成一个新的socket对象
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #设置地址复用
	server.bind(server_addr)  #绑定地址
	server.listen(5)  #监听, 最大监听数为5

	SOCKET_LIST.append(server)

	while True:
		read_sockets, write_sockets, error_sockets = select.select(SOCKET_LIST, [], [])

		for sock in read_sockets:
			if sock == server:
				client, client_addr = server.accept()
				SOCKET_LIST.append(client)
				print 'Connected by', client_addr
				content = "[%s,%s] entered our chatting room\n" % client_addr
				broadcast(server, client, content)
			else:
				try:
					data = sock.recv(BUF_SIZE)
					if data:
						content = "\r" + '[' + str(sock.getpeername()) + '] ' + data
						broadcast(server, sock, content)
					else:
						if sock in SOCKET_LIST:
							SOCKET_LIST.remove(sock)
						content = '[' + str(sock.getpeername()) + '] is offline'
						sock.close()
						broadcast(server, sock, content + "\n")
						print content


				except:
					if sock in SOCKET_LIST:
						SOCKET_LIST.remove(sock)
					content = '[' + str(sock.getpeername()) + '] is offline'
					broadcast(server, sock, content + "\n")
					print content
					sock.close()

	server.close()

if __name__ == "__main__":
	sys.exit(chat_server())