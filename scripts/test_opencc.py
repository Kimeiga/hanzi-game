#!/usr/bin/env python3
"""Test OpenCC and HowNet integration."""

import subprocess
import sys

# Install if needed
subprocess.run([sys.executable, "-m", "pip", "install", "opencc-python-reimplemented", "-q"])

import opencc
import OpenHowNet

# Initialize
converter = opencc.OpenCC('t2s')  # Traditional to Simplified
hownet_dict = OpenHowNet.HowNetDict()

# Test traditional characters
test_chars = ['馬', '鳥', '魚', '龍', '鳳', '國', '學', '書', '話', '語']

print("Testing Traditional -> Simplified -> HowNet lookup:")
print("-" * 60)

for trad in test_chars:
    simp = converter.convert(trad)
    
    # Try traditional first
    trad_senses = hownet_dict.get_sense(trad)
    trad_sememes = None
    if trad_senses:
        try:
            trad_sememes = trad_senses[0].get_sememe_list()
        except:
            pass
    
    # Try simplified
    simp_senses = hownet_dict.get_sense(simp)
    simp_sememes = None
    if simp_senses:
        try:
            simp_sememes = simp_senses[0].get_sememe_list()
        except:
            pass
    
    print(f"{trad} -> {simp}")
    print(f"  Traditional lookup: {trad_sememes}")
    print(f"  Simplified lookup:  {simp_sememes}")
    print()

