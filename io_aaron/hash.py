def binhash(string: str) -> int:
    val = 0xFFFFFFFF
    for c in string:
        val = (val * 33 + ord(c)) & 0xFFFFFFFF
    return val


def string_to_hash(string: str) -> int:
    if not string.startswith('0x'):
        return binhash(string)
    try:
        return int(string, 16)
    except ValueError:
        return binhash(string)
