from rest_framework.views import APIView


# 教师视图
# 成绩列表管理
class ScoreBaseView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, request, **kwargs):
        pass


# 回答获取
class AnswerGetView(APIView):
    def get(self, request):
        pass


# 回答批改
class AnswerGradeView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, request, **kwargs):
        pass


# 学生视图
# 成绩详情
class ScoreDetailView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass
    
    def get(self, request):
        pass


# 回答提交
class AnswerCommitView(APIView):
    def post(self, request):
        pass

    def get(self, request, **kwargs):
        pass


# Agent辅助成绩分析
class ScoreAnalyzeView(APIView):
    def get(self, request):
        pass