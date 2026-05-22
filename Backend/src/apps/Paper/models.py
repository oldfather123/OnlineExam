import uuid

from django.db import models


class Paper(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    duration_minutes = models.PositiveIntegerField(default=60)
    total_marks = models.FloatField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "paper"


class PaperQuestions(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    paper_id = models.CharField(max_length=64)
    question_id = models.CharField(max_length=64)
    sequence_number = models.PositiveIntegerField(default=1)
    marks = models.FloatField(default=0)
    module = models.CharField(max_length=64, blank=True, default="")

    class Meta:
        db_table = "paper_questions"


class PaperModule(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    paper_id = models.CharField(max_length=64)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    sequence_number = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = "paper_module"

