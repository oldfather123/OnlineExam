# OnlineExam 后端

## 1. 入口和顶层文件

### 1.1 `api`目录入口文件

- `api/settings.py`
  - Django 全局配置入口。
  - 包含数据库配置、已安装应用、时区、默认主键类型等。

- `api/urls.py`
  - 项目总路由入口。
  - 将 `src/apps` 下各应用路由统一挂载到 `/api/` 前缀。

- `api/asgi.py`
  - ASGI 服务器入口。

- `api/wsgi.py`
  - WSGI 服务器入口。

### 1.2 顶层文件

- `manage.py`
  - Django 命令入口（迁移、启动、检查等）。

- `src/utils/response_utils.py`
  - 统一接口响应结构与状态码封装，用于查看后端服务结果。

---

## 2. 应用功能框架说明

每个应用包含：
- `apps.py` （Django服务调用）
- `models.py`（数据模型）
- `serializers.py`（数据校验与转换）
- `views.py`（接口处理）
- `urls.py`（路由映射）

### 2.1 `src/apps/User`

负责用户的登录、管理、修改。

- 教师/学生登录：
  - `TeacherLoginView`
  - `StudentLoginView`
- 教师/学生用户管理：
  - `TeacherUserView`
  - `StudentUserView`
- 教师/学生密码修改：
  - `TeacherChangePasswordView`
  - `StudentChangePasswordView`

### 2.2 `src/apps/Question`

负责教师题库管理、学生错题集管理。

- 题目管理：`QuestionBaseView`
- 错题集管理：`ErrorArchiveView`
- 组卷可用题目查询：`QuestionsPaperView`
- Agent 辅助选题：`AgentSelectQuestionsView`

### 2.3 `src/apps/Paper`

负责试卷管理、发布，以及学生参加考试时查看试卷。

- 试卷管理：`PaperBaseView`
- 试卷模块管理：`PaperModuleView`
- 试卷题目管理：`PaperQuestionsView`
- 试卷发布：`PaperPublishView`
- 安排考试时试卷选择：`PaperForSelectorView`
- 试卷详情查看：`PaperDetailView`

### 2.4 `src/apps/Exam`

负责考试管理、发布，学生查看考试安排和进入考试。

- 考试管理：`ExamBaseView`
- 考试发布：`ExamPublishView`
- 考试参加情况查询：`ExamAttendView`
- 学生端考试时间查询：`ExamScheduleView`
- 考试详情查看：`ExamDetailView`

### 2.5 `src/apps/Score`

负责成绩管理、答案提交与批改、成绩分析。

- 成绩管理：`ScoreBaseView`
- 成绩详情：`ScoreDetailView`
- 答案获取：`AnswerGetView`
- 答案批改：`AnswerGradeView`
- 答案提交：`AnswerCommitView`
- Agent 辅助成绩分析：`ScoreAnalyzeView`

---

