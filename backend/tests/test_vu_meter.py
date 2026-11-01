import pytest
import struct
from vu_meter import VUMeter

def test_calculate_rms_silence():
    meter = VUMeter()
    data = struct.pack("<4h", 0, 0, 0, 0) # 4 samples of silence
    rms = meter.calculate_rms(data)
    assert rms == 0

def test_calculate_rms_sine_ish():
    meter = VUMeter()
    # RMS of [1000, -1000, 1000, -1000] is 1000
    data = struct.pack("<4h", 1000, -1000, 1000, -1000)
    rms = meter.calculate_rms(data)
    assert rms == 1000.0
