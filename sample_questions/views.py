import os

from django.conf import settings
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView, ListView

from seo_module.mixins import SEOMixin
from seo_module.utils import build_seo
from account_module.decorators import AdminRequiredMixin
from amozeshga.dashboard_list import build_pagination_query
from .models import SampleQuestion


class SampleQuestionListView(ListView):
    model = SampleQuestion
    template_name = 'sample_questions/question_list.html'
    context_object_name = 'question_papers'
    paginate_by = 9

    def get_queryset(self):
        qs = SampleQuestion.objects.filter(is_active=True)
        q = self.request.GET.get('q', '').strip()
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))

        sort = self.request.GET.get('sort', 'newest')
        if sort == 'oldest':
            qs = qs.order_by('created_at')
        elif sort == 'title':
            qs = qs.order_by('title')
        else:
            qs = qs.order_by('-created_at')

        self._browse_query = build_pagination_query(self.request, exclude=('page',))
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        search_query = self.request.GET.get('q', '').strip()
        sort = self.request.GET.get('sort', 'newest')
        result_count = context['paginator'].count if context.get('paginator') else 0

        context.update({
            'search_query': search_query,
            'sort': sort,
            'result_count': result_count,
            'has_active_filters': bool(search_query) or sort != 'newest',
            'browse_query': getattr(self, '_browse_query', ''),
            'toolbar_action': '',
            'search_placeholder': 'جستجو در عنوان یا توضیحات...',
            'sort_options': [
                ('newest', 'جدیدترین'),
                ('oldest', 'قدیمی‌ترین'),
                ('title', 'عنوان (الفبا)'),
            ],
        })
        context['seo'] = build_seo(self.request, override={
            'canonical': self.request.build_absolute_uri('/questions/'),
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'نمونه سوالات', 'url': None},
            ],
        })
        return context


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


class SampleQuestionDetailView(SEOMixin, DetailView):
    """صفحه HTML نمونه سوال — SEO Friendly."""

    model = SampleQuestion
    template_name = 'sample_questions/question_detail.html'
    context_object_name = 'paper'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return SampleQuestion.objects.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        paper = self.object
        context['seo'] = build_seo(self.request, override={
            'title': f'{paper.title} | نمونه سوال آیین نامه — آیین‌یار',
            'description': paper.description or f'دانلود {paper.title} — نمونه سوالات آیین نامه رانندگی به‌روز.',
            'keywords': 'نمونه سوال آیین نامه, سوالات آیین نامه رانندگی, دانلود PDF آیین نامه',
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'نمونه سوالات', 'url': '/questions/'},
                {'name': paper.title, 'url': paper.get_absolute_url()},
            ],
        })
        context['related_papers'] = SampleQuestion.objects.filter(
            is_active=True,
        ).exclude(pk=paper.pk)[:4]
        return context


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
