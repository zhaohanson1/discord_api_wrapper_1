from enum import Enum
import json
from typing import Any, Optional
from dataclasses import dataclass
import websockets
import asyncio

class Opcode(Enum):
	DISPATCH = 0
	HEARTBEAT = 1
	IDENTIFY = 2
	PRESENCE_UPDATE = 3
	VOICE_STATE_UPDATE = 4
	RESUME = 6
	RECONNECT = 7
	REQUEST_GUILD_MEMBERS = 8
	INVALID_SESSION = 9
	HELLO = 10
	HEARTBEAT_ACK = 11

@dataclass
class Identify:
	token: str
	props: Any
	intents: int
	compress: bool = False
	large_threshold: int = 50
	shard: Any = None
	presence: Any = None

	def toPayload(self):
		data = {
			"token": self.token,
			"intents": self.intents,
			"properties": self.props,
			"compress": self.compress,
			"large_threshold": self.large_threshold
			}
		if self.shard:
			data["shard"] = self.shard
		if self.presence:
			data["presence"] = self.presence
		return Payload(2, data)
	

@dataclass
class Payload:
	opcode: int
	data: Any
	seq_num: Optional[int]=None
	name: Optional[str]=None

	@staticmethod
	def parsePayload(data, compression=False):
		o = json.loads(data)
		payload = Payload(o['op'], o['d'], o['s'], o['t'])
		return payload

	def toJson(self):
		d = {
			"op": self.opcode,
			"d": self.data,
			"s": self.seq_num,
			"t": self.name
			}
		return json.dumps(d)


class GatewayListener:
	def __init__(self, eventName: str, callback):
		self.eventName = eventName
		self.callback = callback

	async def receiveEvent(self, **kwargs):
		asyncio.create_task(self.callback(**kwargs))


class GatewayEventBus:
	def __init__(self):
		self.listeners = {}

	def addListener(self, event, listener):
		if event not in self.listeners:
			self.listeners[event] = set()
		self.listeners[event].add(listener)
		

	def removeListener(self, event, listener):
		if event not in self.listeners:
			return False
		if listener not in self.listeners[event]:
			return False
		self.listeners[event].remove(listener)

	async def emit(self, event, **kwargs):
		if event not in self.listeners:
			return False
		for listener in self.listeners[event]:
			asyncio.create_task(listener.receiveEvent(**kwargs))
		return True


class GatewayClient:

	def __init__(self):	
		self.last_seq = 0
		self.event_bus = GatewayEventBus()
		self.closed = True
		self.gateway_uri = 'wss://gateway.discord.gg/?v=9&encoding=json'

		self.user = None


		events = [self.on_message, self.on_connect]
		for e in events:
			lis = GatewayListener(e.__name__, e)
			self.event_bus.addListener(e.__name__, lis)

	async def on_connect(self):
		return

	async def on_message(self, message):
		return

	async def fire_event(self, event, **kwargs):
		asyncio.create_task(self.event_bus.emit(event, **kwargs))

	async def send_heartbeat(self, ws, heartbeat_interval):
		
		while True:
			heartbeat_payload = Payload(1, self.last_seq)
			print("Heartbeat: " + str(self.last_seq))
			asyncio.create_task(ws.send(heartbeat_payload.toJson()))
			await asyncio.sleep(heartbeat_interval)


	async def _connect(self, token: str):

		async with websockets.connect(self.gateway_uri) as ws:
			asyncio.create_task(self.fire_event("on_connect"))
			self.last_seq = 0
			self.closed = False
			init = True
			heartbeat_interval = None
			heartbeat_task = None
			session_id = None

			resuming = False
			
			arr = [0,9]
			intents = 1
			for i in arr:
				intents |= (1 << i)
			
			
			iden = Identify(token, {"$os": "windows"}, intents)
			id_payload = iden.toPayload().toJson()

			while not self.closed:
				data = await ws.recv()
				packet = Payload.parsePayload(data)
				
				if packet.seq_num:
					self.last_seq = packet.seq_num

				print("Opcode: " +str(packet.opcode))
				print("Name: " + str(packet.name))
				print("Seq num: " +str(packet.seq_num))
				print("Data: " + json.dumps(packet.data, indent=2))

				if init:
					init = False
					heartbeat_interval = packet.data['heartbeat_interval'] * 1e-3
					
					asyncio.create_task(ws.send(id_payload))
					heartbeat_task = asyncio.create_task(self.send_heartbeat(ws, heartbeat_interval))

				if packet.opcode == 0:
					if packet.name == "READY":
						session_id = packet.data['session_id']
						self.user =  packet.data['user']
					elif packet.name == "MESSAGE_CREATE":
						asyncio.create_task(self.fire_event("on_message", message=packet.data))
					elif packet.name == "RESUMED":
						resuming = False
				elif packet.opcode == 1:
					heartbeat_payload = Payload(1, self.last_seq)
					asyncio.create_task(ws.send(heartbeat_payload.toJson()))
				elif packet.opcode == 7:
					resuming = True
					resume_payload = Payload(6, {
						"token": token,
						"session_id": session_id,
						"seq": self.last_seq})
					asyncio.create_task(ws.send(resume_payload))
				elif packet.opcode == 9:
					if packet.data == False:
						self.closed = True
					await asyncio.sleep(5)
					asyncio.create_task(ws.send(id_payload))

				elif packet.opcode == 11:
					print("HEARTBEAT ACK")
				else:
					pass
			
			if heartbeat_task:
				heartbeat_task.cancel()

	def connect(self, token):
		return asyncio.run(self._connect(token))

	def close(self):
		self.closed = True
