"""
URL configuration for amozeshga project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from quizbuilder_module.wrong_question_views import (
    WrongQuestionsExamStartView,
    WrongQuestionsListView,
)
from seo_module.sitemaps import (
    ArticleSitemap,
    CategorySitemap,
    GuidePageSitemap,
    # SampleQuestionSitemap,
    StaticViewSitemap,
)
from seo_module.views import robots_txt

sitemaps = {
    'static': StaticViewSitemap,
    'guides': GuidePageSitemap,
    'articles': ArticleSitemap,
    'categories': CategorySitemap,
    # 'samples': SampleQuestionSitemap,  # نمونه سوالات — موقتاً غیرفعال
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django_sitemap'),
    path('', include('index_module.urls')),
    path('account/', include('account_module.urls')),
    # نمونه سوالات عمومی — موقتاً غیرفعال؛ فقط مسیرهای داشبورد فعال
    path('questions/', include('sample_questions.urls')),
    path('quiz/', include('quizbuilder_module.urls')),
    path('my-wrong-questions/', WrongQuestionsListView.as_view(), name='wrong_questions_list'),
    path('my-wrong-questions/start/', WrongQuestionsExamStartView.as_view(), name='wrong_questions_exam_start'),
    path('pricing/', include('subscriptions_module.urls')),
    path('blog/', include('blog_module.urls')),
    path('', include('seo_module.urls')),
]

# media: در development یا با SERVE_MEDIA=True از Django سرو می‌شود
# در production معمولاً nginx مسیر /media/ را از MEDIA_ROOT می‌خواند
if settings.SERVE_MEDIA:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
