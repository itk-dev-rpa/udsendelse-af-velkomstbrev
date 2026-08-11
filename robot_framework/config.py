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
KEYVAULT_PATH = "Udsendelse-af-Velkomstbrev-International"
EVENT_LOG_CONN = "Event Log"


# Queue specific configs
# ----------------------

# The name of the job queue (if any)
QUEUE_NAME = "Udsendelse af Velkomstbrev"

# Robot specific configs
# ----------------------
SAVE_FOLDER = "robot_framework/tmp"
CVR = "55133018"
PDF_WELCOME = 'robot_framework/template/Velkomstbrev_AK_digital.pdf'
FONT_NAME = 'OpenSans'
FONT_PATH = 'robot_framework/template/OpenSans-Bold.ttf'
FONT_COLOR = '#538135'
# How long to wait after a person arrived in the city before sending them a letter,
# and how far back to keep looking for arrivals we haven't sent a letter for yet.
MIN_DAYS_SINCE_ARRIVAL = 21
MAX_DAYS_SINCE_ARRIVAL = 30
# Format of the arrival date stored on queue elements. Dates are no longer formatted into the query.
QUEUE_DATE_FORMAT = "%d-%m-%Y"
EXPLORE_LINK = "https://direc.to/kN8s"
FEEDBACK_LINK = "https://www.survey-xact.dk/LinkCollector?key=1HZ74774L19K"
