import json

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.apps.Exam.models import Exam
from src.apps.Paper.models import Paper, PaperModule, PaperQuestions
from src.apps.Question.models import Questions
from src.apps.User.models import Student, Teacher


class Command(BaseCommand):
    help = "Create demo users, questions, paper, and an active exam."

    def handle(self, *args, **options):
        teacher, _ = Teacher.objects.update_or_create(
            id="teacher001",
            defaults={
                "username": "teacher",
                "password": "123456",
                "real_name": "教师账号",
            },
        )
        student, _ = Student.objects.update_or_create(
            id="student001",
            defaults={
                "username": "student",
                "password": "123456",
                "real_name": "学生账号",
            },
        )

        question_specs = [
            {
                "id": "demo-q1",
                "topic": "Django 中用于定义数据表结构的组件是？",
                "options": ["Model", "View", "Template", "Router"],
                "answer": "Model",
                "type": "select",
            },
            {
                "id": "demo-q2",
                "topic": "HTTP 状态码 200 表示请求成功。",
                "options": ["正确", "错误"],
                "answer": "正确",
                "type": "judge",
            },
            {
                "id": "demo-q3",
                "topic": "Vue 3 中常用的状态管理库是？",
                "options": ["Pinia", "Django", "SQLite", "Pandas"],
                "answer": "Pinia",
                "type": "select",
            },
            {
                "id": "demo-q4",
                "topic": "Vite 只能用于后端 Django 项目。",
                "options": ["正确", "错误"],
                "answer": "错误",
                "type": "judge",
            },
        ]

        questions = []
        for spec in question_specs:
            question, _ = Questions.objects.update_or_create(
                id=spec["id"],
                defaults={
                    "topic": spec["topic"],
                    "options": json.dumps(spec["options"], ensure_ascii=False),
                    "answer": spec["answer"],
                    "type": spec["type"],
                },
            )
            questions.append(question)

        paper, _ = Paper.objects.update_or_create(
            id="demo-paper-001",
            defaults={
                "title": "在线考试系统演示试卷",
                "description": "用于验证题库、组卷、考试、提交和阅卷流程。",
                "duration_minutes": 60,
                "total_marks": 100,
                "is_published": True,
            },
        )

        select_module, _ = PaperModule.objects.update_or_create(
            id="demo-module-select",
            defaults={
                "paper_id": paper.id,
                "title": "选择题",
                "description": "基础概念选择题",
                "sequence_number": 1,
            },
        )
        judge_module, _ = PaperModule.objects.update_or_create(
            id="demo-module-judge",
            defaults={
                "paper_id": paper.id,
                "title": "判断题",
                "description": "基础概念判断题",
                "sequence_number": 2,
            },
        )

        links = [
            ("demo-pq-1", questions[0], select_module, 25, 1),
            ("demo-pq-2", questions[2], select_module, 25, 2),
            ("demo-pq-3", questions[1], judge_module, 25, 1),
            ("demo-pq-4", questions[3], judge_module, 25, 2),
        ]
        for link_id, question, module, marks, sequence in links:
            PaperQuestions.objects.update_or_create(
                id=link_id,
                defaults={
                    "paper_id": paper.id,
                    "question_id": question.id,
                    "module": module.id,
                    "marks": marks,
                    "sequence_number": sequence,
                },
            )

        now = timezone.now()
        exam, _ = Exam.objects.update_or_create(
            id="demo-exam-001",
            defaults={
                "paper_id": paper.id,
                "title": "在线考试系统演示考试",
                "start_time": now - timezone.timedelta(minutes=10),
                "end_time": now + timezone.timedelta(days=7),
                "is_published": True,
                "is_deleted": False,
            },
        )

        self.stdout.write(self.style.SUCCESS("Demo data ready."))
        self.stdout.write(f"Teacher: {teacher.username} / 123456")
        self.stdout.write(f"Student: {student.username} / 123456")
        self.stdout.write(f"Exam ID: {exam.id}")
