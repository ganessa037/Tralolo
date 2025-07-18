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
        original_line = line
        stripped = line.strip()

        if not stripped or stripped.startswith("```"):
            continue  # skip empty lines and code fences

        stripped_no_bullet = re.sub(r"^(\u2022|\*|-|\d+\.)\s*", "", stripped)

        # Check for indented code or Python assignment → use original line to preserve indentation
        if original_line.startswith(" ") or original_line.startswith("\t") or re.match(r"^\w+\s*=\s*", stripped_no_bullet):
            cleaned.append(original_line.rstrip("\n"))

        # SQL clauses or comments → use original line to preserve indentation
        elif (stripped_no_bullet.startswith("--") or re.match(r"^(SELECT|FROM|WHERE|GROUP BY|ORDER BY|WITH|JOIN|HAVING|LIMIT|UNION|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b", stripped_no_bullet, re.IGNORECASE)):
            cleaned.append(original_line.rstrip("\n"))

        # Plain questions → bullet removed, so use stripped version
        elif stripped_no_bullet.endswith("?"):
            cleaned.append(stripped_no_bullet)

    return cleaned