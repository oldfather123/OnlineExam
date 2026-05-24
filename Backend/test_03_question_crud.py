"""
第三个测试脚本：题库 CRUD 测试

用途：
1) 创建题目 POST /api/questions
2) 查询题目详情 GET /api/questions/{id}
3) 修改题目 PUT /api/questions/{id}
4) 题目列表 GET /api/questions
5) 删除题目 DELETE /api/questions/{id}

前置：
- 后端服务已启动

用法：
python test_03_question_crud.py
python test_03_question_crud.py --base-url http://127.0.0.1:8000
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


def is_ok(status, data):
    return status == 200 and data.get("code") == 200


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")

    question_id = str(uuid.uuid4())
    topic_seed = question_id[:8]

    # 1) 创建题目
    create_payload = {
        "id": question_id,
        "topic": f"测试题目-{topic_seed}",
        "options": "[\"A\",\"B\",\"C\",\"D\"]",
        "answer": "A",
        "type": "select",
    }
    status, data = http_json("POST", f"{base_url}/api/questions", create_payload)
    ok_create = is_ok(status, data)
    print(f"[{'OK' if ok_create else 'FAIL'}] 创建题目 -> status={status}")
    if not ok_create:
        print("  response:", data)
        sys.exit(1)

    # 2) 查询详情
    status, data = http_json("GET", f"{base_url}/api/questions/{question_id}")
    ok_get = is_ok(status, data)
    print(f"[{'OK' if ok_get else 'FAIL'}] 查询题目详情 -> status={status}")

    # 3) 修改题目
    update_payload = {
        "topic": f"测试题目-已更新-{topic_seed}",
        "answer": "B",
    }
    status, data = http_json("PUT", f"{base_url}/api/questions/{question_id}", update_payload)
    ok_put = is_ok(status, data)
    print(f"[{'OK' if ok_put else 'FAIL'}] 修改题目 -> status={status}")

    # 4) 查询列表（带过滤）
    status, data = http_json("GET", f"{base_url}/api/questions?topic={topic_seed}&currentPage=1&pageSize=10")
    ok_list = is_ok(status, data)
    print(f"[{'OK' if ok_list else 'FAIL'}] 查询题目列表 -> status={status}")

    # 5) 删除题目
    status, data = http_json("DELETE", f"{base_url}/api/questions/{question_id}")
    ok_delete = is_ok(status, data)
    print(f"[{'OK' if ok_delete else 'FAIL'}] 删除题目 -> status={status}")

    all_ok = ok_create and ok_get and ok_put and ok_list and ok_delete
    print("\n=== 题库 CRUD 测试结果 ===")
    print("PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
