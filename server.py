from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor
import os.path

log = 'chatlog.log'

class Client(Protocol):
	ip: str = None
	login: str = None
	factory: 'Chat'

	def __init__(self, factory): #инициализвция фабрики client
		self.factory = factory

	def connectionMade(self):  #оюработка подключения
		self.ip = self.transport.getHost().host
		self.factory.clients.append(self)

		print(f'[SERVER] Client connected:\nIP: {self.ip}\n')
		self.transport.write('Welcome to the Chat v0.1\n'.encode())
		if os.path.isfile(log):
			hist = open(log, 'r')
			chatlog = '-----[history]-----\n' + hist.read() + '-----[history]-----\n' #вывод истории
			self.transport.write(str(chatlog).encode())
			hist.close()

	def dataReceived(self, data: bytes): #обработка входящих данный
	
		msg = data.decode().replace('\n', '')

		if self.login != None: #проверка регистрации клиента
			newMsg = f'{self.login}: {msg}'
			self.factory.notify_all_users(newMsg)

			print(f'[CHAT] {newMsg}')

		elif msg.startswith('login:'): #проверка сообщения
			
			logins =[]
			for client in self.factory.clients:
				logins.append(client.login)

			if not msg.replace('login:', '') in logins: #проверка дубликата логина

				self.login = msg.replace('login:', '')

				notify = f'[SERVER] {self.login} connected to the server'

				self.factory.notify_all_users(notify) #регистрация
				print(notify)

		else:
			print('[SERVER] Error: Invalid client login')

	def connectionLost(self, reason=None): #обработка подключений

		notify = f'[SERVER] {self.login} disconnected'
		self.factory.notify_all_users(notify)

		self.factory.clients.remove(self)
		print(notify)


class Chat(Factory): #инициализация сервера
	clients: list

	def __init__(self):
		self.clients = []

		print('[SERVER] Starting')

	def startFactory(self): #ожидание клиентов

		print('[SERVER] Listening...')

	def buildProtocol(self, addr): #инициализация клиента

		return Client(self)

	def notify_all_users(self, data: str): #отправка сообщений в чат

		logfile = open(log, 'a') #логи
		logfile.write(data + '\n')
		logfile.close()

		for user in self.clients:
			user.transport.write(f"{data}\n".encode())


if __name__ == '__main__':
	reactor.listenTCP(2607, Chat())
	reactor.run()