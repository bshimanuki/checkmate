# Generated by Django 3.1.14 on 2024-01-09 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('structure', '0010_googlesheetowner'),
    ]

    operations = [
        migrations.AddField(
            model_name='huntconfig',
            name='block_metas_on_feeders',
            field=models.BooleanField(default=False, help_text='Whether to block access to meta pages until feeders are solved by default.'),
        ),
    ]