from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField(max_length=250, verbose_name='عنوان')
    slug = models.SlugField(max_length=250, unique=True, allow_unicode=True, verbose_name='شناسه URL')
    content = models.TextField(verbose_name='محتوا (HTML)')
    excerpt = models.TextField(max_length=500, blank=True, verbose_name='خلاصه')
    image = models.ImageField(
        upload_to='blog/',
        blank=True,
        null=True,
        verbose_name='تصویر شاخص',
    )
    meta_description = models.CharField(max_length=320, verbose_name='توضیحات متا')
    meta_keywords = models.CharField(max_length=300, blank=True, verbose_name='کلمات کلیدی')
    is_published = models.BooleanField(default=False, verbose_name='منتشر شده')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'مقاله'
        verbose_name_plural = 'مقالات'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        if not self.excerpt and self.content:
            from django.utils.html import strip_tags
            plain = strip_tags(self.content)
            self.excerpt = plain[:300].strip()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:article_detail', kwargs={'slug': self.slug})
