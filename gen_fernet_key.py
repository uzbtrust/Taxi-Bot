"""Run once to generate your FERNET_KEY for .env"""
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
