"""
第五个测试脚本：学生答题 + 学习分析联通测试

覆盖流程：
1) 创建题目（2道）
2) 创建试卷 + 模块 + 关联题目 + 发布试卷
3) 创建考试并发布
4) 学生进入考试（获得 exam_result_id）
5) 提交答案（action=submit）
6) 客观题自动判分
7) 查询学习分析接口

前置：
- 后端服务已启动
- 存在 student_id（可通过 test_01_create_accounts.py 先创建）

运行：
python tests/test_05_exam_answer_analysis_flow.py --student-id student_demo_id
python tests/test_05_exam_answer_analysis_flow.py --base-url http://127.0.0.1:8000 --student-id <你的学生ID>
"""

import argparse
import json
import sys
import uuid
from datetime import timedelta
from urllib import error, request

DEFAULT_BASE_URL = "http://127.0.0.1:8000"


def http_json(method, url, payload=None):
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = request.Request(url=url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=20) as resp:
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


def create_question(base_url, topic, answer):
    qid = str(uuid.uuid4())
    payload = {
        "id": qid,
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
    return qid


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--student-id", required=True)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    student_id = args.student_id
    seed = str(uuid.uuid4())[:8]

    # 1) 创建题目
    q1 = create_question(base_url, f"学习分析测试题1-{seed}", "A")
    q2 = create_question(base_url, f"学习分析测试题2-{seed}", "B")
    if not q1 or not q2:
        sys.exit(1)

    # 2) 创建试卷 + 模块 + 关联 + 发布
    paper_id = str(uuid.uuid4())
    paper_payload = {
        "id": paper_id,
        "title": f"学习分析试卷-{seed}",
        "description": "自动化流程测试",
        "duration_minutes": 30,
        "total_marks": 100,
        "is_published": False,
    }
    s, d = http_json("POST", f"{base_url}/api/papers", paper_payload)
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 创建试卷 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    module_id = str(uuid.uuid4())
    module_payload = {
        "id": module_id,
        "paper_id": paper_id,
        "title": "模块A",
        "description": "选择题",
    }
    s, d = http_json("POST", f"{base_url}/api/paper-modules", module_payload)
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 创建模块 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    link_payload = {
        "questions_info": [
            {"id": str(uuid.uuid4()), "paper_id": paper_id, "module": module_id, "question_id": q1, "marks": 5},
            {"id": str(uuid.uuid4()), "paper_id": paper_id, "module": module_id, "question_id": q2, "marks": 5},
        ]
    }
    s, d = http_json("POST", f"{base_url}/api/paper-questions", link_payload)
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 关联题目 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    s, d = http_json("POST", f"{base_url}/api/papers/publish", {"id": paper_id})
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 发布试卷 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    # 3) 创建考试并发布
    # 使用当前时间窗口，保证可进入
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    start_time = (now - timedelta(minutes=1)).isoformat()
    end_time = (now + timedelta(minutes=30)).isoformat()

    exam_id = str(uuid.uuid4())
    exam_payload = {
        "id": exam_id,
        "title": f"学习分析考试-{seed}",
        "paper_id": paper_id,
        "start_time": start_time,
        "end_time": end_time,
        "is_published": False,
    }
    s, d = http_json("POST", f"{base_url}/api/exams", exam_payload)
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 创建考试 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    s, d = http_json("POST", f"{base_url}/api/exams/publish/{exam_id}")
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 发布考试 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    # 4) 学生进入考试
    enter_payload = {"exam_id": exam_id, "student_id": student_id}
    s, d = http_json("POST", f"{base_url}/api/exams/enter", enter_payload)
    ok = is_ok(s, d)
    print(f"[{'OK' if ok else 'FAIL'}] 进入考试 -> status={s}")
    if not ok:
        print("  response:", d)
        sys.exit(1)

    exam_result_id = d.get("data", {}).get("exam_result_id")
    if not exam_result_id:
        print("[FAIL] 未获取到 exam_result_id")
        sys.exit(1)

    # 5) 提交答案
    commit_payload = {
        "exam_result_id": exam_result_id,
        "action": "submit",
        "client_ts": 1,
        "answers": [
            {"question_id": q1, "type": "select", "payload": {"value": "A"}},
            {"question_id": q2, "type": "select", "payload": {"value": "C"}},
        ],
    }
    s, d = http_json("POST", f"{base_url}/api/answers/commit", commit_payload)
    ok_commit = is_ok(s, d)
    print(f"[{'OK' if ok_commit else 'FAIL'}] 提交答案 -> status={s}")
    if not ok_commit:
        print("  response:", d)
        sys.exit(1)

    # 6) 自动判分
    s, d = http_json("POST", f"{base_url}/api/reviews/exam-results/{exam_result_id}/auto-grade")
    ok_grade = is_ok(s, d)
    print(f"[{'OK' if ok_grade else 'FAIL'}] 自动判分 -> status={s}")
    if not ok_grade:
        print("  response:", d)
        sys.exit(1)

    # 7) 学习分析
    s, d = http_json("GET", f"{base_url}/api/scores/analyze?student_id={student_id}")
    ok_analyze = is_ok(s, d)
    print(f"[{'OK' if ok_analyze else 'FAIL'}] 学习分析 -> status={s}")
    if not ok_analyze:
        print("  response:", d)
        sys.exit(1)

    analyze_data = d.get("data", {})
    print("  exam_count:", analyze_data.get("exam_count"))
    print("  submitted_count:", analyze_data.get("submitted_count"))
    print("  average_score:", analyze_data.get("average_score"))

    all_ok = ok_commit and ok_grade and ok_analyze
    print("\n=== 学生答题与学习分析联通测试结果 ===")
    print("PASS" if all_ok else "FAIL")
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
