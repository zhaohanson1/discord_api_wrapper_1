from enum import Enum, auto
import urllib.error
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import json

from typing import Any

class Method(Enum):
	GET = auto()
	POST = auto()
	PUT = auto()
	DELETE = auto()

class ClientType(Enum):
	Bot = auto()
	OAuth = auto()


DISCORD_BASE = "https://discord.com"
DISCORD_API_VERSION = '9'
DISCORD_API = f"{DISCORD_BASE}/api/v{DISCORD_API_VERSION}"

def addParams(base_url, params):
	url = [base_url, "?"]
	for k,v in params.items():
		url.append(f"{k}={v}")
		url.append("&")
	url.pop()
	return "".join(url)

class Route:
	def __init__(self, method: str, path: str, **params: Any) -> None:
		self.method = method
		self.url = DISCORD_API + path
		# add params to url
		if params:
			self.url = addParams(self.url, params)

	def __str__(self):
		return "Route Object: " + self.method + " " + self.url

class HTTPClient:

	def __init__(self):
		pass

	def getHeaders(self):
		return {
			'Content-Type': 'application/json',
			'User-Agent': 'DiscordBot'
		}

	def request(self, route: Route, headers: dict={}, data: Any=None, payload: Any=None):
		try:
			h = self.getHeaders()
			h.update(headers)
			req = Request(route.url, data=data, headers=h, method=route.method)
			res = urlopen(req)
			v = res.read()
			obj = None
			if v:
				obj = json.loads(v)
		except urllib.error.HTTPError as e:
			obj = e.read().decode()
		return obj

	def getUser(self, user_id):
		return self.request(Route("GET", f"/users/{user_id}"))


	def getCurrentUser(self):
		return self.request(Route("GET", f"/users/@me"))


	def editCurrentUser(self):
		"""
		Modify the requester's user account settings.
		:params
			username?: string
			avatar?: image data
		:return 	user object on success.
		"""
		return self.request(Route("PATCH", f"/users/@me"))
	

	def getCurrentUserGuilds(self):
		"""
		Returns a list of partial guild objects the current user is a member of. 
		:params
			before: snowflake
			after: snowflake
			limit: integer
		:return 	Array[Guild Objects]
		"""
		return self.request(Route("GET", f"/users/@me/guilds"))


	def getCurrentUserGuildMember(self, guild_id):
		"""
		Returns a guild member object for the current user. 
		
		:return 	Guild Object
		"""
		return self.request(Route("GET", f"/users/@me/guilds/{guild_id}/member"))

	
	def leaveGuild(self, guild_id):
		"""
		:return 	204 empty response on success
		"""
		return self.request(Route("DELETE", f"/users/@me/guilds/{guild_id}"))


	def createDM(self):
		"""
		Create a new DM channel with a user. 
		:returns 	DM Channel object.
		"""
		return self.request(Route("POST", f"/users/@me/channels"))
		
	def getGuild(self, guild_id):
		"""
		:params
			Query String
				with_counts?: boolean
		:return 	Guild object
		"""
		return self.request(Route("GET", f'/guilds/{guild_id}'))


	def getGuildPreview(self, guild_id):
		"""
		:return 	Guild Preview object
		"""
		return self.request(Route("GET", f'/guilds/{guild_id}/preview'))


	def getGuildChannels(self, guild_id):
		"""
		Returns a list of guild channel objects. Does not include threads.
		:return 	Guild object
		"""
		return self.request(Route("GET", f'/guilds/{guild_id}/channels'))


	def getGuildMembers(self, guild_id):
		"""
		Returns a list of guild member objects that are members of the guild.
		:return 	Array[Guild member object]
		"""
		return self.request(Route("GET", f'/guilds/{guild_id}/members'))


	def getGuildMember(self, guild_id, user_id):
		"""
		Returns a guild member object for the specified user.
		:return 	Guild member object
		"""
		return self.request(Route("GET", f'/guilds/{guild_id}/members/{user_id}'))


	def modifyCurrentMember(self, guild_id, nick: str):
		"""
		Modifies the current member in a guild. 
		:params
			JSON
				nick:	string
		Returns a 200 with the updated member object on success.
		"""
		return self.request(Route("PATCH", f'/guilds/{guild_id}/members/@me'))

	def getChannel(self, channel_id):
		"""
		:return 	Channel object
		"""
		return self.request(Route("GET", f'/channels/{channel_id}'))


	def getChannelMessages(self, channel_id, around=None, before=None, limit=None):
		"""
		Returns the messages for a channel.
		The before, after, and around keys are mutually exclusive, 
			only one may be passed at a time.
		:params
			Query String
				around: snowflake
				before: snowflake
				after: snowflake
				limit: integer
		:return 	Array[Message objects]
		"""
		params = {}
		if around:
			params['around'] = around
		elif before:
			params['before'] = before
		elif limit:
			params['limit'] = limit
		
		return self.request(Route("GET", f'/channels/{channel_id}/messages', params=params))


	def createMessage(self, channel_id, message: str):
		"""
		Post a message to a guild text or DM channel.
		:return 	Message object
		"""
		s = {"content": message}
		data = json.dumps(s, ensure_ascii=False).encode('utf-8')
		return self.request(Route("POST", f'/channels/{channel_id}/messages'), data=data)


	def getChannelMessage(self, channel_id, message_id):
		"""
		Returns a specific message in the channel.

		:return 	Message object
		"""
		return self.request(Route("GET", f'/channels/{channel_id}/messages/{message_id}'))


	def editMessage(self, channel_id, message_id):
		"""
		Edit a previously sent message. The fields content, embeds, 
		and flags can be edited by the original message author. 
		:return 	Message object
		"""
		return self.request(Route("PATCH", f'/channels/{channel_id}/messages/{message_id}'))


	def deleteMessage(self, channel_id, message_id):
		"""
		Delete a message. 
		:return 	 204 empty response on success
		"""
		return self.request(Route("DELETE", f'/channels/{channel_id}/messages/{message_id}'))


	def getPinnedMessages(self, channel_id):
		"""
		Returns all pinned messages in the channel as an array of message objects.
		"""
		return self.request(Route("GET", f'/channels/{channel_id}/pins'))


	def pinMessage(self, channel_id, message_id):
		"""
		:return 	 204 empty response on success
		"""
		return self.request(Route("PUT", f'/channels/{channel_id}/pins/{message_id}'))


	def unpinMessage(self, message_id):
		"""
		:return 	 204 empty response on success
		"""
		return self.request(Route("DELETE", f'/channels/{channel_id}/pins/{message_id}'))


	def getGateway(self):
		"""
		Returns an object with a single valid WSS URL, which the client can use for Connecting. 
		Clients should cache this value and only call this endpoint to retrieve a new URL 
		if they are unable to properly establish a connection using the cached version of the URL.
		"""
		return self.request(Route("GET", '/gateway'))


	def getGatewayBot(self):
		"""
		Returns an object based on the information in Get Gateway, 
		plus additional metadata that can help during the operation of large or sharded bots. 
		Unlike the Get Gateway, this route should not be cached for extended periods of time 
		as the value is not guaranteed to be the same per-call, 
		and changes as the bot joins/leaves guilds.
		"""
		return self.request(Route("GET", '/gateway/bot'))