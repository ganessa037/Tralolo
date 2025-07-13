import re

def patch_missing_imports(code):
    patched = code
    if "sns." in code and "import seaborn" not in code:
        patched = "import seaborn as sns\n" + patched
    if "datetime" in code and "import datetime" not in code and "from datetime" not in code:
        patched = "from datetime import datetime\n" + patched
    if "pd." in code and "import pandas" not in code:
        code = "import pandas as pd\n" + code
    if "np." in code and "import numpy" not in code:
        patched = "import numpy as np\n" + patched
    return patched

def strip_lines(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        if not line.strip() or line.strip().startswith("```"):
            continue  # skip empty lines and code fences

        # If the line starts with indentation (spaces or tabs), it's code — keep as-is
        if line.startswith(" ") or line.startswith("\t"):
            cleaned.append(line.rstrip("\n"))
        else:
            # Remove leading bullets/numbers if present
            cleaned.append(re.sub(r"^[-–•\d\.\)\s]+", "", line))

    return cleaned