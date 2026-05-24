"""
快速联调脚本：
1) 自动创建教师/学生（若不存在）
2) 测试登录
3) 测试基础接口可用性

用法：
python test_login_and_api.py
python test_login_and_api.py --base-url http://127.0.0.1:8000
"""

import argparse
import json
import sys
import uuid
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


def ensure_user(base_url, role, username, password, real_name):
    list_path = "students" if role == "student" else "teachers"
    create_url = f"{base_url}/api/{list_path}"

    user_id = str(uuid.uuid4())
    payload = {
        "id": user_id,
        "username": username,
        "password": password,
        "real_name": real_name,
    }
    status, data = http_json("POST", create_url, payload)

    if status in (200, 201):
        print(f"[OK] 创建{role}成功: {username}")
        return data.get("data", {}).get("id", user_id)

    msg = str(data)
    if "already exists" in msg or "已存在" in msg or "unique" in msg.lower():
        print(f"[INFO] {role}已存在，跳过创建: {username}")
        return None

    print(f"[WARN] 创建{role}返回状态 {status}: {data}")
    return None


def login(base_url, role, username, password):
    login_path = "auth/student/login" if role == "student" else "auth/teacher/login"
    login_url = f"{base_url}/api/{login_path}"
    status, data = http_json("POST", login_url, {"username": username, "password": password})
    ok = status == 200 and data.get("code") == 200
    print(f"[{'OK' if ok else 'FAIL'}] {role}登录: status={status}, resp={data}")
    return ok


def test_get(base_url, path):
    url = f"{base_url}/api/{path}"
    status, data = http_json("GET", url)
    ok = status == 200 and data.get("code") == 200
    print(f"[{'OK' if ok else 'FAIL'}] GET /api/{path}: status={status}")
    if not ok:
        print("  resp:", data)
    return ok


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    teacher_username = "teacher_demo"
    student_username = "student_demo"
    default_password = "123456"

    ensure_user(base_url, "teacher", teacher_username, default_password, "演示教师")
    ensure_user(base_url, "student", student_username, default_password, "演示学生")

    all_ok = True
    all_ok &= login(base_url, "teacher", teacher_username, default_password)
    all_ok &= login(base_url, "student", student_username, default_password)

    all_ok &= test_get(base_url, "questions")
    all_ok &= test_get(base_url, "papers")
    all_ok &= test_get(base_url, "papers/selector")

    print("\n=== 测试结果 ===")
    print("PASS" if all_ok else "PARTIAL/FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
