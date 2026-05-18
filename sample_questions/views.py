import os

from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from account_module.decorators import AdminRequiredMixin
from amozeshga.dashboard_list import build_pagination_query
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
    raise Http404('فایل درخواستی یافت نشد')


def view_question_paper(request, pk):
    question_paper = get_object_or_404(SampleQuestion, pk=pk, is_active=True)
    if question_paper.pdf_file:
        file_path = question_paper.pdf_file.path
        if os.path.exists(file_path):
            with open(file_path, 'rb') as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type='application/pdf')
                response['Content-Disposition'] = f'inline; filename="{os.path.basename(file_path)}"'
                return response
    raise Http404('فایل درخواستی یافت نشد')


class QuestionListDashboard(AdminRequiredMixin, ListView):
    model = SampleQuestion
    template_name = 'sample_questions/question_list_dashboard.html'
    context_object_name = 'questions'
    paginate_by = 20

    def get_queryset(self):
        qs = SampleQuestion.objects.all().order_by('-created_at')
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        active = self.request.GET.get('active')
        if active == '1':
            qs = qs.filter(is_active=True)
        elif active == '0':
            qs = qs.filter(is_active=False)
        self._pagination_query = build_pagination_query(self.request)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        context['active_filter'] = self.request.GET.get('active', '')
        context['pagination_query'] = getattr(self, '_pagination_query', '')
        context['stats'] = {
            'total': SampleQuestion.objects.count(),
            'active': SampleQuestion.objects.filter(is_active=True).count(),
        }
        return context
