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
    "FAILURE_PROB": "0",
    "ACCELERATION": "1",
    "DECELERATION": "1",
    "MAX_SPEED": "3",
    "DISPLAY_CELL_SIZE": "0.05",
    "BUSY_WAITING": "False",
    "DURATION": "60 * 10",
    "K": "20",
    "SHAPE": "'chess'",
    "RESULTS_PATH": "'/proj/nova-PG0/shuqin/results'",
    "DEBUG": "False",
    "FILE_NAME_KEYS": "[('DISPATCHERS', 'D'), ('DISPATCH_RATE', 'R'), ('FAILURE_TIMEOUT', 'T'), ('MAX_SPEED', 'S')]",
    "DIR_KEYS": "['K']",
    "SERVER_TIMEOUT": "120",
    "PROCESS_JOIN_TIMEOUT": "120",
    "DISPATCHERS": "1",
    "DISPATCH_RATE": "'inf'",
    "MULTICAST": "False",
    "INPUT": "'racecar_K20'"
}

general_props = [
    {
        "keys": ["DISPATCH_RATE"],
        # "values": ["1", "'inf'"]
        "values": ["'inf'"]
    },
    {
        "keys": ["K", "INPUT"],
        "values": [
            {"K": "0", "INPUT": "'chess_K3'"},
            {"K": "3", "INPUT": "'chess_K3'"}
            # {"K": "20", "INPUT": "'chess_K20'"},
        ]
    },
    {
        "keys": ["DISPATCHERS"],
        "values": ["1", "3"]
    },
    {
        "keys": ["FAILURE_TIMEOUT"],
        "values": ["30", "60"]
        # "values": ["30"]
        # "values": ["1", "3", "6", "30", "60", "120", "600"]
    },
    {
        "keys": ["MAX_SPEED", "ACCELERATION", "DECELERATION"],
        "values": [
            {"MAX_SPEED": "30", "ACCELERATION": "10", "DECELERATION": "10"},
            {"MAX_SPEED": "3", "ACCELERATION": "1", "DECELERATION": "1"}
        ]
    },
    # {
    #     "keys": ["SHAPE"],
    #     "values": ["'racecar'", "'skateboard'"]
    # }
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

