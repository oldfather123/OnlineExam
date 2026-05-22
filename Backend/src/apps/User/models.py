from django.db import models


class User(models.Model):
    id = models.CharField(primary_key=True, max_length=64)
    username = models.CharField(max_length=64, unique=True)
    password = models.CharField(max_length=128)
    real_name = models.CharField(max_length=64, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Student(User):
    class Meta:
        db_table = "student"

    def __str__(self):
        return f"{self.username}({self.id})"

    @property
    def is_authenticated(self):
        return True


class Teacher(User):
    class Meta:
        db_table = "teacher"

    def __str__(self):
        return f"{self.username}({self.id})"

    @property
    def is_authenticated(self):
        return True

