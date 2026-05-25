"""
一键执行全部测试脚本

执行顺序：
1) test_01_create_accounts.py
2) test_02_login.py
3) test_03_question_crud.py
4) test_04_paper_flow.py
5) test_05_exam_answer_analysis_flow.py

增强：
- 启动前先探测后端可达性（/api/questions）
- 若 base-url 不可用，自动尝试 8000/8001
- --student-id 支持传学生ID或用户名（如 student_demo）

用法：
python tests/run_all_tests.py --student-id <学生ID或用户名>
python tests/run_all_tests.py --student-id student_demo --base-url http://127.0.0.1:8001
python tests/run_all_tests.py --student-id <学生ID> --stop-on-fail
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from urllib import error, request


def http_get(url, timeout=3):
    req = request.Request(url=url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            data = json.loads(body) if body else {}
            return resp.status, data
    except Exception:
        return None, None


def resolve_base_url(base_url):
    candidates = [base_url.rstrip("/")]
    for fallback in ["http://127.0.0.1:8000", "http://127.0.0.1:8001"]:
        if fallback not in candidates:
            candidates.append(fallback)

    for c in candidates:
        status, data = http_get(f"{c}/api/questions")
        if status == 200 and isinstance(data, dict) and "code" in data:
            return c
    return None


def resolve_student_id(base_url, student_identity):
    # 如果看起来像 UUID，直接使用
    if "-" in student_identity and len(student_identity) >= 32:
        return student_identity

    status, data = http_get(f"{base_url}/api/students")
    if status != 200 or not isinstance(data, dict):
        return None

    rows = data.get("data", {}).get("data", [])
    for item in rows:
        if item.get("username") == student_identity or item.get("id") == student_identity:
            return item.get("id")
    return None


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
    parser.add_argument("--student-id", required=True, help="学生ID或用户名（例如 student_demo）")
    parser.add_argument("--stop-on-fail", action="store_true")
    args = parser.parse_args()

    active_base_url = resolve_base_url(args.base_url)
    if not active_base_url:
        print("[FAIL] 后端不可达，请先启动 runserver（8000 或 8001）")
        sys.exit(1)

    print(f"[INFO] 使用后端地址: {active_base_url}")

    student_id = resolve_student_id(active_base_url, args.student_id)
    if not student_id:
        print(f"[FAIL] 无法解析学生标识: {args.student_id}")
        print("请传入真实 student.id，或可被 /api/students 查到的 username")
        sys.exit(1)

    print(f"[INFO] 使用 student_id: {student_id}")

    tests_dir = Path(__file__).resolve().parent
    plan = [
        (tests_dir / "test_01_create_accounts.py", ["--base-url", active_base_url]),
        (tests_dir / "test_02_login.py", ["--base-url", active_base_url]),
        (tests_dir / "test_03_question_crud.py", ["--base-url", active_base_url]),
        (tests_dir / "test_04_paper_flow.py", ["--base-url", active_base_url]),
        (
            tests_dir / "test_05_exam_answer_analysis_flow.py",
            ["--base-url", active_base_url, "--student-id", student_id],
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

    print("存在失败项，请查看上方日志")
    sys.exit(1)


if __name__ == "__main__":
    main()
