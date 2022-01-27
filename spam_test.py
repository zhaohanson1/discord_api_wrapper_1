# Goal: send 5 messages of your choice to general 3 secs
import time
import sys
from BotClient import BotClient

with f as open('token.txt', 'r'):
	bot_token = f.read()
	f.close()

def sendTrash(msgs):
	b = BotClient(bot_token)
	guilds = b.getCurrentUserGuilds()
	g1id = guilds[0]['id']
	ch = b.getGuildChannels(g1id)
	general = None
	for c in ch:
		if c['name'] == 'general':
			general = c['id']

	if not general:
		print("err")
		return None

	sent_msgs = []
	for m in msgs:
		res = b.createMessage(general, m)
		time.sleep(2)
		sent_msgs.append(res['id'])
	print(sent_msgs)
	for sm in sent_msgs:
		time.sleep(1.5)
		res = b.deleteMessage(general, sm)
		
	return None

if __name__ == '__main__':
	msgs = [
	"foo1",
	"foo3",
	"foo2",
	"foo4",
	"foo5"
	]
	
	sendTrash(msgs)