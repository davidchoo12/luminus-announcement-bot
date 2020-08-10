#!/usr/bin/env python3

import urllib.parse as parse
from html2text import HTML2Text
import requests
import json
import logging
import os
from datetime import datetime, timedelta

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s %(message)s",
    filename=os.path.join(os.path.dirname(__file__), "luminus-anncouncement-bot.log"),
    level=logging.INFO)

OCP_SUBSCRIPTION_KEY = "6963c200ca9440de8fa1eede730d8f7e"

config_file = open(os.path.join(os.path.dirname(__file__), "config.json"), "r")
config = json.loads(config_file.read())

h2t = HTML2Text()
h2t.body_width = 0 # dont wrap, see https://github.com/Alir3z4/html2text/blob/master/docs/usage.md#command-line-options

def auth_jwt():
    try:
        token_file = open(os.path.join(os.path.dirname(__file__), "jwt.txt"), "r+")
    except FileNotFoundError:
        token_file = open(os.path.join(os.path.dirname(__file__), "jwt.txt"), "w+")
    token_file_lines = token_file.read().splitlines()
    if len(token_file_lines) == 2 and datetime.fromisoformat(token_file_lines[1]) + timedelta(seconds=86400) > datetime.now():
        logging.info("Use saved jwt")
        return token_file_lines[0]

    if "username" not in config or "password" not in config:
        logging.error("Username and password not yet configured. Run config.py first.")
        exit(1)
    username = config["username"]
    password = config["password"]

    AUTH_URL = "https://vafs.nus.edu.sg/adfs/oauth2/authorize"
    CLIENT_ID = "E10493A3B1024F14BDC7D0D8B9F649E9-234390"
    REDIRECT_URI = "https://luminus.nus.edu.sg/auth/callback"
    RESOURCE = "sg_edu_nus_oauth"

    auth_params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "resource": RESOURCE,
    }

    auth_data = {
        "UserName": username,
        "Password": password,
        "AuthMethod": "FormsAuthentication",
    }

    auth_headers = {"Content-Type": "application/x-www-form-urlencoded"}

    # https://vafs.nus.edu.sg/adfs/oauth2/authorize?response_type=code&client_id=E10493A3B1024F14BDC7D0D8B9F649E9-234390&redirect_uri=https%3A%2F%2Fluminus.nus.edu.sg%2Fauth%2Fcallback&resource=sg_edu_nus_oauth
    url = AUTH_URL + "?" + parse.urlencode(auth_params)
    response = requests.post(url, headers=auth_headers, data=auth_data)

    if len(response.history) != 2:
        logging.error("Invalid credentials")
        exit(1)

    resp1, resp2 = response.history

    # get the code found in the query parameters of
    # the location header of second response
    decoded = parse.urlparse(resp2.headers["Location"])
    code = dict(parse.parse_qsl(decoded.query))["code"]

    adfs_body = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": code,
    }
    api_login_url = "https://luminus.nus.edu.sg/v2/api/login/adfstoken"

    login_headers = {
        "Ocp-Apim-Subscription-Key": OCP_SUBSCRIPTION_KEY,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    token_resp = requests.post(url=api_login_url, data=adfs_body, headers=login_headers)
    print(token_resp.json())
    access_token = token_resp.json().get("access_token")
    now = datetime.now().isoformat()
    token_file.seek(0)
    token_file.write("{}\n{}".format(access_token, now))
    return access_token

def api(method, path):
    API_BASE_URL = "https://luminus.azure-api.net/"

    headers = {
        "Authorization": "Bearer {}".format(auth_jwt()),
        "Ocp-Apim-Subscription-Key": OCP_SUBSCRIPTION_KEY,
        "Content-Type": "application/json",
    }

    # NOTE remove leading / else joined url is broken
    uri = parse.urljoin(API_BASE_URL, path.rstrip("/"))
    # method = requests.get

    response = method(uri, headers=headers)

    status_code = response.status_code
    if status_code == 200:
        try:
            logging.debug(response.json())
            return response.json()
        except Exception as e:
            logging.error(e)
            exit(1)
    elif status_code == 401:
        logging.error("expired token")
        exit(1)
    else:
        logging.error(response.content)
        exit(1)

if __name__ == "__main__":
    announcements = api(requests.get, "announcement/Unread")["data"]
    try:
        annc_sent_file = open(os.path.join(os.path.dirname(__file__), "announcements_sent.txt"), "r+")
    except FileNotFoundError:
        annc_sent_file = open(os.path.join(os.path.dirname(__file__), "announcements_sent.txt"), "w+")
    annc_sent_ids = [annc_id.strip() for annc_id in annc_sent_file.read().splitlines()]

    any_sent = False
    for annc in announcements:
        a_id = annc["id"]
        if a_id in annc_sent_ids:
            continue
        mod_id = annc["parentID"]
        mod = api(requests.get, "module/" + mod_id)
        message_args = {
            "mod_code": mod["name"],
            "a_title": annc["title"],
            "a_desc": h2t.handle(annc["description"]),
            "mod_name": mod["courseName"],
            "a_url": "https://luminus.nus.edu.sg/modules/{}/announcements/active/{}".format(mod_id, a_id)
        }
        # multiline string considers indentation as spaces, so don't indent
        message = """{mod_code} {mod_name}

{a_title}

{a_desc}
{a_url}""".format(**message_args)
        resp = requests.post("https://api.telegram.org/bot{}/sendMessage".format(config["bot_token"]), json={"chat_id": config["telegram_id"], "text": message})
        if resp.json()["ok"]:
            any_sent = True
            annc_sent_ids.append(a_id)
            logging.info("Sent to telegram {mod_code}: {a_title}".format(**message_args))

    if any_sent:
        annc_sent_file.seek(0)
        annc_sent_file.write("\n".join(annc_sent_ids))
