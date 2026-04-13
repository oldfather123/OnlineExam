from django.db import models


class User(models.Model):
    class Meta:
        abstract = True


class Student(User):
    def __str__(self):
        pass

    @property
    def is_authenticated(self):
        pass


class Teacher(User):
    def __str__(self):
        pass

    @property
    def is_authenticated(self):
        pass
