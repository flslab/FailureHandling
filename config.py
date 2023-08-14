class Config:
    INITIAL_RANGE = 2000
    MAX_RANGE = 2000
    DROP_PROB_SENDER = 0
    DROP_PROB_RECEIVER = 0
    DEAD_RECKONING_ANGLE = 0
    FAILURE_TIMEOUT = 60 * 0.5
    FAILURE_PROB = 0
    ACCELERATION = 1
    DECELERATION = 1
    MAX_SPEED = 3
    DISPLAY_CELL_SIZE = 0.05
    BUSY_WAITING = False
    DURATION = 60 * 0.3
    K = 5  # if k = 0 no standbys are deployed
    SHAPE = 'racecar'
    RESULTS_PATH = 'results'
    DEBUG = True
    FILE_NAME_KEYS = [('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T'), ('MAX_SPEED_1', 'S')]
    DIR_KEYS = ['K']
    SERVER_TIMEOUT = 120
    PROCESS_JOIN_TIMEOUT = 120
    DISPATCHERS = 5  # valid values 1 3 5
    DISPATCH_RATE = 1  # valid values 'inf' or a non-zero number
    MULTICAST = False  # should be False for cloudlab and True for AWS
    INPUT = 'racecar_K5'  # place the file int the results directory
