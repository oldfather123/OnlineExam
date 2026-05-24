"""
第1个独立测试脚本：创建测试账号（学生/教师）

用法：
1) 先启动后端服务
   python manage.py runserver

2) 执行脚本
   python test_create_accounts.py
   python test_create_accounts.py --base-url http://127.0.0.1:8000
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


def create_teacher(base_url, username="teacher_demo", password="123456", real_name="演示教师"):
    url = f"{base_url}/api/teachers"
    payload = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "real_name": real_name,
    }
    return http_json("POST", url, payload)


def create_student(base_url, username="student_demo", password="123456", real_name="演示学生"):
    url = f"{base_url}/api/students"
    payload = {
        "id": str(uuid.uuid4()),
        "username": username,
        "password": password,
        "real_name": real_name,
    }
    return http_json("POST", url, payload)


def print_result(role, status, resp):
    success = status in (200, 201) and resp.get("code") == 200
    if success:
        print(f"[OK] 创建{role}成功")
        print("     返回:", resp)
        return

    text = str(resp)
    if "already exists" in text or "已存在" in text or "unique" in text.lower():
        print(f"[INFO] {role}已存在，跳过")
        print("       返回:", resp)
    else:
        print(f"[FAIL] 创建{role}失败: status={status}")
        print("       返回:", resp)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="后端地址，例如 http://127.0.0.1:8000")
    parser.add_argument("--teacher-username", default="teacher_demo")
    parser.add_argument("--student-username", default="student_demo")
    parser.add_argument("--password", default="123456")
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    print("=== 创建测试教师账号 ===")
    t_status, t_resp = create_teacher(base_url, args.teacher_username, args.password)
    print_result("教师", t_status, t_resp)

    print("\n=== 创建测试学生账号 ===")
    s_status, s_resp = create_student(base_url, args.student_username, args.password)
    print_result("学生", s_status, s_resp)

    print("\n完成：你现在可以用以下账号登录测试")
    print(f"教师: {args.teacher_username} / {args.password}")
    print(f"学生: {args.student_username} / {args.password}")


if __name__ == "__main__":
    main()
