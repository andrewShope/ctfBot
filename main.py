from Game import Game
from IRC import IRC
from Bot import Bot

IRCObject = IRC()
gameObject = Game(IRCObject)
pugBot = Bot(IRCObject, gameObject)

pugBot.updateTopic()
while True:
	pugBot.handle()