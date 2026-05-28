"""
انتقال سوالات از db.sqlite3 قدیمی (QuizQuestion + QuizQuestionChoice) به مدل Question جدید.
اجرا: python manage.py import_legacy_questions
"""
import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from quizbuilder_module.models import Category, Question


class Command(BaseCommand):
    help = 'Import questions from legacy SQLite database'

    def handle(self, *args, **options):
        sqlite_path = Path(__file__).resolve().parents[3] / 'db.sqlite3'
        if not sqlite_path.exists():
            self.stderr.write(f'Not found: {sqlite_path}')
            return

        category, _ = Category.objects.get_or_create(
            slug='general',
            defaults={'name': 'عمومی', 'is_active': True},
        )

        conn = sqlite3.connect(sqlite_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        try:
            cur.execute(
                'SELECT id, description, image, quiz_id FROM quizbuilder_module_quizquestion'
            )
        except sqlite3.OperationalError:
            self.stderr.write('Legacy quiz tables not found in sqlite.')
            conn.close()
            return

        rows = cur.fetchall()
        created = 0
        for row in rows:
            qid = row['id']
            cur.execute(
                '''
                SELECT c.id, c.text, c.image, c.is_answer
                FROM quizbuilder_module_quizquestion_choices m
                JOIN quizbuilder_module_quizquestionchoice c ON c.id = m.quizquestionchoice_id
                WHERE m.quizquestion_id = ?
                ORDER BY c.id
                LIMIT 4
                ''',
                (qid,),
            )
            choices = cur.fetchall()
            if len(choices) < 4:
                pad = list(choices)
                while len(pad) < 4:
                    pad.append({'text': f'گزینه {len(pad) + 1}', 'image': None, 'is_answer': False})
                choices = pad

            correct = 1
            for i, ch in enumerate(choices[:4], start=1):
                if ch['is_answer']:
                    correct = i
                    break

            Question.objects.create(
                text=row['description'] or f'سوال {qid}',
                option_1=choices[0]['text'] or '—',
                option_2=choices[1]['text'] or '—',
                option_3=choices[2]['text'] or '—',
                option_4=choices[3]['text'] or '—',
                correct_answer=correct,
                category=category,
                is_active=True,
            )
            created += 1

        conn.close()
        self.stdout.write(self.style.SUCCESS(f'Imported {created} questions into category "{category.name}"'))
