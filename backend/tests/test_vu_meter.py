import pytest
import struct
import math
from vu_meter import VUMeter

def test_calculate_rms_silence():
    meter = VUMeter()
    data = struct.pack("<4h", 0, 0, 0, 0) # 4 samples of silence
    rms = meter.calculate_rms(data)
    assert rms == 0

def test_calculate_rms_constant():
    meter = VUMeter()
    # 1000 is the constant value for all samples
    val = 1000
    data = struct.pack("<4h", val, val, val, val)
    rms = meter.calculate_rms(data)
    assert rms == float(val)

def test_calculate_rms_sine_ish():
    meter = VUMeter()
    # RMS of [1000, -1000, 1000, -1000] is 1000
    data = struct.pack("<4h", 1000, -1000, 1000, -1000)
    rms = meter.calculate_rms(data)
    assert rms == 1000.0

def test_db_mapping():
    # Test dB logic
    # -96dB is our floor
    rms = 0
    db = 20 * math.log10(rms / 32768.0) if rms > 0 else -96.0
    assert db == -96.0
    
    # 0dB is full scale (32768)
    rms = 32768.0
    db = 20 * math.log10(rms / 32768.0)
    assert db == 0.0

def test_percentage_mapping():
    # Test (db + 60) / 60 * 100 logic
    # -60dB -> 0%
    db = -60.0
    percentage = max(0, min(100, (db + 60) / 60 * 100))
    assert percentage == 0
    
    # 0dB -> 100%
    db = 0.0
    percentage = max(0, min(100, (db + 60) / 60 * 100))
    assert percentage == 100
    
    # -30dB -> 50%
    db = -30.0
    percentage = max(0, min(100, (db + 60) / 60 * 100))
    assert percentage == 50
