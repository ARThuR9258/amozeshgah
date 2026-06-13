from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class GuidePage(models.Model):
    """صفحات آموزشی SEO — محتوای ثابت با قابلیت ویرایش از ادمین."""

    title = models.CharField(max_length=200, verbose_name='عنوان')
    slug = models.SlugField(max_length=200, unique=True, allow_unicode=True, verbose_name='شناسه URL')
    meta_description = models.CharField(max_length=320, verbose_name='توضیحات متا')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='کلمات کلیدی')
    excerpt = models.TextField(max_length=500, verbose_name='خلاصه')
    content = models.TextField(verbose_name='محتوا (HTML)')
    icon = models.CharField(max_length=60, default='fas fa-book', verbose_name='آیکون FontAwesome')
    display_order = models.PositiveSmallIntegerField(default=0, verbose_name='ترتیب')
    is_published = models.BooleanField(default=True, verbose_name='منتشر شده')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'صفحه آموزشی'
        verbose_name_plural = 'صفحات آموزشی'
        ordering = ['display_order', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('seo:guide_detail', kwargs={'slug': self.slug})
