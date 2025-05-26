import re

# Regex to match valid lat,long strings with optional spaces
lat_long_pattern = re.compile(r"""
    ^\s*
    (-?\d+(?:\.\d+)?)
    \s*,\s*
    (-?\d+(?:\.\d+)?)
    \s*$
""", re.VERBOSE)

# Thailand bounding box
MIN_LAT, MAX_LAT = 5.0, 21.0
MIN_LON, MAX_LON = 97.0, 106.0

def is_within_thailand(lat, lon):
    return MIN_LAT <= lat <= MAX_LAT and MIN_LON <= lon <= MAX_LON

# Test cases
test_cases = [
    "13.701819140103558, 100.54416756337254",   # Bangkok (valid)
    "20.0, 105.0",                              # Northern Thailand (valid)
    "4.9, 100.0",                               # Too far south (invalid)
    "22.0, 100.0",                              # Too far north (invalid)
    "13.5, 96.9",                               # Too far west (invalid)
    "13.5, 106.1",                              # Too far east (invalid)
    "latitude, longitude",                      # Invalid format
]

# Run validation
for case in test_cases:
    match = lat_long_pattern.match(case)
    if match:
        lat, lon = map(float, match.groups())
        if is_within_thailand(lat, lon):
            print(f"✅ Valid in Thailand: {case}")
        else:
            print(f"⚠️  Valid format but OUTSIDE Thailand: {case}")
    else:
        print(f"❌ Invalid format: {case}")

