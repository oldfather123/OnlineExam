from rest_framework import serializers

from .models import Exam


class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exam
        fields = "__all__"


class ExamEnterRequestSerializer(serializers.Serializer):
    exam_id = serializers.CharField(max_length=64)
    student_id = serializers.CharField(max_length=64)
