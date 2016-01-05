import time
import socket

server = "irc.quakenet.org".encode()
channel = "#nactf.ql".encode()
botnick = "[nactf]".encode()
playerList = []

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
 					   "Type !w or !who to see who is currently added.")
		query(message.userName, helpMessage, socket)
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
	playerString = ""
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
				contents.encode() + b"\n")

def updateTopic(numPlayers, socket):
	socket.send(b"TOPIC " + channel + b" :\x02\x0304[\x0312CTF \x03\x02" +
		b"[\x02\x0303" + numPlayers.encode() + b"\x03\x02/\x03038\x03]" +
		b"\x02\x0304] [\x03\x02Welcome to #nactf.ql - Type !h for a list of " +
		b"commands.\x0304\x02]\x02\x03\n")

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
  	print("It is a PRIVMSG")
  	msgObject = Message(ircmsg)
  	print(msgObject.userName)
  	print(msgObject.contents)
  	playerList = messageHandler(msgObject, playerList, ircsock)

  ## If it's a parting message, make sure the user that left wasn't
  ## in our queue to play
  if ircmsg.split(" ")[1] == "PART":
  	if getUser(ircmsg) in playerList:
  		playerList.remove(getUser(ircmsg))
  		updateTopic(str(len(playerList)), ircsock)

  if ircmsg.find("PING :") != -1 or ircmsg.find("PONG") != -1: 
    ping(getID(ircmsg))

