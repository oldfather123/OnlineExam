from rest_framework import serializers

from .models import Score, Answer, ScoreDetail


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = "__all__"


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = "__all__"


class ScoreDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScoreDetail
        fields = "__all__"
