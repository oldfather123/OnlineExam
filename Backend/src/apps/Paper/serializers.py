from rest_framework import serializers

from .models import Paper, PaperModule, PaperQuestions


class UserInfoMixin:
    def get_user_info(self, user_id):
        pass


class PaperSerializer(serializers.ModelSerializer, UserInfoMixin):
    class Meta:
        model = Paper
        fields = "__all__"


class PaperModuleSerializer(serializers.ModelSerializer, UserInfoMixin):
    class Meta:
        model = PaperModule
        fields = "__all__"


class PaperQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaperQuestions
        fields = "__all__"
