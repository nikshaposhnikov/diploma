# Generated by Django 3.0 on 2020-03-16 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20200316_1147'),
    ]

    operations = [
        migrations.AlterField(
            model_name='additionalschedule',
            name='start_time',
            field=models.TimeField(choices=[('08:30:00', '08:30:00'), ('10:25:00', '10:25:00'), ('12:35:00', '12:35:00'), ('14:30:00', '14:30:00'), ('16:25:00', '16:25:00'), ('18:10:00', '18:10:00')], max_length=10, null=True, verbose_name='Начало занятия'),
        ),
    ]
