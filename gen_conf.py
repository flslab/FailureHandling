import itertools
import os
import sys

def_general_conf = {
    "INITIAL_RANGE": "2000",
    "MAX_RANGE": "2000",
    "DROP_PROB_SENDER": "0",
    "DROP_PROB_RECEIVER": "0",
    "DEAD_RECKONING_ANGLE": "0",
    "FAILURE_TIMEOUT": "60 * 2",
    "FAILURE_MODEL": "0",
    "FAILURE_PROB": "0",
    "ACCELERATION": "1",
    "DECELERATION": "1",
    "MAX_SPEED": "3",
    "DISPLAY_CELL_SIZE": "0.05",
    "BUSY_WAITING": "False",
    "DURATION": "60 * 60",
    "K": "3",
    "SHAPE": "'chess'",
    "RESULTS_PATH": "'/proj/nova-PG0/shuqin/results/'",
    # "RESULTS_PATH": "'/Users/shuqinzhu/Desktop/experiments_aug29.nosync'",
    "DEBUG": "False",
    "FILE_NAME_KEYS": "[('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T'), ('MAX_SPEED', 'S'),"
    "('PRIORITIZE_ILLUMINATING_FLS', 'P')]",
    # "('NAME', 'N')]",
    #                   "('DISPATCHER_ASSIGN_POLICY', 'P')]",
    # "]",
    "DIR_KEYS": "['K']",
    "SERVER_TIMEOUT": "120",
    "PROCESS_JOIN_TIMEOUT": "120",
    "DISPATCHERS": "1",
    "DISPATCH_RATE": "'inf'",
    "MULTICAST": "False",
    "INPUT": "'chess_Kmeans20'",
    "RESET_AFTER_INITIAL_DEPLOY": "True",  # flag that if reset all metrics after intial FLSs are all deployed
    "SANITY_TEST": "0",  # 0 for not test, 1 for normal test with hub and no standby, 2 for standby test with no hub
    "SANITY_TEST_CONFIG": "[('NUMBER_OF_FLS', 10), ('DIST_TO_POINT', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]",
    "STANDBY_TEST_CONFIG": "[('RADIUS', 10), ('DEPLOY_DIST', 10), ('FAILURE_TIMEOUT_GAP', 10), ('CHECK_TIME_RANGE', 60 * 0.5, 60 * 1)]",
    "DISPATCHER_ASSIGN_POLICY": "'ShortestDistance'",
    "PRIORITIZE_ILLUMINATING_FLS": "True",
    "CEDED_POLICY": "1",
    "NAME": "'kmeans'"

}

general_props = [
    {
        "keys": ["SHAPE", "K", "INPUT", "DISPATCHERS", "DISPATCH_RATE", "FAILURE_TIMEOUT", "PRIORITIZE_ILLUMINATING_FLS"],
        "values": [
            # {"SHAPE": "'skateboard'", "K": "3", "INPUT": "'skateboard_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "35",
            #  "FAILURE_TIMEOUT": "60", "PRIORITIZE_ILLUMINATING_FLS": "True"},
            #
            # {"SHAPE": "'skateboard'", "K": "3", "INPUT": "'skateboard_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "35",
            #  "FAILURE_TIMEOUT": "60", "PRIORITIZE_ILLUMINATING_FLS": "False"},
            {"SHAPE": "'dragon'", "K": "0", "INPUT": "'dragon_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
             "FAILURE_TIMEOUT": "900", "PRIORITIZE_ILLUMINATING_FLS": "True"},

            {"SHAPE": "'dragon'", "K": "3", "INPUT": "'dragon_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
             "FAILURE_TIMEOUT": "900", "PRIORITIZE_ILLUMINATING_FLS": "True"},

            {"SHAPE": "'dragon'", "K": "20", "INPUT": "'dragon_G20'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
             "FAILURE_TIMEOUT": "900", "PRIORITIZE_ILLUMINATING_FLS": "True"},

            # {"SHAPE": "'dragon'", "K": "3", "INPUT": "'dragon_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "10",
            #  "FAILURE_TIMEOUT": "60", "PRIORITIZE_ILLUMINATING_FLS": "False"},

            # {"SHAPE": "'skateboard'", "K": "0", "INPUT": "'skateboard_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
            #  "FAILURE_TIMEOUT": "120"},
            # {"SHAPE": "'skateboard'", "K": "3", "INPUT": "'skateboard_G3'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
            #  "FAILURE_TIMEOUT": "120"},
            # {"SHAPE": "'skateboard'", "K": "20", "INPUT": "'skateboard_G20'", "DISPATCHERS": "1", "DISPATCH_RATE": "3000",
            #  "FAILURE_TIMEOUT": "120"},

            # {"SHAPE": "'skateboard'", "K": "0", "INPUT": "'skateboard_G3'", "DISPATCHERS": "3", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
            # {"SHAPE": "'skateboard'", "K": "3", "INPUT": "'skateboard_G3'", "DISPATCHERS": "3", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
            # {"SHAPE": "'skateboard'", "K": "20", "INPUT": "'skateboard_G20'", "DISPATCHERS": "3", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
            # {"SHAPE": "'skateboard'", "K": "0", "INPUT": "'skateboard_G3'", "DISPATCHERS": "4", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
            # {"SHAPE": "'skateboard'", "K": "3", "INPUT": "'skateboard_G3'", "DISPATCHERS": "4", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
            # {"SHAPE": "'skateboard'", "K": "20", "INPUT": "'skateboard_G20'", "DISPATCHERS": "4", "DISPATCH_RATE": "1000",
            #  "FAILURE_TIMEOUT": "60"},
        ]
    },
    # {
    #     "keys": ["DISPATCH_RATE"],
    #     "values": ["3000"],
    #     # "values": ["10", "20", "100"]
    #     # "values": ["5", "10"]
    # },
    # {
    #     "keys": ["K", "INPUT", "SHAPE", "NAME"],
    #     "values": [
    #
    #         {"K": "0", "INPUT": "'skateboard_G3'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #         {"K": "3", "INPUT": "'skateboard_G3'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #         {"K": "5", "INPUT": "'skateboard_G5'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #         {"K": "10", "INPUT": "'skateboard_G10'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #         {"K": "15", "INPUT": "'skateboard_G15'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #         {"K": "20", "INPUT": "'skateboard_G20'", "SHAPE": "'skateboard'", "NAME": "'kmeans'"},
    #
    #     ]
    # },
    # {
    #     "keys": ["DISPATCHERS"],
    #     "values": ["1"],
    #     # "values": ["1", "3"]
    # },
    # {
    #     "keys": ["FAILURE_TIMEOUT"],
    #     # "values": ["30", "60", "120", "300"]
    #     "values": ["900"]
    #     # "values": ["1", "3", "6", "30", "60", "120", "600"]
    # },
    {
        "keys": ["MAX_SPEED", "ACCELERATION", "DECELERATION"],
        "values": [
            {"MAX_SPEED": "6.11", "ACCELERATION": "6.11", "DECELERATION": "6.11"},
            # {"MAX_SPEED": "30", "ACCELERATION": "30", "DECELERATION": "30"},
            # {"MAX_SPEED": "66.67", "ACCELERATION": "66.67", "DECELERATION": "66.67"},
        ]
    },

    # {
    #     "keys": ["K", "INPUT", "DISPATCHERS"],
    #     "values": [
    #         {"K": "0", "INPUT": "'dragon_K3'", "DISPATCHERS": "1"},
    #         # {"K": "0", "INPUT": "'dragon_K10'", "DISPATCHERS": "3"},
    #         {"K": "3", "INPUT": "'dragon_K3'", "DISPATCHERS": "1"},
    #         {"K": "5", "INPUT": "'dragon_K5'", "DISPATCHERS": "1"},
    #         {"K": "15", "INPUT": "'dragon_K15'", "DISPATCHERS": "1"},
    #         {"K": "10", "INPUT": "'dragon_K10'", "DISPATCHERS": "1"},
    #         {"K": "15", "INPUT": "'dragon_K15'", "DISPATCHERS": "1"},
    #         {"K": "20", "INPUT": "'dragon_K20'", "DISPATCHERS": "1"},
    #     ]
    # },

    # {
    #     "keys": ["PRIORITIZE_ILLUMINATING_FLS"],
    #     "values": ["True"]
    # },
    # # {
    {
        "keys": ["DISPATCHER_ASSIGN_POLICY"],
        # "values": ["'ShortestDistance'", "'PoD'", "'RR'", "'Random'", "'HybridSDPoD'"]
        "values": ["'ShortestDistance'"]
    },
    # {
    #     "keys": ["SANITY_TEST", "DISPATCHERS"],
    #     "values": [
    #         # {"SANITY_TEST": "True", "DISPATCHERS": "1"}]
    #     # "values": ["1", "3", "6", "30", "60", "120", "600"]
    # },
    # {
    #     "keys": ["SHAPE"],
    #     "values": ["'skateboard'"]
    # },
    # {
    #     "keys": ["SAMPLE_SIZE", "SHAPE"],
    #     "values": [{"SAMPLE_SIZE": 94, "SHAPE": "'butterfly'"},
    #                {"SAMPLE_SIZE": 100, "SHAPE": "'teapot'"},
    #                {"SAMPLE_SIZE": 114, "SHAPE": "'cat'"}]
    # },
]

if __name__ == '__main__':
    if not os.path.exists('experiments'):
        os.makedirs('experiments', exist_ok=True)

    file_name = "config"
    class_name = "Config"
    props = general_props
    def_conf = def_general_conf
    # if len(sys.argv) > 1:
    #     file_name = "test_config"
    #     class_name = "TestConfig"
    #     props = test_props
    #     def_conf = def_test_conf

    props_values = [p["values"] for p in props]
    print(props_values)
    combinations = list(itertools.product(*props_values))
    print(len(combinations))

    for j in range(len(combinations)):
        c = combinations[j]
        conf = def_conf.copy()
        for i in range(len(c)):
            for k in props[i]["keys"]:
                if isinstance(c[i], dict):
                    conf[k] = c[i][k]
                else:
                    conf[k] = c[i]
        with open(f'experiments/{file_name}{j}.py', 'w') as f:
            f.write(f'class {class_name}:\n')
            for key, val in conf.items():
                f.write(f'    {key} = {val}\n')
