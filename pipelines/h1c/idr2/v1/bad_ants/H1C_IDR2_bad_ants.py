#!/usr/bin/env python
"""Script for producing bad_ants text files."""

JDs = [
    2458098,
    2458099,
    2458101,
    2458102,
    2458103,
    2458104,
    2458105,
    2458106,
    2458107,
    2458108,
    2458109,
    2458110,
    2458111,
    2458112,
    2458113,
    2458114,
    2458115,
    2458116,
    2458140,
]

always_flagged = [0, 2, 50, 98, 136]

for JD in JDs:
    flagged = set(always_flagged)
    if JD == 2458114:
        flagged.add(11)
    if JD == 2458140:
        flagged.add(68)
        flagged.add(104)
        flagged.add(117)
    with open(str(JD) + ".txt", "w") as f:
        for bad_ant in sorted(flagged):
            f.write(str(bad_ant) + "\n")
