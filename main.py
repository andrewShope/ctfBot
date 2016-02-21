from Game import Game
from IRC import IRC
from Bot import Bot

IRCObject = IRC(testing=True)
gameObject = Game(IRCObject)
pugBot = Bot(IRCObject, gameObject)

pugBot.updateTopic()
while True:
	pugBot.handle()