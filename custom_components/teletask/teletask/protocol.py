
#################################################################################################
# File:    protocol.py
# Version: V06.1
#
# Description:
#   Protocol constants for TELETASK MICROS RS232 communication.
#################################################################################################

# Frame markers
STX: int = 0x02

# Command types
CMD_SET: int = 1
CMD_GET: int = 2
CMD_LOG: int = 3      # Enable/disable event reporting for a function type
CMD_EVENT: int = 8

# Function types (MICROS RS232 supported)
FUNC_RELAY: int = 1
FUNC_DIMMER: int = 2
FUNC_LOCMOOD: int = 8
FUNC_TIMEDMOOD: int = 9
FUNC_GENMOOD: int = 10
FUNC_FLAG: int = 15
FUNC_SENSOR: int = 20     # Analog sensors (temperature, humidity, lux)
FUNC_MOTOR: int = 55
FUNC_COND: int = 60       # Condition

# Note: MICROS RS232 does NOT report physical input events.
# Inputs trigger actions (relay/dimmer/mood changes) which ARE reported,
# but the input event itself is not sent over RS232.

# State values (MICROS uses 255 for ON, 0 for OFF)
STATE_OFF: int = 0
STATE_ON: int = 255
