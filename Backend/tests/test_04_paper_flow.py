"""
第四个测试脚本：组卷流程测试

覆盖流程：
1) 创建题目（2道）
2) 创建试卷
3) 创建试卷模块
4) 关联题目到试卷模块
5) 查询试卷详情
6) 发布试卷
7) 查询发布试卷选择器

前置：
- 后端服务已启动

运行：
python tests/test_04_paper_flow.py
python tests/test_04_paper_flow.py --base-url http://127.0.0.1:8000
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
        with request.urlopen(req, timeout=15) as resp:
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


def create_question(base_url, topic, answer="A"):
    payload = {
        "topic": topic,
        "options": "[\"A\",\"B\",\"C\",\"D\"]",
        "answer": answer,
        "type": "select",
    }
    status, data = http_json("POST", f"{base_url}/api/questions", payload)
    ok = is_ok(status, data)
    print(f"[{'OK' if ok else 'FAIL'}] 创建题目 {topic} -> status={status}")
    if not ok:
        print("  response:", data)
        return None
    return data.get("data", {}).get("id")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    args = parser.parse_args()
    base_url = args.base_url.rstrip("/")

    seed = str(uuid.uuid4())[:8]

    # 1) 创建2道题
    q1 = create_question(base_url, f"组卷测试题1-{seed}", "A")
    q2 = create_question(base_url, f"组卷测试题2-{seed}", "B")
    if not q1 or not q2:
        sys.exit(1)

    # 2) 创建试卷
    create_paper_payload = {
        "title": f"测试试卷-{seed}",
        "description": "自动化测试生成",
        "duration_minutes": 60,
        "total_marks": 100,
        "is_published": False,
    }
    status, data = http_json("POST", f"{base_url}/api/papers", create_paper_payload)
    ok_paper = is_ok(status, data)
    print(f"[{'OK' if ok_paper else 'FAIL'}] 创建试卷 -> status={status}")
    if not ok_paper:
        print("  response:", data)
        sys.exit(1)
    paper_id = data.get("data", {}).get("id")
    if not paper_id:
        print("[FAIL] 创建试卷成功但未返回 paper_id")
        print("  response:", data)
        sys.exit(1)

    # 3) 创建模块
    module_id = str(uuid.uuid4())
    create_module_payload = {
        "id": module_id,
        "paper_id": paper_id,
        "title": "第一模块",
        "description": "基础选择题",
    }
    status, data = http_json("POST", f"{base_url}/api/paper-modules", create_module_payload)
    ok_module = is_ok(status, data)
    print(f"[{'OK' if ok_module else 'FAIL'}] 创建模块 -> status={status}")
    if not ok_module:
        print("  response:", data)
        sys.exit(1)

    # 4) 关联题目
    link_payload = {
        "questions_info": [
            {
                "id": str(uuid.uuid4()),
                "paper_id": paper_id,
                "module": module_id,
                "question_id": q1,
                "marks": 5,
            },
            {
                "id": str(uuid.uuid4()),
                "paper_id": paper_id,
                "module": module_id,
                "question_id": q2,
                "marks": 5,
            },
        ]
    }
    status, data = http_json("POST", f"{base_url}/api/paper-questions", link_payload)
    ok_link = is_ok(status, data)
    print(f"[{'OK' if ok_link else 'FAIL'}] 关联题目 -> status={status}")
    if not ok_link:
        print("  response:", data)
        sys.exit(1)

    # 5) 查询试卷详情
    status, data = http_json("GET", f"{base_url}/api/papers/{paper_id}/detail")
    ok_detail = is_ok(status, data)
    print(f"[{'OK' if ok_detail else 'FAIL'}] 查询试卷详情 -> status={status}")
    if not ok_detail:
        print("  response:", data)

    # 6) 发布试卷
    status, data = http_json("POST", f"{base_url}/api/papers/publish", {"id": paper_id})
    ok_publish = is_ok(status, data)
    print(f"[{'OK' if ok_publish else 'FAIL'}] 发布试卷 -> status={status}")
    if not ok_publish:
        print("  response:", data)

    # 7) 查询选择器
    status, data = http_json("GET", f"{base_url}/api/papers/selector")
    ok_selector = is_ok(status, data)
    print(f"[{'OK' if ok_selector else 'FAIL'}] 查询试卷选择器 -> status={status}")
    if not ok_selector:
        print("  response:", data)

    all_ok = ok_paper and ok_module and ok_link and ok_detail and ok_publish and ok_selector
    print("\n=== 组卷流程测试结果 ===")
    print("PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
