"""依序執行 A、B、C、D 的測試；有測試失敗時以非 0 結束。"""

import subprocess
import sys
from pathlib import Path


project_root = Path(__file__).resolve().parent
test_modules = [
    "tests.test_a",
    "tests.test_b",
    "tests.test_c",
    "tests.test_d",
]
has_failures = False

for test_module in test_modules:
    test_name = test_module.rsplit(".", 1)[1] + ".py"
    test_path = project_root / "tests" / test_name

    try:
        source = test_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"失敗：無法讀取 {test_name}：{error}", flush=True)
        has_failures = True
        continue

    if "def main" not in source:
        print(f"略過：{test_name} 尚無測試", flush=True)
        continue

    print(f"== 執行 {test_name} ==", flush=True)
    result = subprocess.run(
        [sys.executable, "-m", test_module],
        cwd=project_root,
        check=False,
    )
    if result.returncode != 0:
        print(f"失敗：{test_name}（結束碼 {result.returncode}）", flush=True)
        has_failures = True
    else:
        print(f"通過：{test_name}", flush=True)

sys.exit(1 if has_failures else 0)
