'''
Constant definitions
'''

## Operation constants.
#: indicates a set request
OP_SET = 0
#: indicates a get request
OP_GET = 1
#OP_CONFIG = 6 # config is deprecated
#: indicates a send request
OP_SEND = 7
#: indicates a run request
OP_RUN = 8
#: indicates a command request
OP_CMD = 9

# Message type constants.
T_REPLY = 2
T_REQUEST = 3
T_ALERT = 4

# Timestamp format (RFC3339)
TIME_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
