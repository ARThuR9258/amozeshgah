# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quizbuilder_module', '0007_quizquestionchoice_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='userquiz',
            name='finished_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='زمان پایان'),
        ),
        migrations.AddField(
            model_name='userquiz',
            name='time_spent_seconds',
            field=models.PositiveIntegerField(default=0, verbose_name='مدت شرکت (ثانیه)'),
        ),
        migrations.AddField(
            model_name='userquiz',
            name='share_token',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=32,
                null=True,
                unique=True,
                verbose_name='توکن اشتراک نتیجه',
            ),
        ),
    ]
