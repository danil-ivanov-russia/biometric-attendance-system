import io

import numpy as np


def convert_encoding_to_binary(encoding):
    out = io.BytesIO()
    np.save(out, encoding)
    out.seek(0)
    return out.read()


def convert_binary_to_encoding(binary):
    out = io.BytesIO(binary)
    out.seek(0)
    return np.load(out)
