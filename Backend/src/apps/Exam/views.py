from rest_framework.views import APIView


# 教师视图
# 考试列表管理
class ExamBaseView(APIView):
    def post(self, request):
        pass

    def delete(self, _, **kwargs):
        pass

    def put(self, request, **kwargs):
        pass

    def get(self, request):
        pass


# 考试发布
class ExamPublishView(APIView):
    def post(self, _, **kwargs):
        pass

    def delete(self, _, **kwargs):
        pass


# 考试参加情况
class ExamAttendView(APIView):
    def get(self, request):
        pass


# 学生视图
# 考试时间查询
class ExamScheduleView(APIView):
    def get(self, request):
        pass


# 考试详情查看
class ExamDetailView(APIView):
    def get(self, request):
        pass
