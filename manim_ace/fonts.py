import sys

LM_MONO = "Latin Modern Mono"
if sys.platform == "win32":
    # Windows names this font differently for unknown reasons
    LM_MONO = "LM Mono 10"
ROBOTO_MONO = "Roboto Mono"