from hera_cal import io
import sys

# extract relevant information from filename
basefile = sys.argv[1]
JD = (basefile.split("zen.")[-1]).split(".")[0]
time = ".".join(basefile.split("zen.")[-1].split(".")[0:2])

# load flags from validation abscal file
ac_file = basefile.replace(".uvh5", ".abs.calfits")
print(f"Now loading {ac_file}")
hc_ac = io.HERACal(ac_file)
_, flags_ac, _, _ = hc_ac.read()

# load flags from H1C IDR2.2
h1c_idr2_fa_file = (
    f"/lustre/aoc/projects/hera/H1C_IDR2/IDR2_2/{JD}/zen.{time}.HH.flagged_abs.calfits"
)
print(f"Loading flags from {h1c_idr2_fa_file}")
hc_fa = io.HERACal(h1c_idr2_fa_file)
_, flags_fa, _, _ = hc_fa.read()

# cross apply flags
for ant in flags_ac:
    flags_ac[ant] = flags_fa[ant]
hc_ac.history += f"\nFlags transfered from {h1c_idr2_fa_file} using xrfi_transfer.py\n"

# update flags and write to disk
hc_ac.update(flags=flags_ac)
outfile = ac_file.replace(".abs.", ".flagged_abs.")
print(f"Saving calfits with modified flags to {outfile}")
hc_ac.write_calfits(outfile, clobber=True)
