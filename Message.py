class Message(object):
	def __init__(self, msgText):
		self.type = msgText.split(" ")[1]
		self.raw = msgText.strip("\r\n")
		self.contents = ""
		self.badChars = [":", "@", "+"]

		if msgText.split(" ")[0].find("!") != -1:
			self.senderNick = msgText.split(" ")[0].split("!")[0]
			# Remove the preceding colon
			self.senderNick = self.senderNick[1:]
			# Remove any special character in front of ops
			if self.senderNick[0] in self.badChars:
				self.senderNick = self.senderNick[1:]

		if self.type == "PRIVMSG":
			self.contents = msgText.split(" ")[3][1:]
			self.destination = msgText.split(" ")[2]

		if self.type == "JOIN" or self.type == "PART":
			self.destination = msgText.split(" ")[2]

		if self.type == "353":
			# Make a string of where the names list begins to the end of message
			# We will need to remove more information from the end of the string
			# so we split it this way first
			self.names = msgText.split(" ")[5:]
			self.names = (" ").join(self.names)

			self.names = self.names.split(":")[1]
			self.names = self.names.strip("\r\n")
			self.names = self.names.split(" ")

			# Need to remove special characters that appear in front of ops
			for index, name in enumerate(self.names):
				if name[0] in self.badChars:
					self.names[index] = name[1:]