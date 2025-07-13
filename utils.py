def patch_missing_imports(code):
    patched = code
    if "sns." in code and "import seaborn" not in code:
        patched = "import seaborn as sns\n" + patched
    if "datetime" in code and "import datetime" not in code and "from datetime" not in code:
        patched = "from datetime import datetime\n" + patched
    if "np." in code and "import numpy" not in code:
        patched = "import numpy as np\n" + patched
    return patched