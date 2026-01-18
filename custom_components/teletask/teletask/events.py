
#################################################################################################
# File:    events.py
# Version: V06.0
#
# Description:
#   Event dataclasses used by MICROS RX-thread system.
#################################################################################################

from dataclasses import dataclass

@dataclass
class AckEvent:
    timestamp: float
    raw: bytes

@dataclass
class StateEvent:
    timestamp: float
    func: int
    num: int
    state: int
    raw: bytes

@dataclass
class GetReplyEvent:
    timestamp: float
    func: int
    num: int
    state: int
    raw: bytes
