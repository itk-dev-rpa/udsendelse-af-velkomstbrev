"""This module contains configuration constants used across the framework"""

# The number of times the robot retries on an error before terminating.
MAX_RETRY_COUNT = 3

# Whether the robot should be marked as failed if MAX_RETRY_COUNT is reached.
FAIL_ROBOT_ON_TOO_MANY_ERRORS = True

# Error screenshot config
SMTP_SERVER = "smtp.aarhuskommune.local"
SMTP_PORT = 25
SCREENSHOT_SENDER = "robot@friend.dk"

# Constant/Credential names
ERROR_EMAIL = "Error Email"
KEYVAULT_CREDENTIALS = "Keyvault"
KEYVAULT_URI = "Keyvault URI"
KEYVAULT_PATH = "Digital_Post_Masseopslag"


# Queue specific configs
# ----------------------

# The name of the job queue (if any)
QUEUE_NAME = "Udsendelse af Velkomstbrev"

# Robot specific configs
# ----------------------
SAVE_FOLDER = "robot_framework/tmp"
CVR = "55133018"
TEMPLATE = 'robot_framework/template/Welcome letter to internationals.docx'
PDF_WELCOME = 'robot_framework/template/Welcome letter to internationals_noname.pdf'
MAX_DAYS_SINCE_LAST_MOVE = 50
