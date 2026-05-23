# 在线考试系统前端

本目录是在线考试系统的前端工程，技术栈为 Vue 3、Vite、TypeScript、Element Plus、Pinia。前端接口统一通过 `/api` 访问后端，开发环境下由 Vite 代理到 `http://127.0.0.1:8000`。

## 环境要求

- Node.js 18 或更高版本
- npm
- 后端服务已安装依赖并完成数据库迁移

在 PowerShell 中可以先检查：

```powershell
node -v
npm -v
```

如果提示 `npm` 无法识别，说明 Node.js 或 npm 没有加入系统 `Path`。可以安装 Node.js 后重新打开 PowerShell，或使用本机已有的 npm 完整路径执行命令。

## 启动流程

1. 启动后端

   进入后端目录：

   ```powershell
   cd .\OnlineExam\Backend
   ```

   如果使用 conda 环境：

   ```powershell
   conda activate onlineexam
   python manage.py runserver 127.0.0.1:8000
   ```

   后端启动成功后，命令行会停留在运行状态。浏览器直接打开 `http://127.0.0.1:8000/` 出现 Django 的 404 页面是正常的，因为后端只提供 `/api` 接口。
2. 安装前端依赖

   新开一个 PowerShell，进入前端目录：

   ```powershell
   cd .\OnlineExam\Frontend
   npm install
   ```
3. 启动前端开发服务器

   ```powershell
   npm run dev
   ```

   启动后访问：

   ```text
   http://localhost:5173
   ```
4. 构建生产版本

   ```powershell
   npm run build
   ```

   构建产物会生成到 `dist` 目录。

## 常用账号

如果已经执行过后端的演示数据初始化命令，可以使用以下账号测试：

| 身份 | 用户名或 ID | 密码   |
| ---- | ----------- | ------ |
| 教师 | teacher001  | 123456 |
| 学生 | student001  | 123456 |

登录页需要先选择身份，再输入对应账号和密码。

## 功能入口

教师端包含：

- 工作台
- 题库管理
- 试卷管理
- 考试管理
- 阅卷中心
- 用户管理

学生端包含：

- 工作台
- 考试管理
- 成绩分析
- 错题集

学生提交试卷后会自动退出答题页，并进入成绩分析页。选择题、判断题会自动判分，主观题需要教师在阅卷中心手动评分。

## 常见问题

### 登录提示账号或密码错误

先确认后端正在运行，并且数据库中已经创建对应教师或学生账号。后端命令行出现 `401 Unauthorized` 通常表示账号、密码或身份选择不匹配。

### 前端提示 Request failed

优先检查后端是否仍在运行。前端默认请求 `http://127.0.0.1:8000/api`，如果后端没有启动或接口报错，前端会显示请求失败。

### 后端首页显示 Page not found

这是正常现象。后端根路径 `/` 没有页面，接口路径以 `/api` 开头，前端页面需要访问 `http://localhost:5173`。

### 修改代码后页面没有变化

先刷新浏览器。如果修改的是后端代码，需要停止后端服务并重新执行：

```powershell
python manage.py runserver 127.0.0.1:8000
```

如果修改的是前端代码，Vite 通常会自动热更新；不生效时可以停止后重新运行：

```powershell
npm run dev
```
