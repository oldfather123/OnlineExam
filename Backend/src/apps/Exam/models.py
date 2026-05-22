import uuid

from django.db import models


class Exam(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    paper_id = models.CharField(max_length=64)
    title = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_published = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "exam"

