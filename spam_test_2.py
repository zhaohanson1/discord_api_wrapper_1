# goal: om message, repeat the message
import time
import sys
from BotClient import BotClient
from GatewayClient import GatewayClient

with open('token.txt', 'r') as f:
	bot_token = f.read()
	f.close()

b = BotClient(bot_token)

guilds = b.getCurrentUserGuilds()
g1id = guilds[0]['id']
ch = b.getGuildChannels(g1id)
general = None
for c in ch:
	if c['name'] == 'spam':
		general = c['id']
	

with open('sus.txt', 'r', encoding='utf-8') as f:
	sus = f.read()
	f.close()

class CustomClient(GatewayClient):

	async def on_connect(self):
		b.createMessage(general, sus + "\nREADY TO SUS")

	async def on_message(self, message):

		mentioned = True
		for users in message['mentions']:
			if users['id'] == self.user['id']:
				mentioned = True

		if mentioned and self.user['id'] != message['author']['id']:
			if 'sus' in message['content']:
				b.createMessage(message['channel_id'], sus + "\n SUS AMONG US")
			if message['content'] == "shutdown":
				self.close()


c = CustomClient()
c.connect(bot_token)