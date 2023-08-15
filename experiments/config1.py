class Config:
    INITIAL_RANGE = 2000
    MAX_RANGE = 2000
    DROP_PROB_SENDER = 0
    DROP_PROB_RECEIVER = 0
    DEAD_RECKONING_ANGLE = 0
    FAILURE_TIMEOUT = 30
    FAILURE_PROB = 0
    ACCELERATION = 1
    DECELERATION = 1
    MAX_SPEED = 3
    DISPLAY_CELL_SIZE = 0.05
    BUSY_WAITING = False
    DURATION = 60 * 10
    K = 0
    SHAPE = 'chess'
    RESULTS_PATH = '/proj/nova-PG0/shuqin/results'
    DEBUG = False
    FILE_NAME_KEYS = [('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T')]
    DIR_KEYS = ['K']
    SERVER_TIMEOUT = 120
    PROCESS_JOIN_TIMEOUT = 120
    DISPATCHERS = 1
    DISPATCH_RATE = 'inf'
    MULTICAST = False
    INPUT = 'chess_K3'
