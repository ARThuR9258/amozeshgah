from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from sample_questions.forms import SampleQuestionDashboardForm
from sample_questions.models import SampleQuestion

from .crud_base import ListPageView, ModalFormView, paginate


class SampleListView(ListPageView):
    template_name = 'admin_panel/samples/list.html'
    table_url_name = 'admin_panel:samples_table'
    create_url_name = 'admin_panel:samples_create'
    page_title = 'نمونه سوالات'
    page_subtitle = 'مدیریت فایل‌های PDF نمونه سوال'
    page_icon = 'fa-file-pdf'
    page_accent = 'ap-accent-rose'
    table_id = 'apSamplesTable'
    refresh_event = 'apRefreshSamples'


class SampleTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/samples/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = SampleQuestion.objects.order_by('-created_at')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        active = (self.request.GET.get('active') or '').strip()
        if active in ('1', '0'):
            qs = qs.filter(is_active=(active == '1'))
        page_obj, _ = paginate(self.request, qs, 20)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'active': active}
        return ctx


class SampleCreateView(ModalFormView):
    model = SampleQuestion
    form_class = SampleQuestionDashboardForm
    create_title = 'نمونه سوال جدید'
    form_icon = 'fa-file-pdf'
    form_subtitle = 'آپلود PDF نمونه سوال با عنوان و توضیحات'
    section_icon = 'fa-file-pdf'
    multipart = True
    refresh_event = 'apRefreshSamples'
    list_url_name = 'admin_panel:samples_list'

    def get(self, request):
        return self._render(request, self.form_class(), self.create_title, self.submit_create)

    def post(self, request):
        form = self.form_class(**self.get_form_kwargs(request))
        if form.is_valid():
            form.save()
            return self._success('نمونه سوال ذخیره شد.')
        return self._render(request, form, self.create_title, self.submit_create)


class SampleUpdateView(ModalFormView):
    model = SampleQuestion
    form_class = SampleQuestionDashboardForm
    form_icon = 'fa-file-pdf'
    form_subtitle = 'ویرایش فایل یا مشخصات نمونه سوال'
    section_icon = 'fa-file-pdf'
    multipart = True
    refresh_event = 'apRefreshSamples'
    list_url_name = 'admin_panel:samples_list'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'ویرایش {obj.title}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('نمونه سوال به‌روزرسانی شد.')
        return self._render(request, form, f'ویرایش {obj.title}', self.submit_update)


class SampleDeleteView(ModalFormView):
    model = SampleQuestion
    refresh_event = 'apRefreshSamples'
    list_url_name = 'admin_panel:samples_list'

    def post(self, request, pk):
        self.get_object(pk).delete()
        return self._success('نمونه سوال حذف شد.')
