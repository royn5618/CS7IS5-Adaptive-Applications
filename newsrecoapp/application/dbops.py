import sqlite3
conn = sqlite3.connect('database.db', check_same_thread=False)

from application import encryption
from django.contrib.auth.models import User
from django.contrib.auth.validators import ASCIIUsernameValidator

class UserOperations:
	def register(username, email, password):
		c = conn.cursor()

		# Encrypt Password
		encryptedPass = encryption.AESCipher.encode_string(password).decode("utf-8") 

		# Create table if doesn't exist)
		c.execute('''CREATE TABLE IF NOT EXISTS users(username text, email text, password text)''')

		# Insert a row of data
		c.execute("INSERT INTO users VALUES ('"+username+"','"+email+"','"+encryptedPass+"')")

		# Save (commit) the changes
		conn.commit()

		# We can also close the connection if we are done with it.
		# Just be sure any changes have been committed or they will be lost.
		#conn.close()
