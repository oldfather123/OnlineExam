import uuid

from django.db import models


class Questions(models.Model):
    TYPE_CHOICES = (("select", "Select"), ("judge", "Judge"))

    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    topic = models.TextField(max_length=1000)
    options = models.TextField(default="[]")
    answer = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="select")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "questions"


class ErrorArchive(models.Model):
    id = models.CharField(primary_key=True, default=uuid.uuid4, editable=False, max_length=64)
    question_id = models.CharField(max_length=64)
    collector = models.CharField(max_length=64)
    explanation = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "error_archive"

