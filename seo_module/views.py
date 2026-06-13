from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.generic import DetailView, ListView

from blog_module.models import Article
from quizbuilder_module.models import Category
from seo_module.mixins import SEOMixin
from seo_module.utils import absolute_url, build_seo

from .models import GuidePage


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /dashboard/',
        'Disallow: /account/panel/',
        'Disallow: /account/forgot-password/',
        'Disallow: /account/reset-password/',
        'Disallow: /quiz/session/',
        'Disallow: /quiz/start/',
        'Disallow: /my-wrong-questions/',
        'Disallow: /pricing/checkout/',
        'Disallow: /pricing/payment/',
        '',
        f'Sitemap: {absolute_url("/sitemap.xml", request)}',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain; charset=utf-8')


class GuideListView(ListView):
    model = GuidePage
    template_name = 'seo_module/guide_list.html'
    context_object_name = 'guides'

    def get_queryset(self):
        return GuidePage.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo'] = build_seo(self.request, override={
            'title': 'راهنمای آزمون آیین‌نامه | آیین‌یار',
            'description': 'راهنمای جامع آزمون آیین‌نامه: سوالات فنی، تابلوها، حق تقدم، پارک دوبل و نکات قبولی.',
            'keywords': 'راهنمای آیین نامه, نکات آزمون آیین نامه, تابلوهای راهنمایی رانندگی',
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'راهنما', 'url': None},
            ],
        })
        return context


class GuideDetailView(SEOMixin, DetailView):
    model = GuidePage
    template_name = 'seo_module/guide_detail.html'
    context_object_name = 'guide'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return GuidePage.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        guide = self.object
        context['seo'] = build_seo(self.request, override={
            'title': f'{guide.title} | آیین‌یار',
            'description': guide.meta_description,
            'keywords': guide.meta_keywords,
            'og_type': 'article',
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'راهنما', 'url': '/guide/'},
                {'name': guide.title, 'url': guide.get_absolute_url()},
            ],
            'article_schema': {
                '@context': 'https://schema.org',
                '@type': 'Article',
                'headline': guide.title,
                'description': guide.meta_description,
                'url': absolute_url(guide.get_absolute_url(), self.request),
                'datePublished': guide.created_at.isoformat(),
                'dateModified': guide.updated_at.isoformat(),
                'author': {'@type': 'Organization', 'name': 'آیین‌یار'},
                'publisher': {
                    '@type': 'Organization',
                    'name': 'آیین‌یار',
                    'logo': {'@type': 'ImageObject', 'url': absolute_url('/static/images/logo-full.png', self.request)},
                },
            },
        })
        context['related_guides'] = GuidePage.objects.filter(
            is_published=True,
        ).exclude(pk=guide.pk)[:4]
        context['recent_articles'] = Article.objects.filter(is_published=True)[:3]
        return context
