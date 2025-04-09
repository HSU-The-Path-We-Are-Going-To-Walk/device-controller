import os
from dotenv import load_dotenv

load_dotenv()

DEVICE_IP = os.getenv("DEVICE_IP")
USERNAME = os.getenv("DEVICE_USERNAME")
PASSWORD = os.getenv("DEVICE_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")
CHATBOT_SERVER = os.getenv("CHATBOT_SERVER")
ADMIN_SERVER = os.getenv("ADMIN_SERVER")
BUS_STOP_ID = int(os.getenv("BUS_STOP_ID"))