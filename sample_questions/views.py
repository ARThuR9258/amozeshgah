from django.views.generic import ListView
from django.http import Http404, FileResponse, HttpResponse
from django.utils import timezone
from django.conf import settings
from django.shortcuts import get_object_or_404
import os
from wsgiref.util import FileWrapper
from .models import SampleQuestion

class SampleQuestionListView(ListView):
    model = SampleQuestion
    template_name = 'sample_questions/question_list.html'
    context_object_name = 'question_papers'
    paginate_by = 10
    
    def get_queryset(self):
        return SampleQuestion.objects.filter(is_active=True).order_by('-created_at')


def download_question_paper(request, pk):
    question_paper = get_object_or_404(SampleQuestion, pk=pk, is_active=True)
    if question_paper.pdf_file:
        file_path = question_paper.pdf_file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                return response
    raise Http404("فایل درخواستی یافت نشد")


class QuestionListDashboard(ListView):
    model = SampleQuestion
    template_name = 'sample_questions/question_list_dashboard.html'
    context_object_name = 'questions'


    def get_queryset(self):
        questions = SampleQuestion.objects.all()
        return questions


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
