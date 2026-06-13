from django.views.generic import DetailView, ListView

from seo_module.mixins import SEOMixin
from seo_module.utils import absolute_url, build_seo

from .models import Article


class ArticleListView(ListView):
    model = Article
    template_name = 'blog_module/article_list.html'
    context_object_name = 'articles'
    paginate_by = 9

    def get_queryset(self):
        return Article.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo'] = build_seo(self.request, override={
            'title': 'مقالات آموزشی آیین‌نامه رانندگی | آیین‌یار',
            'description': 'مقالات آموزشی، نکات آزمون و راهنمای قبولی در آزمون آیین‌نامه رانندگی.',
            'keywords': 'مقالات آیین نامه, نکات آزمون آیین نامه, آموزش رانندگی',
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'مقالات', 'url': None},
            ],
        })
        return context


class ArticleDetailView(SEOMixin, DetailView):
    model = Article
    template_name = 'blog_module/article_detail.html'
    context_object_name = 'article'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Article.objects.filter(is_published=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        og_image = ''
        if article.image:
            og_image = article.image.url

        context['seo'] = build_seo(self.request, override={
            'title': f'{article.title} | آیین‌یار',
            'description': article.meta_description,
            'keywords': article.meta_keywords,
            'og_type': 'article',
            'og_image': og_image,
            'og_image_alt': article.title,
            'breadcrumbs': [
                {'name': 'صفحه نخست', 'url': '/'},
                {'name': 'مقالات', 'url': '/blog/'},
                {'name': article.title, 'url': article.get_absolute_url()},
            ],
            'article_schema': {
                '@context': 'https://schema.org',
                '@type': 'Article',
                'headline': article.title,
                'description': article.meta_description,
                'image': absolute_url(og_image, self.request) if og_image else None,
                'url': absolute_url(article.get_absolute_url(), self.request),
                'datePublished': article.created_at.isoformat(),
                'dateModified': article.updated_at.isoformat(),
                'author': {'@type': 'Organization', 'name': 'آیین‌یار'},
                'publisher': {
                    '@type': 'Organization',
                    'name': 'آیین‌یار',
                    'logo': {'@type': 'ImageObject', 'url': absolute_url('/static/images/logo-full.png', self.request)},
                },
            },
        })
        context['related_articles'] = Article.objects.filter(
            is_published=True,
        ).exclude(pk=article.pk)[:3]
        return context
