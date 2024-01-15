# user\user_model.py
import bcrypt

class User:
   def __init__(self, nome, email, password):
       self.nome = nome
       self.email = email
       self.password = password