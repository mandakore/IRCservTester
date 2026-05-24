import socket
import time
import unittest

PORT = 6667
HOST = '127.0.0.1'

class TestNetworkLayer(unittest.TestCase):

	def setUp(self):
		self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client.connect((HOST, PORT))
		self.client.settimeout(2.0)

	def tearDown(self):
		self.client.close()

	def test_basic_echo(self):
		"""通常の1行メッセージが正しくエコーされるか"""
		self.client.sendall(b"HELLO\r\n")
		response = self.client.recv(1024).decode('utf-8')
		self.assertEqual(response, "Server received: HELLO\r\n")

	def test_partial_send(self):
		"""メッセージが分割して到達した場合（パーシャルリード）のテスト"""
		self.client.sendall(b"PARTIAL ")
		time.sleep(0.1)
		self.client.sendall(b"MESSAGE\r\n")
		
		response = self.client.recv(1024).decode('utf-8')
		self.assertEqual(response, "Server received: PARTIAL MESSAGE\r\n")

	def test_multiple_messages(self):
		"""一度に複数行のメッセージが到達した場合のテスト"""
		self.client.sendall(b"MSG1\r\nMSG2\r\n")
		
		response = self.client.recv(1024).decode('utf-8')
		self.assertIn("Server received: MSG1\r\n", response)
		self.assertIn("Server received: MSG2\r\n", response)

	def test_multiple_clients(self):
		"""複数クライアントからの同時接続と送受信のテスト"""
		client2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client2.connect((HOST, PORT))
		client2.settimeout(2.0)

		# 1
		self.client.sendall(b"FROM CLIENT 1\r\n")
		# 2
		client2.sendall(b"FROM CLIENT 2\r\n")

		resp1 = self.client.recv(1024).decode('utf-8')
		resp2 = client2.recv(1024).decode('utf-8')

		self.assertEqual(resp1, "Server received: FROM CLIENT 1\r\n")
		self.assertEqual(resp2, "Server received: FROM CLIENT 2\r\n")

		client2.close()

if __name__ == '__main__':
	unittest.main()