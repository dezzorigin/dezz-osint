"""dezz-osint project config — paths to upstream tools + engine toggles."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent          # dezz-osint/
DATA = ROOT / "Data"
DATA.mkdir(exist_ok=True)

# Upstream checkouts (cloned side-by-side for reference / optional launch)
WORKSPACE = ROOT.parent  # Default Project/
MAIGRET_DIR = Path(os.getenv("MAIGRET_DIR", WORKSPACE / "maigret-upstream"))
TOOKIE_DIR = Path(os.getenv("TOOKIE_DIR", WORKSPACE / "tookie-osint"))
PHOTON_DIR = Path(os.getenv("PHOTON_DIR", WORKSPACE / "Photon"))
SPIDERFOOT_DIR = Path(os.getenv("SPIDERFOOT_DIR", WORKSPACE / "spiderfoot-upstream"))
AWESOME_README = Path(os.getenv("AWESOME_README", WORKSPACE / "awesome-osint-upstream" / "README.md"))

VERSION = "0.2.0"
