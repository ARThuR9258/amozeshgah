import os
from django.db import models
from django.utils import timezone

def question_pdf_path(instance, filename):
    # File will be uploaded to MEDIA_ROOT/sample_questions/<year>/<month>/<filename>
    date_path = timezone.now().strftime('sample_questions/%Y/%m')
    return os.path.join(date_path, filename)

class SampleQuestion(models.Model):
    title = models.CharField(max_length=200, verbose_name='عنوان سوال')
    description = models.TextField(verbose_name='توضیحات', blank=True, null=True)
    pdf_file = models.FileField(upload_to=question_pdf_path, verbose_name='فایل PDF سوالات')
    is_active = models.BooleanField(default=True, verbose_name='فعال/غیرفعال')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='تاریخ به‌روزرسانی')

    class Meta:
        verbose_name = 'سوال نمونه'
        verbose_name_plural = 'سوالات نمونه'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
        
    def get_file_extension(self):
        name, extension = os.path.splitext(self.pdf_file.name)
        return extension.lower()
        
    def get_file_size(self):
        try:
            size = self.pdf_file.size
            # Convert to KB or MB
            if size < 1024 * 1024:  # Less than 1MB
                return f"{size / 1024:.1f} KB"
            return f"{size / (1024 * 1024):.1f} MB"
        except:
            return "N/A"
