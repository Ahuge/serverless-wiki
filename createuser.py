#!/usr/bin/env python

import os
import bcrypt
import sys

username = sys.argv[1]
fullname = sys.argv[2]
password = sys.argv[3]
iterations = 10

nonce = os.environ['NONCE'].encode("utf-8")

def light_hash(pwd):
  r = 0
  for c in pwd:
    r = (r + ord(c)) % 100
  return r

def hash(pwd):
  pwd = pwd.encode("utf-8")
  salt = bcrypt.gensalt(10)
  first_hash = bcrypt.hashpw(pwd, salt)
  return bcrypt.hashpw(nonce + first_hash, salt).decode("utf-8")

print('{')
print('  full_name= "' + fullname + '"')
print('  password_light_hash= %d' % light_hash(password))
print('  password_hash= "' + hash(password) + '"')
print('}')
