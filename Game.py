class Game(object):
	def __init__(self, IRC, teamSize = 8):
		self.players = []
		self.maxPlayers = teamSize
		self.IRC = IRC
		self.lastGameTime = None
		self.lastGamePlayers = []

	def addPlayer(self, playerName):
		if playerName in self.players:
			self.IRC.say("You're already added!")
			return 0
		else:
			self.players.append(playerName)
			return 1

	def removePlayer(self, playerName, notify=True):
		if playerName in self.players:
			self.players.remove(playerName)
			return 1
		elif notify:
			self.IRC.say("You weren't added!")
			return 0
		return 0

	def getPlayers(self):
		return self.players

	def reset(self):
		self.players = []

	def numPlayers(self):
		return len(self.players)