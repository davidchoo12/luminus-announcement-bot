#!/usr/bin/env python3

from getpass import getpass
import json
import os
import re

while True:
  username = input("What's your NUSNET id? (eg nusstu\\e1234567). Ctrl+C to exit.\n")
  username_regex = re.compile(r"nusstu\\e\d{7}")
  match = username_regex.search(username)
  if match:
    break
  else:
    print("Invalid format, should be nusstu\\e followed by 7 digits. Try again. Ctrl+C to exit.")
password = getpass("What's your password? Ctrl+C to exit.\n")
while True:
  tg_id = input("What's your telegram id? Send /start to @getmyid_bot. Ctrl+C to exit.\n")
  tg_id_regex = re.compile(r"\d{6,}")
  match = username_regex.search(username)
  if match:
    break
  else:
    print("Invalid format, should be at least 6 digits. Try again. Ctrl+C to exit.")
token = input("What's your telegram bot token? Send /newbot to @BotFather. Ctrl+C to exit.\n")

path = os.path.join(os.path.dirname(__file__), "config.json")
json_file = open(path, "w")
json_file.write(json.dumps({"username": username, "password": password, "telegram_id": tg_id, "bot_token": token}))
print("Config saved to " + path)