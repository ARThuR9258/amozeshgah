from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from quizbuilder_module.exam_services import build_result_summary
from quizbuilder_module.helpers import ExamSessionStatus
from quizbuilder_module.models import ExamSession

from .crud_base import ListPageView, paginate


class SessionListView(ListPageView):
    template_name = 'admin_panel/sessions/list.html'
    table_url_name = 'admin_panel:sessions_table'
    create_url_name = ''
    page_title = 'جلسات آزمون'
    page_subtitle = 'مشاهده و تحلیل آزمون‌های کاربران'
    page_icon = 'fa-user-check'
    page_accent = 'ap-accent-cyan'
    table_id = 'apSessionsTable'
    refresh_event = 'apRefreshSessions'


class SessionTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/sessions/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        status = (self.request.GET.get('status') or '').strip()
        qs = ExamSession.objects.select_related('user').order_by('-started_at')
        if q:
            qs = qs.filter(Q(user__phone_number__icontains=q) | Q(user__username__icontains=q))
        if status:
            qs = qs.filter(status=status)
        page_obj, _ = paginate(self.request, qs, 25)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'status': status}
        ctx['status_choices'] = ExamSessionStatus.CHOICES
        return ctx


class SessionDetailView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/sessions/detail.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        session = ExamSession.objects.select_related('user').get(pk=kwargs['pk'])
        ctx['session'] = session
        ctx['answers'] = session.answers.select_related('question').order_by('question_id')
        if session.status != ExamSessionStatus.IN_PROGRESS:
            ctx['summary'] = build_result_summary(session)
        return ctx
