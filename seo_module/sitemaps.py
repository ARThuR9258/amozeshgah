from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog_module.models import Article
from quizbuilder_module.models import Category
from sample_questions.models import SampleQuestion

from .models import GuidePage


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return [
            'first_page',
            'about_page',
            'contact_page',
            # 'sample_questions:question_list',  # موقتاً غیرفعال
            'subscriptions:pricing',
            'blog:article_list',
            'quizbuilder:exam_hub',
        ]

    def location(self, item):
        return reverse(item)

    def priority(self, item):
        if item == 'first_page':
            return 1.0
        if item in ('quizbuilder:exam_hub',):
            return 0.9
        return 0.7


class GuidePageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.85

    def items(self):
        return GuidePage.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class ArticleSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Article.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.75

    def items(self):
        return Category.objects.filter(is_active=True)

    def location(self, obj):
        return obj.get_absolute_url()


class SampleQuestionSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return SampleQuestion.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()
