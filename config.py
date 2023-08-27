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
    DURATION = 30
    K = 0  # if k = 0 no standbys are deployed
    SHAPE = 'racecar'
    RESULTS_PATH = 'results'
    DEBUG = True
    FILE_NAME_KEYS = [('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T'), ('MAX_SPEED', 'S'),
                      ('SANITY_TEST', 'test')]
    DIR_KEYS = ['K']
    SERVER_TIMEOUT = 120
    PROCESS_JOIN_TIMEOUT = 120
    DISPATCHERS = 1  # valid values 1 3 5
    DISPATCH_RATE = "inf"  # valid values 'inf' or a non-zero number
    MULTICAST = False  # should be False for cloudlab and True for AWS
    INPUT = 'racecar_K5'  # place the file int the results directory
    RESET_AFTER_INITIAL_DEPLOY = False  # flag that if reset all metrics after intial FLSs are all deployed
    SANITY_TEST = 0 # 0 for not test, 1 for normal test with hub and no standby, 2 for standby test with no hub
    SANITY_TEST_CONFIG = [('NUMBER_OF_FLS', 10), ('DIST_TO_POINT', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]
    STANDBY_TEST_CONFIG = [('RADIUS', 10), ('DEPLOY_DIST', 10), ('FAILURE_TIMEOUT_GAP', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]
