# OnlineExam Backend

第一阶段已完成内容：
1. 系统数据库准备（模型 + 迁移）
2. 提供前端请求接口
3. 后端进入考试与获取试卷接口

## 1. 数据库准备

默认使用 SQLite（开箱即用）。

```powershell
cd OnlineExam/Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations User Question Paper Exam Score
python manage.py migrate
```

如果要改为 MySQL，先设置环境变量再迁移：

```powershell
$env:DB_ENGINE="mysql"
$env:DB_NAME="examonline"
$env:DB_USER="root"
$env:DB_PASSWORD="你的密码"
$env:DB_HOST="127.0.0.1"
$env:DB_PORT="3306"
python manage.py migrate
```

## 2. 第一阶段接口

### 2.1 进入考试
- 方法：`POST`
- 路径：`/api/exams/enter`
- 请求体：

```json
{
  "exam_id": "考试ID",
  "student_id": "学生ID"
}
```

- 功能：
  - 校验考试是否存在/已发布/在考试时间内
  - 校验考试关联试卷是否存在并已发布
  - 初始化考试记录（`exam_result`），记录开始时间

### 2.2 获取试卷
- 方法：`GET`
- 路径：`/api/papers/online`
- 参数：`paper_id` 或 `exam_id` 二选一

示例：
- `/api/papers/online?paper_id=xxx`
- `/api/papers/online?exam_id=xxx`

- 返回内容：
  - 试卷基本信息
  - 按模块组织的题目数据（题干、选项、题型、分值、顺序）

## 3. 如何验证后端服务成功启动

### 3.1 运行服务

```powershell
python manage.py runserver 127.0.0.1:8000
```

### 3.2 启动成功标志
出现如下信息即成功：
- `Starting development server at http://127.0.0.1:8000/`

### 3.3 接口联调快速验证

1. 先做基础检查（无语法错误）：
```powershell
python manage.py check
```

2. 用 `curl` 验证接口可达（示例）：
```powershell
curl "http://127.0.0.1:8000/api/papers/online?paper_id=test"
```

返回 JSON（即使是业务错误码）说明服务已正常启动并能处理请求。

