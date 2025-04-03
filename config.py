import os
from dotenv import load_dotenv

load_dotenv()

DEVICE_IP = os.getenv("DEVICE_IP")
USERNAME = os.getenv("DEVICE_USERNAME")
PASSWORD = os.getenv("DEVICE_PASSWORD")
TARGET_EMAIL = os.getenv("TARGET_EMAIL")
SERVER = os.getenv("SERVER")