# Load csv file

from django.core.management.base import BaseCommand, CommandError
from main.models import Expense
import csv
import os
import sys
import django
from django.contrib.auth.models import User
from django.db import IntegrityError
from datetime import datetime
from django.utils import timezone

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'splitwise.settings')
django.setup()


# CSV Columns: Date,Description,Category,Cost,Currency,user1,user2
class Command(BaseCommand):
    help = """Command to migrate expenses from splitwise. 
    Please remove header and footer rows from csv, only data. 
    Usage: python manage.py migrate_from_splitwise --filename=expenses.csv --user_1=foo --user_2=bar"""

    def add_arguments(self, parser):
        parser.add_argument('--filename', type=str)
        parser.add_argument('--user_1', type=str)
        parser.add_argument('--user_2', type=str)

    def handle(self, *args, **options):

        with open(options['filename']) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                date = datetime.strptime(row[0], '%Y-%m-%d')
                title = row[1]
                int_value = float(row[3])
                is_payment = True if row[2] == 'Payment' else False
                value = None if is_payment else int_value
                is_settle = True if is_payment else False
                net_value = int_value if is_payment else int_value * 0.5
                if (float(row[5]) < 0):
                    user = User.objects.get(username=options['user_1'])
                else:
                    user = User.objects.get(username=options['user_2'])
                Expense.objects.create(
                    date=date, title=title, value=value, user=user, net_value=net_value, is_settle=is_settle)

        self.stdout.write(self.style.SUCCESS(
            'Migration completed successfully'))
