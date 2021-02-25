""" Настройки сервиса.
"""
from os import getenv


# Константы для app ----------------------------------------------------------

SERVICE_HOST = getenv("SERVICE_HOST", "0.0.0.0")
SERVICE_PORT = getenv("SERVICE_PORT", "5000")
