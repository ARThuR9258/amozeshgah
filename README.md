# 🎓 سیستم آموزشی آنلاین "آموزشگاه"

یک پلتفرم کامل آموزشی آنلاین با قابلیت ایجاد و برگزاری آزمون‌های آنلاین، توسعه یافته با Django 6.0

## 📋 خلاصه پروژه

این پروژه یک سیستم مدیریت آموزشی جامع است که امکانات زیر را فراهم می‌کند:
- ثبت‌نام و احراز هویت کاربران با شماره موبایل
- ایجاد و مدیریت آزمون‌های آنلاین
- سیستم سوالات چند گزینه‌ای
- مدیریت پاسخ‌های کاربران و نمره‌دهی
- رابط کاربری فارسی و راحت

## 🏗️ ساختار پروژه

```
amozeshgah/
├── amozeshga/                 # تنظیمات اصلی پروژه
│   ├── settings.py           # فایل تنظیمات Django
│   ├── urls.py              # مسیرهای اصلی پروژه
│   └── wsgi.py              # WSGI configuration
├── account_module/           # ماژول مدیریت کاربران
│   ├── models.py            # مدل کاربر سفارشی
│   ├── views.py             # ویوهای احراز هویت
│   ├── forms.py             # فرم‌های ثبت‌نام و ورود
│   └── backends.py          # backend احراز هویت با موبایل
├── quizbuilder_module/       # ماژول سازنده آزمون
│   ├── models.py            # مدل‌های آزمون، سوالات و پاسخ‌ها
│   ├── views.py             # ویوهای مدیریت آزمون
│   └── helpers.py           # توابع کمکی
├── index_module/             # ماژول صفحه اصلی
├── sample_questions/         # نمونه سوالات
├── templates/                # قالب‌های HTML
│   ├── layout/              # قالب‌های اصلی
│   └── shared/              # قالب‌های مشترک
├── static/                   # فایل‌های استاتیک
│   ├── css/                 # استایل‌ها
│   ├── js/                  # جاوا اسکریپت
│   └── dashboard/           # فایل‌های داشبورد
├── media/                    # فایل‌های رسانه‌ای
├── requirements.txt          # پکیج‌های مورد نیاز
└── manage.py                # فایل مدیریت Django
```

## 🚀 قابلیت‌های اصلی

### 🔐 مدیریت کاربران (account_module)
- **احراز هویت با شماره موبایل**: ثبت‌نام و ورود با شماره موبایل
- **مدل کاربر سفارشی**: شامل فیلدهای اختصاصی برای سیستم آموزشی
- **مدیریت تایید ایمیل**: قابلیت تایید ایمیل کاربران
- **سیستم آزمون رایگان**: محدودیت تعداد آزمون‌های رایگان روزانه
- **پرداخت برای آزمون**: قابلیت پرداخت برای دسترسی به آزمون‌های ویژه

### 📝 سازنده آزمون (quizbuilder_module)
- **ایجاد آزمون**: تعریف آزمون با عنوان، توضیحات و زمان
- **مدیریت سوالات**: ایجاد سوالات چند گزینه‌ای با بارم‌دهی
- **سیستم پاسخ‌دهی**: ثبت پاسخ‌های کاربران و محاسبه نمره
- **وضعیت آزمون**: مدیریت وضعیت‌های مختلف آزمون (باز/بسته/منقضی شده)
- **زمان‌بندی**: کنترل زمان شروع و پایان آزمون

### 🎨 رابط کاربری
- **طراحی فارسی**: رابط کاربری کامل فارسی
- **قالب‌بندی واکنش‌گرا**: طراحی مناسب برای دستگاه‌های مختلف
- **داشبورد مدیریتی**: پنل مدیریت کامل برای آزمون‌ها و کاربران

## 🛠️ تکنولوژی‌ها

- **Backend**: Django 6.0
- **Database**: SQLite (قابل تغییر به PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **API**: Django REST Framework
- **Authentication**: Custom Phone Number Backend
- **Language**: Python 3.12+

## 📦 پکیج‌های اصلی

```txt
Django==6.0
djangorestframework==3.17.1
django-widget-tweaks==1.5.1
django-render-partial==0.4
asgiref==3.11.0
sqlparse==0.5.5
tzdata==2025.3
```

## 🚀 راهنمای نصب و راه‌اندازی

### پیش‌نیازها
- Python 3.12+
- pip
- Git

### مراحل نصب

1. **کلون کردن پروژه**
```bash
git clone <repository-url>
cd amozeshgah
```

2. **ایجاد محیط مجازی**
```bash
python -m venv .venv
```

3. **فعال‌سازی محیط مجازی**
```powershell
.venv\Scripts\activate  # ویندوز
source .venv/bin/activate  # لینوکس/مک
```

4. **نصب پکیج‌های مورد نیاز**
```bash
pip install -r requirements.txt
```

5. **اجرای مهاجرت‌های پایگاه داده**
```bash
python manage.py migrate
```

6. **ایجاد کاربر ادمین**
```bash
python manage.py createsuperuser
```

7. **اجرای سرور توسعه**
```bash
python manage.py runserver
```

پس از اجرای سرور، می‌توانید به آدرس `http://127.0.0.1:8000` دسترسی داشته باشید.

## 📚 مستندات API

### مسیرهای اصلی

- `GET /` - صفحه اصلی
- `GET /admin/` - پنل مدیریت Django
- `POST /account/sign-in/` - ورود کاربر
- `POST /account/sign-up/` - ثبت‌نام کاربر
- `GET /quiz/` - لیست آزمون‌ها
- `POST /quiz/<id>/start/` - شروع آزمون
- `POST /quiz/<id>/submit/` - ارسال پاسخ‌های آزمون

### مدل‌های داده

#### User (مدل کاربر)
```python
class User(AbstractUser):
    email = models.EmailField(null=True, blank=True)
    phone_number = models.CharField(max_length=11, unique=True)
    is_verified = models.BooleanField(default=False)
    exam_attempts = models.PositiveIntegerField(default=0)
    last_attempt_date = models.DateField(null=True, blank=True)
    has_paid_for_exam = models.BooleanField(default=False)
```

#### Quiz (مدل آزمون)
```python
class Quiz(models.Model):
    title = models.CharField(max_length=255)
    desc = models.TextField(max_length=500)
    status = models.CharField(max_length=50)
    time = models.PositiveIntegerField()  # به دقیقه
    expire_time = models.DateTimeField()
```

## 🔧 تنظیمات کلیدی

### تنظیمات پایگاه داده
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### تنظیمات احراز هویت
```python
AUTH_USER_MODEL = 'account_module.User'
AUTHENTICATION_BACKENDS = [
    'account_module.backends.PhoneNumberBackend',
    'django.contrib.auth.backends.ModelBackend',
]
```

### تنظیمات بین‌المللی
```python
LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True
```

## 🎯 ویژگی‌های خاص

### احراز هویت با شماره موبایل
سیستم از شماره موبایل به عنوان فیلد اصلی برای احراز هویت استفاده می‌کند که این ویژگی برای کاربران ایرانی بسیار مناسب است.

### سیستم آزمون هوشمند
- محدودیت آزمون رایگان روزانه
- زمان‌بندی خودکار آزمون‌ها
- محاسبه خودکار نمرات
- ذخیره کامل پاسخ‌های کاربر

### رابط کاربری فارسی
تمام رابط کاربری و پیام‌های سیستم به زبان فارسی طراحی شده‌اند.

## 🚨 نکات امنیتی

- در محیط تولید، `DEBUG = False` تنظیم شود
- `SECRET_KEY` باید به صورت امن نگهداری شود
- `ALLOWED_HOSTS` باید با دامین‌های مورد نظر تنظیم شود
- از HTTPS در محیط تولید استفاده شود

## 🤝 مشارکت

برای مشارکت در پروژه:
1. یک Fork از پروژه ایجاد کنید
2. یک شاخه (branch) جدید بسازید
3. تغییرات خود را اعمال کنید
4. یک Pull Request ارسال کنید

## 📄 مجوز

این پروژه تحت مجوز [MIT License](LICENSE) منتشر شده است.

## 📞 پشتیبانی

برای سوالات و مشکلات، از طریق Issues در GitHub اقدام کنید.

---

**توسعه داده شده با ❤️ برای نظام آموزشی ایران**
