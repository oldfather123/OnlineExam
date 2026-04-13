from rest_framework import serializers

from .models import Questions, ErrorArchive


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Questions
        fields = "__all__"


class ErrorArchiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = ErrorArchive
        fields = "__all__"
