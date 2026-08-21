"""One palette for every rendering of the collection, static or interactive.

The committed PNGs (via lib/chart.py) and the interactive pages (via
tools/build_docs.py) must read as the same charts, so the colours live in this
matplotlib-free module both can import. lib/chart.py re-exports them so figure
code keeps one import surface.
"""

AI = "#c1442f"
# Affiliation-only credits: the same family as AI, visibly weaker evidence.
# Shared here so the PNGs and the interactive pages use one soft red.
AI_SOFT = "#e09a8c"
HUMAN = "#2f6cc1"
# The interactive pages' softened human blue, for sensitivity overlays.
HUMAN_SOFT = "#8fb3d9"
FUZZ = "#c98a00"
VENDOR = "#777777"
NEUTRAL = "#aaaaaa"
# For a series with no authorship field at all, which is a different thing from
# one whose finders are recorded and happen to be human. Blue would claim more
# than the data says: nobody counted who wrote these artifacts.
UNATTRIBUTED = "#37474f"

# Severity is ordered, not categorical, so it takes one hue in even lightness
# steps rather than four separate colours: the reader should see the ordering in
# the ink without consulting the legend. The steps are spaced so the closest
# adjacent pair stays about 16 apart in OKLab (×100) under normal, protanopic
# and deuteranopic vision, and the lightest clears 2:1 against white. The hue is
# deliberately not the AI red or the fuzzer amber those charts already spend on
# identity, so a severity bar cannot be misread as a finder band.
SEVERITY_RAMP = ["#87afc1", "#547d8f", "#234f61", "#002435"]
