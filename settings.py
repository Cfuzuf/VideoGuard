import os
from dotenv import load_dotenv


load_dotenv()

CAMERA_IP = os.getenv("CAMERA_IP")
CAMERA_LOGIN = os.getenv("CAMERA_LOGIN")
CAMERA_PASSWORD = os.getenv("CAMERA_PASSWORD")
TOKEN = os.getenv("TOKEN")
CHANNEL_CHAT_ID = int(os.getenv("CHANNEL_CHAT_ID"))
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID"))
ALLOWED_USERS_ID = list(map(int, os.getenv("ALLOWED_USERS_ID").split()))
