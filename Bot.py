import time

class Bot(object):
	def __init__(self, IRCObject, gameObject):
		self.IRC = IRCObject
		self.game = gameObject
		self.topicMessage = " - 2/15/16: !promote has been reimplemented"
		self.mumbleInfo = "Mumble: vx38.commandchannel.com Port: 31282"
		self.serverInfo = "steam://connect/74.91.122.157:27961"
		self.promoteFlag = 0
		self.promoter = ""

	def handle(self):
		message = self.IRC.receiveMessage()
		if message == "RECONNECT":
			self.game.reset()
			self.updateTopic()
			return 0

		msg = message.contents.lower()

		if message.type == "QUIT" or message.type == "PART":
			if self.game.removePlayer(message.senderNick, notify=False):
				self.updateTopic()

		if self.promoteFlag == 1:
			if self.IRC.updatingNames == False:
				self.promoteFlag = 0
				self.sendPromotions()

		if msg == "!a" or msg == "!add":
			if self.game.addPlayer(message.senderNick):
				self.updateTopic()
			if self.game.numPlayers() == self.game.maxPlayers:
				self.createGame()

		if msg == "!r" or msg == "!remove":
			if self.game.removePlayer(message.senderNick):
				self.updateTopic()

		if msg == "!w" or msg == "!who":
			if self.game.numPlayers() == 0:
				self.IRC.say("Noone is currently added.")
			else:
				whoString = "Currently added: "
				whoString += ", ".join(self.game.getPlayers())
				self.IRC.say(whoString)

		if msg == "!mumble":
			self.IRC.say(self.mumbleInfo)

		if msg == "!server":
			self.IRC.say(self.serverInfo)

		if msg == "!p" or msg == "!promote":
			self.IRC.getNames()
			self.promoteFlag = 1
			self.promoter = message.senderNick

		if msg == "!l" or msg == "!lastgame":
			if self.game.lastGameTime:
				timePassed = time.time() - self.game.lastGameTime
				timeString = makeTimeString(timePassed)
				timeString += " Players were: " + (", ").join(self.game.lastGamePlayers)
				self.IRC.notice(message.senderNick, timeString)
			else:
				self.IRC.notice(message.senderNick, 
								"No games since the bot last restarted.")


		if msg == "!h" or msg == "!help":
			self.IRC.notice(message.senderNick, ("Command list: !a/add " +
							"!r/remove !w/who !l/lastgame !p/promote " +
							"!mumble !server"))

	def updateTopic(self):
		topicString = self.makeTopicString()
		self.IRC.setTopic(topicString)

	def makeTopicString(self):
		numPlayers = self.game.numPlayers()
		topicString = ("\x02\x0304[\x0312CTF \x03\x02" +
		"[\x02\x0303" + str(numPlayers) + "\x03\x02/\x03038\x03]"
		"\x02\x0304] [\x03\x02Welcome to #nactf.ql - Type !h for a list of "
		"commands" + self.topicMessage + "\x0304\x02]\x02\x03")

		return topicString

	def createGame(self):
		announcement = "A new CTF game is ready to start! Players are "
		announcement += (", ").join(self.game.getPlayers())
		self.IRC.say(announcement)
		self.game.lastGameTime = time.time()
		self.game.lastGamePlayers = self.game.getPlayers()
		self.game.reset()
		self.updateTopic()

	def sendPromotions(self):
		names = self.IRC.names
		promoteString = (self.promoter + " wants you to add up! " +
						str(self.game.maxPlayers - self.game.numPlayers()) +
						" more players needed.")
		print(names)
		for name in names:
			if name == "Q" or name == self.IRC.botNick:
				pass
			else:
				self.IRC.notice(name, promoteString)

###
# Some Utility Functions
###

def makeTimeString(seconds):
	seconds = int(seconds)
	originalSeconds = seconds
	minutes, seconds = divmod(seconds, 60)
	hours, minutes = divmod(minutes, 60)
	days, hours = divmod(hours, 24)
	timeString = "The last game was "
	if days:
		timeString += str(days)
		if days == 1:
			timeString += " day "
		else:
			timeString += " days "
	if hours:
		timeString += str(hours)
		if hours == 1:
			timeString += " hour "
		else:
			timeString += " hours "
	if minutes:
		timeString += str(minutes)
		if minutes == 1:
			timeString += " minute "
		else:
			timeString += " minutes "
	if seconds:
		timeString += str(seconds)
		if seconds == 1:
			timeString += " second "
		else:
			timeString += " seconds "

	timeString += "ago."

	return timeString
