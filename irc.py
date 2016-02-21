import socket
import configparser
from Message import Message

class IRC(object):
    def __init__(self, testing=False):
        configHeading = "Bot Settings"
        if testing:
            configHeading = "Test Settings"
        config = configparser.RawConfigParser()
        config.read("botInfo.cfg")
        self.server = config.get(configHeading, "server").encode()
        self.channel = config.get(configHeading, "channel").encode()
        self.botNick = config.get(configHeading, "botNick").encode()
        self.updatingNames = False
        self.names = []

        self.connect()

    def connect(self):
        # Wait for the server to send it's initial messages to signal
        # to us that it is time to send user info

        self.ircsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ircsock.connect((self.server, 6667))

        while True:
            ircmsg = self.ircsock.recv(2048)
            ircmsg = ircmsg.decode()
            ircmsg = ircmsg.strip('\n\r')
            print(ircmsg)
            if ircmsg.find('Found your hostname') != -1:
                print("Found")
                break

        # Send nick info to IRC server
        self.send(b"NICK "+ self.botNick + b"\r\n") 
        self.send(b"USER "+ self.botNick + b" * 8" + b" :" + self.botNick +b"\r\n")

        # Wait for the server to finish sending MOTD so that we can send
        # the commands to join our channel
        while True:
            ircmsg = self.ircsock.recv(2048)
            ircmsg = ircmsg.decode('ascii')
            ircmsg = ircmsg.strip('\n\r')
            print(ircmsg)
            if ircmsg.find("PING :") != -1:
                self.ping(self.getPingID(ircmsg))
            if ircmsg.find('End of /MOTD command.') != -1:
                print("End of MOTD")
                break

        self.joinChannel(self.channel)

        # Once we join the channel we need to wait to get op. This loop will
        # wait until that has been achieved
        while True:
          ircmsg = self.ircsock.recv(2048)
          ircmsg = ircmsg.decode()
          ircmsg = ircmsg.strip('\n\r')

          # Check to see if we have a message giving us op yet
          if ircmsg.split(" ")[1] == "MODE" and ircmsg.split(" ")[3] == "+o":
              break

    def say(self, contents):
        self.send(b"PRIVMSG " + self.channel + b" :" + contents.encode() + b"\r\n")


    def query(self, userName, contents):
        self.send(b"PRIVMSG " + userName.encode() + b" :" + 
                contents.encode() + b"\r\n")

    def notice(self, userName, contents):
        self.send(b"NOTICE " + userName.encode() + b" :" +
                contents.encode() + b"\r\n")

    def send(self, contents):
        self.ircsock.send(contents)

    def ping(self, pingID):
        self.send(b"PONG :" + pingID.encode() +  b"\r\n")

    def joinChannel(self, channelName):
        self.send(b"JOIN "+ channelName + b"\r\n")

    def getPingID(self, msg):
        msgList = msg.split(':')
        return msgList[1]

    def receiveMessage(self):
        ircmsg = self.ircsock.recv(2048)
        ircmsg = ircmsg.decode()
        ircmsg = ircmsg.strip("\n\r")

        print(ircmsg)

        if ircmsg.find("PING :") != -1 or ircmsg.find("PONG") != -1: 
            self.ping(self.getPingID(ircmsg))

        messageObject = Message(ircmsg)

        if messageObject.type == "353":
            self.names = messageObject.names
            self.updatingNames = False

        if len(ircmsg) == 0:
            time.sleep(60)
            self.connect()
            return "RECONNECT"

        return messageObject

    def getNames(self):
        self.send(b"NAMES " + self.channel + b"\r\n")
        self.updatingNames = True

    def setTopic(self, topicMessage):
        self.send(b"TOPIC " + self.channel + b" :" + topicMessage.encode() + b"\r\n")


if __name__ == "__main__":
    IRCObject = IRC(testing=True)
    IRCObject.say("HELLO")
    while True:
        message = IRCObject.receiveMessage()
        if message.contents:
            textFile = open('log.txt', 'a')
            print(message.raw)
            textFile.write(message.raw)
            textFile.close()
