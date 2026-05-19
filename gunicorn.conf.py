# Gunicorn configuration file to prevent worker timeout
import os

bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
timeout = 120
workers = 1
threads = 4
