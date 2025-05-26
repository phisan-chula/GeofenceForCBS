import re

# Regex with flexible whitespace around zone, easting, northing
utm_pattern = re.compile(r"""
    ^\s*
    (47|48)                       # UTM Zone: 47 or 48
    \s*,\s*                       # Comma separator with optional whitespace
    (\d{6})                       # Easting: 6 digits
    \s*,\s*                       # Comma separator with optional whitespace
    (\d{6,7})                     # Northing: 6-7 digits
    \s*$                         # Optional trailing whitespace
""", re.VERBOSE)

# Thailand UTM bounds
def is_within_thailand_utm(zone, easting, northing):
    zone = int(zone)
    easting = int(easting)
    northing = int(northing)

    # Same range for zone 47 and 48
    return (
        zone in (47, 48) and
        166000 <= easting <= 833000 and
        600000 <= northing <= 2200000
    )

# Test cases with varied spacing
test_cases = [
    "47,666666,1523456",           # no spaces
    "  47 , 666666 , 1523456 ",    # leading/trailing spaces
    "\t47\t,\t500000\t,\t987654",  # tab-separated
    "47 ,100000 ,1500000",         # invalid easting
    "48, 900000, 2000000",         # invalid easting
    "49 , 500000 , 1000000",       # invalid zone
    "47, 600000, 3000000",         # invalid northing
    "47, 600000, 500000",          # invalid northing
    "48, 500000, 1500000",         # valid northing
    "zone , easting , northing",   # invalid format
]

# Validate all cases
for case in test_cases:
    match = utm_pattern.match(case)
    if match:
        zone, easting, northing = match.groups()
        if is_within_thailand_utm(zone, easting, northing):
            print(f"✅ Valid Thailand UTM: {case}")
        else:
            print(f"⚠️  Valid format but OUTSIDE Thailand UTM range: {case}")
    else:
        print(f"❌ Invalid format: {case}")

