import zlib

def compress(data: bytes) -> bytes:
    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    return zlib.compress(data, zlib.Z_BEST_COMPRESSION)

    return compressed

def decompress(data: bytes) -> bytes:
    if not isinstance(data, bytes):
        data = data.encode('utf-8')

    return zlib.decompress(data)