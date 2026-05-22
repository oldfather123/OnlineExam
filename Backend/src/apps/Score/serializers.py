from rest_framework import serializers

from .models import Answer, Score, ScoreDetail


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


class UnifiedAnswerItemSerializer(serializers.Serializer):
    question_id = serializers.CharField(max_length=64)
    type = serializers.ChoiceField(choices=["select", "blank", "subjective", "judge"], required=False, default="subjective")
    payload = serializers.JSONField(required=False, default=dict)


class AnswerCommitRequestSerializer(serializers.Serializer):
    exam_result_id = serializers.CharField(max_length=64, required=False, allow_blank=False)
    exam_id = serializers.CharField(max_length=64, required=False, allow_blank=False)
    student_id = serializers.CharField(max_length=64, required=False, allow_blank=False)
    action = serializers.ChoiceField(choices=["save", "submit"], required=False, default="save")
    client_ts = serializers.IntegerField(min_value=1)
    answers = UnifiedAnswerItemSerializer(many=True, required=False, default=list)

    def validate(self, attrs):
        if not attrs.get("exam_result_id"):
            if not attrs.get("exam_id") or not attrs.get("student_id"):
                raise serializers.ValidationError("exam_result_id 与 (exam_id, student_id) 至少提供一组")
        return attrs


class AnswerCommitStatusQuerySerializer(serializers.Serializer):
    exam_result_id = serializers.CharField(max_length=64)


class ReviewScoreItemSerializer(serializers.Serializer):
    question_id = serializers.CharField(max_length=64)
    mark = serializers.FloatField(min_value=0)
    comment = serializers.CharField(required=False, allow_blank=True, default="")


class ReviewScoreProcessRequestSerializer(serializers.Serializer):
    grader_id = serializers.CharField(max_length=64, required=False, allow_blank=True, default="")
    finalize = serializers.BooleanField(required=False, default=False)
    items = ReviewScoreItemSerializer(many=True)
