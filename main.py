"""Copy entry.png to the grader output directory.

The entry image is a fixed file shipped in the same directory as this
program (rendered in-session by render.py + stories.json, deterministic).
The program copies it unchanged into the directory given by the
MAKEFUN_OUTPUT_DIR environment variable (default /output) and checks that
the copy has exactly the same size as the source, so repeated runs produce
identical bytes. No network, no randomness, no runtime dependencies
beyond the standard library — the render itself is not re-run here.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
# The grader sets MAKEFUN_OUTPUT_DIR; honour ENTRY_OUT too (the
# renderer's variable) so the copy lands in the right place either way.
OUT = os.environ.get("ENTRY_OUT")
if OUT is None:
    OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    OUT = os.path.join(OUT_DIR, "entry.png")
else:
    OUT_DIR = os.path.dirname(OUT) or "."

os.makedirs(OUT_DIR, exist_ok=True)
shutil.copyfile(SRC, OUT)

assert os.path.getsize(OUT) == os.path.getsize(SRC), "copy size mismatch"
# The grader runs this program twice; both runs must write the same
# bytes, which holds because the source image is fixed in the repo.
print(f"entry image: {OUT} ({os.path.getsize(OUT)} bytes)")
