import json

import bpy


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


hash_cache = None


def prime_hash_cache():
    global hash_cache
    if hash_cache is not None:
        return
    hash_cache = dict()

    prefs = bpy.context.preferences.addons[__package__].preferences
    if prefs.strings_file is None:
        return
    with open(bpy.path.abspath(prefs.strings_file), 'r') as f:
        strings_list = json.load(f)

    for string in strings_list:
        hash_cache[binhash(string)] = string


def reset_hash_cache():
    global hash_cache
    hash_cache = None


def resolve_hash(hash: int) -> str:
    if hash == 0:
        return '0x{0:08X}'.format(hash)
    prime_hash_cache()
    return hash_cache.get(hash, '0x{0:08X}'.format(hash))
