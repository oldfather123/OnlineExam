from rest_framework.views import APIView


# 教师视图
# 题库列表管理
class QuestionBaseView(APIView):
    def post(self, request):
        pass

    def put(self, request, **kwargs):
        pass

    def delete(self, _, **kwargs):
        pass

    def get(self, request, **kwargs):
        pass


# 试卷可用题库管理
class QuestionsPaperView(APIView):
    def get(self, request):
        pass


# Agent辅助选择题目
class AgentSelectQuestionsView(APIView):
    def get(self, request):
        pass


# 学生视图
# 错题集管理
class ErrorArchiveView(APIView):
    def post(self, request):
        pass

    def delete(self, request):
        pass

    def get(self, request, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass
