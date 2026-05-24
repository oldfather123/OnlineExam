"""
第1个独立测试脚本：创建测试账号

功能：
- 创建测试教师账号
- 创建测试学生账号
- 若账号已存在，给出提示并跳过

运行：
python tests/test_01_create_accounts.py
python tests/test_01_create_accounts.py --base-url http://127.0.0.1:8000
"""

import argparse
import json
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


def create_user(base_url, role, username, password, real_name):
    endpoint = "teachers" if role == "teacher" else "students"
    url = f"{base_url}/api/{endpoint}"

    payload = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "real_name": real_name,
    }

    status, data = http_json("POST", url, payload)
    if status in (200, 201) and data.get("code") == 200:
        print(f"[OK] 创建{role}成功: username={username}, password={password}")
        return True

    text = str(data)
    if "unique" in text.lower() or "已存在" in text or "already exists" in text.lower():
        print(f"[INFO] {role}账号已存在，跳过: username={username}")
        return True

    print(f"[FAIL] 创建{role}失败: status={status}, resp={data}")
    return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--teacher-username", default="teacher_demo")
    parser.add_argument("--student-username", default="student_demo")
    parser.add_argument("--password", default="123456")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    print("=== 开始创建测试账号 ===")
    ok_teacher = create_user(base_url, "teacher", args.teacher_username, args.password, "演示教师")
    ok_student = create_user(base_url, "student", args.student_username, args.password, "演示学生")

    if ok_teacher and ok_student:
        print("=== 完成：测试账号可用 ===")
        print(f"教师: {args.teacher_username} / {args.password}")
        print(f"学生: {args.student_username} / {args.password}")
    else:
        print("=== 失败：请检查后端服务和接口 ===")


if __name__ == "__main__":
    main()
