from django.db.models import Q
from django.views.generic import TemplateView

from admin_panel.auth import AdminRequiredMixin
from quizbuilder_module.forms import CategoryForm
from quizbuilder_module.models import Category

from .crud_base import ListPageView, ModalFormView, paginate


class CategoryListView(ListPageView):
    template_name = 'admin_panel/categories/list.html'
    table_url_name = 'admin_panel:categories_table'
    create_url_name = 'admin_panel:categories_create'
    page_title = 'دسته‌بندی سوالات'
    page_subtitle = 'افزودن، ویرایش و حذف دسته‌ها'
    page_icon = 'fa-folder'
    page_accent = 'ap-accent-amber'
    table_id = 'apCategoriesTable'
    refresh_event = 'apRefreshCategories'


class CategoryTableView(AdminRequiredMixin, TemplateView):
    template_name = 'admin_panel/categories/_table.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = (self.request.GET.get('q') or '').strip()
        qs = Category.objects.all().order_by('display_order', 'name')
        if q:
            qs = qs.filter(Q(name__icontains=q) | Q(slug__icontains=q))
        page_obj, _ = paginate(self.request, qs, 20)
        ctx['items'] = page_obj.object_list
        ctx['page_obj'] = page_obj
        ctx['filters'] = {'q': q}
        return ctx


class CategoryCreateView(ModalFormView):
    model = Category
    form_class = CategoryForm
    create_title = 'دسته‌بندی جدید'
    form_icon = 'fa-folder-plus'
    form_subtitle = 'نام، شناسه و ترتیب نمایش دسته را مشخص کنید'
    section_icon = 'fa-folder'
    refresh_event = 'apRefreshCategories'

    def get(self, request):
        return self._render(request, self.form_class(), self.create_title, self.submit_create)

    def post(self, request):
        form = self.form_class(**self.get_form_kwargs(request))
        if form.is_valid():
            form.save()
            return self._success('دسته‌بندی ذخیره شد.')
        return self._render(request, form, self.create_title, self.submit_create)


class CategoryUpdateView(ModalFormView):
    model = Category
    form_class = CategoryForm
    form_icon = 'fa-folder-open'
    form_subtitle = 'ویرایش مشخصات دسته‌بندی'
    section_icon = 'fa-folder'
    refresh_event = 'apRefreshCategories'

    def get(self, request, pk):
        obj = self.get_object(pk)
        return self._render(request, self.form_class(instance=obj), f'ویرایش {obj.name}', self.submit_update)

    def post(self, request, pk):
        obj = self.get_object(pk)
        form = self.form_class(**self.get_form_kwargs(request, obj))
        if form.is_valid():
            form.save()
            return self._success('دسته‌بندی به‌روزرسانی شد.')
        return self._render(request, form, f'ویرایش {obj.name}', self.submit_update)


class CategoryDeleteView(ModalFormView):
    model = Category
    refresh_event = 'apRefreshCategories'

    def post(self, request, pk):
        self.get_object(pk).delete()
        return self._success('دسته‌بندی حذف شد.')
