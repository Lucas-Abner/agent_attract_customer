from instagrapi import Client
import os

USERNAME = os.getenv("LOGIN_USERNAME", "llucasabnerr")
PASSWORD = os.getenv("LOGIN_PASSWORD", "L.abner1")

cl = Client()

try:
    login = cl.login(USERNAME, PASSWORD)
    print(f"Login realizado: @{USERNAME}")
except Exception as e:
    print(f"Login deu errado: @{USERNAME}. Error {e}")
    