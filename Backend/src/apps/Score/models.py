import uuid

from django.db import models


class Score(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_id = models.CharField(max_length=64)
    student_id = models.CharField(max_length=64)
    result_mark = models.FloatField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    ending_status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_result"
        constraints = [
            models.UniqueConstraint(fields=["exam_id", "student_id"], name="uniq_exam_student")
        ]


class Answer(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_result_id = models.CharField(max_length=64)
    question_id = models.CharField(max_length=64)
    solution = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "answer"


class ScoreDetail(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_result_id = models.CharField(max_length=64)
    question_id = models.CharField(max_length=64)
    mark = models.FloatField(default=0)

    class Meta:
        db_table = "score_detail"

