import json
from pathlib import Path

CONTROLS_PATH = Path(__file__).parent / "controls" / "nist_csf.json"

def load_controls():
    with open(CONTROLS_PATH) as f:
        return json.load(f)

def get_first_control():
    controls = load_controls()
    return controls[0]
