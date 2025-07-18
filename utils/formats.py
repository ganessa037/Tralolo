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
        stripped = line.strip()

        if not stripped or stripped.startswith("```"):
            continue  # skip empty lines and code fences

        # Preserve indented lines or Python assignments
        if (line.startswith(" ") or line.startswith("\t") or re.match(r"^\w+\s*=\s*", line)):
            cleaned.append(line.rstrip("\n"))
        else:
            # Preserve SQL comments or clauses
            if stripped.startswith("--") or re.match(r"^(SELECT|FROM|WHERE|GROUP BY|ORDER BY|WITH|JOIN|HAVING|LIMIT|UNION|INSERT|UPDATE|DELETE|CREATE|DROP|ALTER)\b", stripped, re.IGNORECASE):
                cleaned.append(line.rstrip("\n"))
            else:
                continue  # skip narration or markdown

    return cleaned