from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from quizbuilder_module.forms import QuestionForm
from quizbuilder_module.models import Category, Question

from .crud_base import ListPageView, ModalFormView, paginate


class QuestionListView(ListPageView):
    template_name = 'admin_panel/questions/list.html'
    table_url_name = 'admin_panel:questions_table'
    create_url_name = 'admin_panel:questions_create'
    page_title = 'بانک سوالات'
    page_subtitle = 'مدیریت سوالات آزمون با تصویر و گزینه‌ها'
    page_icon = 'fa-file-alt'
    page_accent = 'ap-accent-violet'
    table_id = 'apQuestionsTable'
    refresh_event = 'apRefreshQuestions'


class QuestionTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/questions/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        category_id = (self.request.GET.get('category') or '').strip()
        difficulty = (self.request.GET.get('difficulty') or '').strip()
        active = (self.request.GET.get('active') or '').strip()

        qs = Question.objects.select_related('category').order_by('-id')
        if q:
            qs = qs.filter(text__icontains=q)
        if category_id.isdigit():
            qs = qs.filter(category_id=int(category_id))
        if difficulty:
            qs = qs.filter(difficulty=difficulty)
        if active in ('1', '0'):
            qs = qs.filter(is_active=(active == '1'))

        page_obj, _ = paginate(self.request, qs, 20)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q, 'category': category_id, 'difficulty': difficulty, 'active': active}
        ctx['categories'] = Category.objects.order_by('name')
        ctx['difficulty_choices'] = Question._meta.get_field('difficulty').choices
        return ctx


class QuestionCreateView(ModalFormView):
    model = Question
    form_class = QuestionForm
    create_title = 'سوال جدید'
    form_icon = 'fa-plus-circle'
    form_subtitle = 'متن سوال، گزینه‌ها، تصاویر و پاسخ صحیح'
    section_title = 'بانک سوال'
    section_icon = 'fa-file-alt'
    multipart = True
    form_extra_class = 'ap-glass-form--wide'
    refresh_event = 'apRefreshQuestions'

    def get(self, request):
        return self._render(request, self.form_class(), self.create_title, self.submit_create)

    def post(self, request):
        form = self.form_class(**self.get_form_kwargs(request))
        if form.is_valid():
            form.save()
            return self._success('سوال ذخیره شد.')
        return self._render(request, form, self.create_title, self.submit_create)


class QuestionUpdateView(ModalFormView):
    model = Question
    form_class = QuestionForm
    form_icon = 'fa-pen'
    form_subtitle = 'ویرایش سوال و گزینه‌های آن'
    section_title = 'بانک سوال'
    section_icon = 'fa-file-alt'
    multipart = True
    form_extra_class = 'ap-glass-form--wide'
    refresh_event = 'apRefreshQuestions'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'ویرایش سوال #{obj.id}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('سوال به‌روزرسانی شد.')
        return self._render(request, form, f'ویرایش سوال #{obj.id}', self.submit_update)


class QuestionDeleteView(ModalFormView):
    model = Question
    refresh_event = 'apRefreshQuestions'

    def post(self, request, pk):
        self.get_object(pk).delete()
        return self._success('سوال حذف شد.')
