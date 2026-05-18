from django.db import models


class ContactMessage(models.Model):
    SUBJECT_CHOICES = [
        ('support', 'پشتیبانی فنی'),
        ('subscription', 'اشتراک و پرداخت'),
        ('content', 'محتوا و سوالات'),
        ('partnership', 'همکاری'),
        ('other', 'سایر موارد'),
    ]

    name = models.CharField(max_length=120, verbose_name='نام و نام خانوادگی')
    email = models.EmailField(verbose_name='ایمیل')
    phone = models.CharField(max_length=15, blank=True, verbose_name='شماره موبایل')
    subject = models.CharField(max_length=30, choices=SUBJECT_CHOICES, default='support', verbose_name='موضوع')
    message = models.TextField(verbose_name='پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')

    class Meta:
        verbose_name = 'پیام تماس'
        verbose_name_plural = 'پیام‌های تماس'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.get_subject_display()}'
