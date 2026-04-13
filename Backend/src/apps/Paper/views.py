from rest_framework.views import APIView


# 教师视图
# 试卷列表管理
class PaperBaseView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, request, **kwargs):
        pass


# 试卷模块管理
class PaperModuleView(APIView):
    def post(self, request):
        pass

    def delete(self, request):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, _, **kwargs):
        pass


# 试卷题目管理
class PaperQuestionsView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, _, **kwargs):
        pass


# 试卷发布
class PaperPublishView(APIView):
    def post(self, request):
        pass

    def delete(self, request):
        pass


# 试卷选择，用于安排考试时选择试卷
class PaperForSelectorView(APIView):
    def get(self, request):
        pass


# 学生视图
# 试卷详情
class PaperDetailView(APIView):
    def get(self, _, **kwargs):
        pass
