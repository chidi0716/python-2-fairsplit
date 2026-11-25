"""依序執行 A、B、C、D 的測試；任何測試失敗時以非 0 結束。"""

import ast
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
        parsed_test = ast.parse(source, filename=str(test_path))
    except (OSError, SyntaxError) as error:
        print(f"失敗：無法讀取或解析 {test_name}：{error}", flush=True)
        has_failures = True
        continue

    executable_statements = [
        statement
        for statement in parsed_test.body
        if not (
            isinstance(statement, ast.Expr)
            and isinstance(statement.value, ast.Constant)
            and isinstance(statement.value.value, str)
        )
    ]
    if not executable_statements:
        print(f"失敗：{test_name} 只有註解或空白，尚無可執行測試", flush=True)
        has_failures = True
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
