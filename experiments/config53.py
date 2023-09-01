class Config:
    INITIAL_RANGE = 2000
    MAX_RANGE = 2000
    DROP_PROB_SENDER = 0
    DROP_PROB_RECEIVER = 0
    DEAD_RECKONING_ANGLE = 0
    FAILURE_TIMEOUT = 5
    FAILURE_PROB = 0
    ACCELERATION = 600
    DECELERATION = 600
    MAX_SPEED = 600
    DISPLAY_CELL_SIZE = 0.05
    BUSY_WAITING = False
    DURATION = 60
    K = 5
    SHAPE = 'chess'
    RESULTS_PATH = '/proj/nova-PG0/shuqin/results'
    DEBUG = False
    FILE_NAME_KEYS = [('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T'), ('MAX_SPEED', 'S')]
    DIR_KEYS = ['K']
    SERVER_TIMEOUT = 120
    PROCESS_JOIN_TIMEOUT = 120
    DISPATCHERS = 1
    DISPATCH_RATE = 'inf'
    MULTICAST = False
    INPUT = 'chess_K5'
    RESET_AFTER_INITIAL_DEPLOY = True
    SANITY_TEST = 0
    SANITY_TEST_CONFIG = [('NUMBER_OF_FLS', 10), ('DIST_TO_POINT', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]
    STANDBY_TEST_CONFIG = [('RADIUS', 10), ('DEPLOY_DIST', 10), ('FAILURE_TIMEOUT_GAP', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]
