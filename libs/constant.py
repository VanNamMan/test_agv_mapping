MODEL_DIR = "resources/models"
LOG_DIR = "log"
DATABASE_DIR = "resources/database"
DATABASE_PATH = "resources/database/database.db"
IMAGE_DIR = "resources/images"
CANVAS_LABEL_PATH = "resources/static/labels.txt"
GENERAL_PATH = "resources/static/general.json"

PASS = 1
FAIL = 0
CHECKING = -1
MAT_IS_NONE = -2

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
IMG_FILENAME_FORMAT = "%Y%m%d_%H%M%S_%f.jpg"

STEP_WAIT_TRIGGER = 0
STEP_CHECKING = 1
STEP_WAIT_CHECKING = 2
STEP_OUTPUT = 3
STEP_CAPTURE = 4
STEP_SET_ORG = 5

# update check tape on jig
PGM_VERSION = "22.00.02.11.2023"

CONN_CAMERA = 0
CONN_COMPORT = 1
CONN_SOCKET = 2 

SAVE_NG = 0
SAVE_OK = 1
SAVE_ALL = 2
DONT_SAVE = -1

WARNING = 0
INFO = 1
QUESTION = 2

FLIP_H = 1
FLIP_V = 0
FLIP_T = -1
NO_FLIP = 2

CAMERA_CLASS_INDEX = 0
PHONE_CLASS_INDEX = 1

TOPLEFT = "topleft"
TOPRIGHT = "topright"
BOTTOMLEFT = "bottomleft"
BOTTOMRIGHT = "bottomright"

CV_GREEN = (0, 255, 0)
CV_BLUE = (255, 0, 0)
CV_RED = (0, 0, 255)
CV_YELLOW = (0, 255, 255)
CV_BLACK = (0, 0, 0)
CV_WHITE = (255, 255, 255)

TRANSFER_TABLE = "transfer"
TURN_TABLE = "turn"
ELEVATOR_TABLE = "elevator"
STANDBY_TABLE = "standby"
SPEED_TABLE = "speed"
DISPLAY_TABLE = "display"
OTHER_TABLE = "other"