from rest_framework import serializers

from .models import Student, Teacher


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        abstract = True


class StudentSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        model = Student
        fields = "__all__"


class TeacherSerializer(UserBaseSerializer):
    class Meta(UserBaseSerializer.Meta):
        model = Teacher
        fields = "__all__"
