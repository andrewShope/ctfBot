import time
import socket

server = "irc.quakenet.org".encode()
channel = "#nactf.ql".encode()
botnick = "[nactf]".encode()
playerList = []
lastGameTime = None
promoteFlag = 0
lastPlayers = []

class Message(object):
	def __init__(self, msgText):
		self.userName = msgText.split(":")[1].split("!")[0]
		self.messageType = msgText.split(" ")[1]
		self.destinationChannel = msgText.split(" ")[2]
		self.contents = msgText.split(":")[2]
		self.hostName = msgText.split("!")[1].split(" ")[0]

def ping(pingID): 
	ircsock.send(b"PONG :" + pingID.encode() +  b"\r\n")
	print("PONG :" + pingID)

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

	if lastPlayers:
		timeString += " Players were: " + ", ".join(lastPlayers)

	if originalSeconds < 10:
		timeString = "The game just started bruh, why are you already asking?"

	return timeString

def joinchan(chan): 
  ircsock.send(b"JOIN "+ chan + b"\n")

def hello(socket): 
  say("Hello", socket)

def getID(msg):
	"""
	This function takes in a PING message and strips it of the ID 
	so that we can send it back in our PONG
	"""
	msg = msg
	msgList = msg.split(':')
	return msgList[1]

def say(contents, socket):
 	socket.send(b"PRIVMSG " + channel + b" :" + contents.encode() + b"\n")

def messageHandler(message, players, socket):
	message.contents = message.contents.lower()
	if message.contents == "!a" or message.contents == "!add":
		players = addPlayer(message, players, socket)
		return players

	if message.contents == "!r" or message.contents == "!remove":
		return removePlayer(message, players, socket)

	if message.contents == "!w" or message.contents == "!who":
		print("IN WHO")
		print(players)
		playerString = ""
		if players:
			for index, player in enumerate(players):
				playerString += player
				if index != len(players) - 1:
					playerString += ", "
			say("Currently added: " + playerString, socket)
		else:
			say("Noone is currently added.", socket)
		return players

	if message.contents == "!h" or message.contents == "!help":
		helpMessage = ("Type !a or !add to add yourself to a game. "
					   "Type !r or !remove to remove yourself from a game. "
 					   "Type !w or !who to see who is currently added."
 					   "Type !l or !lastgame to see when the last game was played."
 					   "Type !p or !promote to query all players to add up."
 					   "To receive the address for the game server type !server"
 					   "and type !mumble to receive the mumble address.")
		query(message.userName, helpMessage, socket)
		return players

	if message.contents == "!l" or message.contents == "!lastgame":
		if lastGameTime:
			lastGame = makeTimeString(time.time() - lastGameTime)
			say(lastGame, socket)
		else:
			say("No games since the last time the bot restarted.", socket)
		return players
	# if message.contents == "!p" or message.contents == "!promote":
	# 	socket.send(b"NAMES "+ channel + b"\r\n")
	# 	global promoteFlag
	# 	promoteFlag = 1
	# 	return players
	if message.contents == "!server":
		say("/connect 74.91.122.157:27961", socket)
		return players
	if message.contents == "!mumble":
		say("Mumble: vx38.commandchannel.com Port: 31282", socket)
		return players
	else:
		return players


def addPlayer(message, playerList, socket):
	print(playerList)
	print("IN ADDED")
	if message.userName in playerList:
		say("You're already added!", socket)
		return playerList

	else:
		playerList.append(message.userName)
		updateTopic(str(len(playerList)), socket)
		if len(playerList) == 8:
			createGame(playerList, socket)
			updateTopic("0", socket)
			return []
		return playerList

def removePlayer(message, playerList, socket):
	if message.userName in playerList:
		playerList.remove(message.userName)
		updateTopic(str(len(playerList)), socket)
		return playerList

	else:
		say("You weren't added!", socket)
		return playerList

def createGame(playerList, socket):
	global lastPlayers
	lastPlayers = playerList
	playerString = ""
	global lastGameTime
	lastGameTime = time.time()
	for player in playerList:
		playerString += player
		playerString += " "

	say("New game ready to start! Players are: " + playerString, socket)
	for player in playerList:
		query(player, "CTF Game is ready to start!", socket)

def getUser(message):
	return message.split(":")[1].split("!")[0]

def query(userName, contents, socket):
	socket.send(b"PRIVMSG " + userName.encode() + b" :" + 
				contents.encode() + b"\r\n")

def updateTopic(numPlayers, socket):
	socket.send(b"TOPIC " + channel + b" :\x02\x0304[\x0312CTF \x03\x02" +
		b"[\x02\x0303" + numPlayers.encode() + b"\x03\x02/\x03038\x03]" +
		b"\x02\x0304] [\x03\x02Welcome to #nactf.ql - Type !h for a list of " +
		b"commands - 1/25/16: Added !mumble and !server\x0304\x02]\x02\x03\n")

def promoteGame(message, socket):
	outgoingMessage = "Add up! We need " + str(8-len(playerList)) + " more player(s)!"
	names = message.split(":")[2]
	namesList = names.split(" ")
	for name in namesList:
		name = name.strip('\n\r')
		if name[0] == "@":
			name = name[1:]
		if name == "Q" or name == botnick.decode():
			pass
		else:
			query(name, outgoingMessage, socket)
	global promoteFlag
	promoteFlag = 0

ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ircsock.connect((server, 6667))

# Wait for the server to send it's initial messages to signal
# to us that it is time to send user info
while True:
	ircmsg = ircsock.recv(2048)
	ircmsg = ircmsg.decode()
	ircmsg = ircmsg.strip('\n\r')
	print(ircmsg)
	if ircmsg.find('Found your hostname') != -1:
		print("Found")
		break

# Send nick info to IRC server
ircsock.send(b"NICK "+ botnick + b"\r\n") 
ircsock.send(b"USER "+ botnick + b" * 8" + b" :" + botnick +b"\r\n")

# Wait for the server to finish sending MOTD so that we can send
# the commands to join our channel
while True:
	ircmsg = ircsock.recv(2048)
	ircmsg = ircmsg.decode('ascii')
	ircmsg = ircmsg.strip('\n\r')
	print(ircmsg)
	if ircmsg.find("PING :") != -1:
		ping(getID(ircmsg))
	if ircmsg.find('End of /MOTD command.') != -1:
		print("End of MOTD")
		break

joinchan(channel)

# Once we join the channel we need to wait to get op. This loop will
# wait until that has been achieved
while True:
	ircmsg = ircsock.recv(2048)
	ircmsg = ircmsg.decode()
	ircmsg = ircmsg.strip('\n\r')

	# Check to see if we have a message giving us op yet
	if ircmsg.split(" ")[1] == "MODE" and ircmsg.split(" ")[3] == "+o":
		break

# Set the initial topic
updateTopic("0", ircsock)

# This is the main loop for the bot to operate in. Once here we
# are in the channel and have op status
while True: 
  ircmsg = ircsock.recv(2048) 
  ircmsg = ircmsg.decode()
  ircmsg = ircmsg.strip('\n\r') 
  print(ircmsg)

  ## This function will handle all of the logic of determining what 
  ## to do with each message
  if ircmsg.split(" ")[1] == "PRIVMSG":
  	msgObject = Message(ircmsg)
  	playerList = messageHandler(msgObject, playerList, ircsock)

  ## Check to see if this is a NAMES list
  if (botnick.decode() + " = " + channel.decode()) in ircmsg and promoteFlag == 1:
  	promoteGame(ircmsg, ircsock)

  ## If it's a parting message, make sure the user that left wasn't
  ## in our queue to play
  if ircmsg.split(" ")[1] == "PART" or ircmsg.split(" ")[1] == "QUIT":
  	if getUser(ircmsg) in playerList:
  		playerList.remove(getUser(ircmsg))
  		updateTopic(str(len(playerList)), ircsock)

  if ircmsg.find("PING :") != -1 or ircmsg.find("PONG") != -1: 
    ping(getID(ircmsg))

