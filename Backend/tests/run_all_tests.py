"""
一键执行全部测试脚本

执行顺序：
1) test_01_create_accounts.py
2) test_02_login.py
3) test_03_question_crud.py
4) test_04_paper_flow.py
5) test_05_exam_answer_analysis_flow.py

说明：
- 第5个脚本需要 student_id，请通过 --student-id 传入
- 若中途某个脚本失败，默认继续执行并在最后汇总

用法：
python tests/run_all_tests.py --student-id <你的学生ID>
python tests/run_all_tests.py --student-id <你的学生ID> --base-url http://127.0.0.1:8000
python tests/run_all_tests.py --student-id <你的学生ID> --stop-on-fail
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_script(script_path, args):
    cmd = [sys.executable, str(script_path), *args]
    print(f"\n>>> 运行: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    ok = result.returncode == 0
    print(f"<<< 结果: {'PASS' if ok else 'FAIL'} (exit_code={result.returncode})")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--student-id", required=True)
    parser.add_argument("--stop-on-fail", action="store_true")
    args = parser.parse_args()

    tests_dir = Path(__file__).resolve().parent

    plan = [
        (tests_dir / "test_01_create_accounts.py", ["--base-url", args.base_url]),
        (tests_dir / "test_02_login.py", ["--base-url", args.base_url]),
        (tests_dir / "test_03_question_crud.py", ["--base-url", args.base_url]),
        (tests_dir / "test_04_paper_flow.py", ["--base-url", args.base_url]),
        (
            tests_dir / "test_05_exam_answer_analysis_flow.py",
            ["--base-url", args.base_url, "--student-id", args.student_id],
        ),
    ]

    results = []
    for script, script_args in plan:
        ok = run_script(script, script_args)
        results.append((script.name, ok))
        if not ok and args.stop_on_fail:
            break

    print("\n===== 测试汇总 =====")
    passed = 0
    for name, ok in results:
        print(f"- {name}: {'PASS' if ok else 'FAIL'}")
        if ok:
            passed += 1

    total = len(results)
    print(f"\n总计: {passed}/{total} 通过")

    if passed == total:
        print("全部测试通过")
        sys.exit(0)
    else:
        print("存在失败项，请查看上方日志")
        sys.exit(1)


if __name__ == "__main__":
    main()
