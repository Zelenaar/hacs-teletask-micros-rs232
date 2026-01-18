
#################################################################################################
# File:    helpers.py
# Version: V06.0
#
# Description:
#   Small helper utilities for Teletask protocol.
#################################################################################################

def bytes_to_hex(b: bytes) -> str:
    return " ".join(f"{x:02X}" for x in b)

def checksum(data: bytes) -> int:
    return sum(data) & 0xFF
