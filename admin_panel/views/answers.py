from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from quizbuilder_module.models import UserAnswer

from .crud_base import ListPageView, paginate


class AnswerListView(ListPageView):
    template_name = 'admin_panel/answers/list.html'
    table_url_name = 'admin_panel:answers_table'
    create_url_name = ''
    page_title = 'پاسخ‌های کاربران'
    page_subtitle = 'مشاهده پاسخ‌های ثبت‌شده در آزمون‌ها'
    page_icon = 'fa-clipboard-check'
    page_accent = 'ap-accent-emerald'
    table_id = 'apAnswersTable'
    refresh_event = 'apRefreshAnswers'


class AnswerTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/answers/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = UserAnswer.objects.select_related(
            'session', 'session__user', 'question',
        ).order_by('-answered_at', '-id')
        if q:
            qs = qs.filter(
                Q(question__text__icontains=q)
                | Q(session__user__phone_number__icontains=q)
            )
        correct = self.request.GET.get('correct')
        if correct == '1':
            qs = qs.filter(is_correct=True)
        elif correct == '0':
            qs = qs.filter(is_correct=False)

        page_obj, _ = paginate(self.request, qs, 30)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'correct': correct or ''}
        return ctx
