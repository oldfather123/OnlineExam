"""
第二个测试脚本：登录功能测试

用途：
1) 测试教师登录接口
2) 测试学生登录接口

前置：
- 后端服务已启动
- 已先运行 test_01_create_accounts.py（或你已手动创建账号）

用法：
python test_02_login.py
python test_02_login.py --base-url http://127.0.0.1:8000
python test_02_login.py --teacher-username teacher_demo --student-username student_demo --password 123456
"""

import argparse
import json
import sys
from urllib import error, request


DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def http_json(method, url, payload=None):
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url=url, data=data, headers=headers, method=method)

    try:
        with request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8")
            return resp.status, json.loads(body) if body else {}
    except error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        try:
            parsed = json.loads(body) if body else {}
        except Exception:
            parsed = {"raw": body}
        return e.code, parsed


def login(base_url, role, username, password):
    path = "auth/teacher/login" if role == "teacher" else "auth/student/login"
    url = f"{base_url}/api/{path}"

    payload = {
        "username": username,
        "password": password,
    }

    status, data = http_json("POST", url, payload)
    ok = status == 200 and data.get("code") == 200

    print(f"[{'OK' if ok else 'FAIL'}] {role} 登录 -> status={status}")
    print(f"  request: {payload}")
    print(f"  response: {data}")
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--teacher-username", default="teacher_demo")
    parser.add_argument("--student-username", default="student_demo")
    parser.add_argument("--password", default="123456")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    teacher_ok = login(base_url, "teacher", args.teacher_username, args.password)
    student_ok = login(base_url, "student", args.student_username, args.password)

    print("\n=== 登录测试结果 ===")
    all_ok = teacher_ok and student_ok
    print("PASS" if all_ok else "FAIL")

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
