#!/usr/bin/env python3
"""Independently decode the Zen encoder's IEEE float WAV chunks."""
from pathlib import Path
import struct
import subprocess
import tempfile

binary = Path(__file__).resolve().parents[2] / "build/wav-test"
with tempfile.TemporaryDirectory(prefix="zen-wav-") as temporary:
    subprocess.run([str(binary)], cwd=temporary, check=True)
    data = (Path(temporary) / "test.wav").read_bytes()
    assert data[:4] == b"RIFF" and data[8:12] == b"WAVE"
    assert struct.unpack_from("<I", data, 4)[0] == len(data) - 8
    chunks = {}
    offset = 12
    while offset < len(data):
        tag, length = struct.unpack_from("<4sI", data, offset)
        offset += 8
        chunks[tag] = data[offset:offset + length]
        assert len(chunks[tag]) == length
        offset += length + length % 2
    assert offset == len(data)
    assert struct.unpack("<HHIIHHH", chunks[b"fmt "]) == (3, 1, 16000, 64000, 4, 32, 0)
    assert struct.unpack("<I", chunks[b"fact"]) == (4,)
    assert struct.unpack("<4f", chunks[b"data"]) == (0.0, 0.5, -0.5, 1.0)
print("WAV independent chunk and sample validation passed")
