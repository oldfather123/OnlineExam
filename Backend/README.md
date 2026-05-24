# OnlineExam Backend

当前后端已在重构版基础上完成以下模块：

1. 用户/题库/试卷/考试/成绩基础模型与接口
2. 题库管理（开发端）
3. 组卷管理（模块化组卷 + 发布）
4. 学生端答题保存与提交
5. 学生端学习分析
6. 自动化接口测试脚本（按功能拆分 + 一键串行执行）

---

## 1. 环境准备与启动

默认使用 SQLite（开箱即用）。

```powershell
cd OnlineExam/Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations User Question Paper Exam Score
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

如需切换 MySQL，先设置环境变量再迁移：

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="examonline"
$env:DB_USER="root"
$env:DB_PASSWORD="你的密码"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
python manage.py migrate
```

---

## 2. 已实现接口（按模块）

> 统一前缀：`/api/`

### 2.1 题库管理（Question）

#### 题目 CRUD
- `POST /api/questions`：创建题目
- `GET /api/questions`：分页查询题目（支持 `topic/type/currentPage/pageSize`）
- `GET /api/questions/{id}`：题目详情
- `PUT /api/questions/{id}`：编辑题目
- `DELETE /api/questions/{id}`：删除题目

#### 错题集（Error Archive）
- `POST /api/error-archives`：加入错题集
- `GET /api/error-archives`：按 `collector` 分页查询错题
- `GET /api/error-archives/{id}`：错题记录详情
- `PUT /api/error-archives/{id}`：编辑错题记录
- `DELETE /api/error-archives`：取消错题收藏（通过 `collector + question_id`）

#### 组卷可用题库
- `GET /api/questions/paper-available`：用于试卷选题

#### 智能/随机选题
- `GET /api/questions/agent-select`
- 参数：
  - `randomQuestionType`（可选：`select/judge`）
  - `randomNumber`（必填，数量）

---

### 2.2 组卷管理（Paper）

#### 试卷 CRUD
- `POST /api/papers`
- `GET /api/papers`
- `GET /api/papers/{id}`
- `PUT /api/papers/{id}`
- `DELETE /api/papers/{id}`

#### 试卷模块管理
- `POST /api/paper-modules`
- `PUT /api/paper-modules/{id}`
- `DELETE /api/paper-modules`（请求体传 `id/paper_id`）
- `GET /api/paper-modules/{id}`（`id` 为 `paper_id`）

#### 试题关联（组卷）
- `POST /api/paper-questions`（批量关联，字段 `questions_info`）
- `PUT /api/paper-questions/{id}`
- `DELETE /api/paper-questions/{id}`
- `GET /api/paper-questions/{id}`（`id` 为 `paper_id`）

#### 发布管理
- `POST /api/papers/publish`：发布试卷
- `DELETE /api/papers/publish`：取消发布

#### 试卷选择器
- `GET /api/papers/selector`

#### 试卷详情（按模块聚合）
- `GET /api/papers/{id}/detail`

#### 在线考试取卷
- `GET /api/papers/online?paper_id=xxx`
- 或 `GET /api/papers/online?exam_id=xxx`

---

### 2.3 考试与答题（Exam / Score）

#### 进入考试
- `POST /api/exams/enter`
- 请求体：

```json
{
  "exam_id": "考试ID",
  "student_id": "学生ID"
}
```

#### 答案保存/提交
- `POST /api/answers/commit`：暂存或提交答案
- `GET /api/answers/commit?id=exam_result_id` 或 `GET /api/answers/commit?exam_result_id=...`：查询提交状态

#### 获取考生答案
- `GET /api/answers?exam_result_id=...`

#### 教师评阅相关
- 已实现评阅列表、考生答卷列表、答卷详情、手动评分、自动判分、统计等接口（位于 `Score` 模块）。

#### 学习分析（学生端）
- `GET /api/scores/analyze?student_id=...`
- 返回：
  - 考试总数
  - 已提交数
  - 平均分
  - 成绩趋势
  - 题型得分率统计

---

## 3. 自动化测试脚本

测试脚本统一放在：`Backend/tests/`

### 3.1 按功能拆分脚本
- `test_01_create_accounts.py`：创建教师/学生测试账号
- `test_02_login.py`：教师/学生登录测试
- `test_03_question_crud.py`：题库 CRUD 测试
- `test_04_paper_flow.py`：组卷流程测试（建题->建卷->模块->关联->发布）
- `test_05_exam_answer_analysis_flow.py`：考试答题与学习分析联通测试

### 3.2 一键执行全部测试
- `run_all_tests.py`：串行执行 01~05 并汇总结果

运行示例：

```powershell
cd OnlineExam/Backend
python tests/run_all_tests.py --student-id <你的学生ID>
```

可选参数：
- `--base-url`：默认 `http://127.0.0.1:8000`
- `--stop-on-fail`：遇到失败立即停止

示例：

```powershell
python tests/run_all_tests.py --student-id <你的学生ID> --base-url http://127.0.0.1:8000 --stop-on-fail
```

---

## 4. 架构说明（关于“是否都写一个文件”）

本项目当前采用 Django 常见分层：
- 每个业务 app 一个 `views.py`
- 模型在 `models.py`
- 序列化在 `serializers.py`
- 路由在 `urls.py`

也就是说：
- 不是所有功能都塞在同一个全局文件；
- 而是按业务域（Question / Paper / Score）分别集中在各自 app 的 `views.py`。

这与原仓库的组织方式保持一致（原仓库同样是每个 app 内集中写视图类）。

---

## 5. 快速自检

```powershell
python manage.py check
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

启动成功标志：
- `Starting development server at http://127.0.0.1:8000/`

可快速验证：

```powershell
curl "http://127.0.0.1:8000/api/questions"
```

返回 JSON（即使业务失败）即表示接口可达。
