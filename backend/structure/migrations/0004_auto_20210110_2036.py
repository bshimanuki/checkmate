# Generated by Django 3.1.3 on 2021-01-11 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0003_auto_20210105_0120'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='botconfig',
            name='alert_new_puzzle_id',
        ),
        migrations.RemoveField(
            model_name='botconfig',
            name='alert_solved_puzzle_id',
        ),
        migrations.AddField(
            model_name='botconfig',
            name='alert_new_puzzle_webhook',
            field=models.CharField(blank=True, default='', help_text='Discord webhook for new puzzle alerts.', max_length=500),
        ),
        migrations.AddField(
            model_name='botconfig',
            name='alert_solved_puzzle_webhook',
            field=models.CharField(blank=True, default='', help_text='Discord webhook for solved puzzle alerts.', max_length=500),
        ),
    ]
