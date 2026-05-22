import uuid

from django.db import models


class Score(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_id = models.CharField(max_length=64, db_index=True)
    student_id = models.CharField(max_length=64, db_index=True)
    result_mark = models.FloatField(default=0)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField(null=True, blank=True)
    ending_status = models.BooleanField(default=True)

    # autosave/submit consistency control
    last_client_ts = models.BigIntegerField(default=0)
    last_save_at = models.DateTimeField(null=True, blank=True)
    submit_status = models.BooleanField(default=False, db_index=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    submitted_client_ts = models.BigIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam_result"
        constraints = [
            models.UniqueConstraint(fields=["exam_id", "student_id"], name="uniq_exam_student")
        ]
        indexes = [
            models.Index(fields=["exam_id", "submit_status"], name="idx_score_exam_submit"),
            models.Index(fields=["exam_id", "student_id"], name="idx_score_exam_student"),
        ]


class Answer(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_result_id = models.CharField(max_length=64, db_index=True)
    question_id = models.CharField(max_length=64, db_index=True)
    answer_type = models.CharField(max_length=32, default="subjective")
    # unified payload: {"value": ..., "meta": {...}}
    answer_payload = models.JSONField(default=dict)
    solution = models.TextField(blank=True, default="")
    last_client_ts = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "answer"
        constraints = [
            models.UniqueConstraint(
                fields=["exam_result_id", "question_id"],
                name="uniq_answer_exam_result_question",
            )
        ]
        indexes = [
            models.Index(fields=["exam_result_id", "question_id"], name="idx_answer_result_q"),
        ]


class ScoreDetail(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    exam_result_id = models.CharField(max_length=64, db_index=True)
    question_id = models.CharField(max_length=64, db_index=True)
    mark = models.FloatField(default=0)
    comment = models.TextField(blank=True, default="")
    graded_by = models.CharField(max_length=64, blank=True, default="")
    graded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "score_detail"
        constraints = [
            models.UniqueConstraint(
                fields=["exam_result_id", "question_id"],
                name="uniq_score_detail_exam_result_question",
            )
        ]
        indexes = [
            models.Index(fields=["exam_result_id", "question_id"], name="idx_detail_result_q"),
        ]
