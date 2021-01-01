# Generated by Django 3.1.3 on 2021-01-01 19:50

import autoslug.fields
from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.hstore
from django.db import migrations, models
import django.db.models.constraints
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BotConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('puzzles_page', models.CharField(blank=True, default='', help_text='Page with puzzles list (or data endpoint) to be queried by scraper.', max_length=500)),
                ('login_page', models.CharField(blank=True, default='', help_text='Login page (used by scraper).', max_length=500)),
                ('login_api_endpoint', models.CharField(blank=True, default='', help_text='Login endpoint (used by scraper).', max_length=500)),
                ('enable_scraping', models.BooleanField(default=False, help_text='Enable scraping for new puzzles.')),
                ('default_category_id', models.BigIntegerField(blank=True, help_text='Category for puzzles to be placed if not in round category.', null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HuntConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auto_assign_puzzles_to_meta', models.BooleanField(default=True, help_text='Should be true when the entire round corresponds to one meta.')),
                ('root', models.CharField(blank=True, default='', help_text='Hunt prefix (protocol, domain, and path prefix). (eg https://example.com)', max_length=500)),
                ('discord_server_id', models.BigIntegerField(blank=True, default=781000769758691358, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MetaFeeder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, help_text='Order of puzzles (0-indexed). Will default to last.')),
            ],
            options={
                'ordering': ['order'],
                'get_latest_by': 'created',
                'abstract': False,
                'required_db_features': {'supports_deferrable_unique_constraints'},
            },
        ),
        migrations.CreateModel(
            name='Puzzle',
            fields=[
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=500, populate_from='name', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('link', models.CharField(blank=True, default='', help_text='Can be path relative to hunt root', max_length=500)),
                ('original_link', models.CharField(blank=True, default='', editable=False, help_text='Link upon creation. (Used to ensure scraper does not duplicate)', max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('hidden', models.BooleanField(default=False, help_text='Hidden objects will not be shown.')),
                ('notes', models.TextField(blank=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict, help_text='Keys with optional values.')),
                ('discord_text_channel_id', models.BigIntegerField(blank=True, null=True)),
                ('discord_voice_channel_id', models.BigIntegerField(blank=True, null=True)),
                ('sheet_link', models.CharField(blank=True, default='', max_length=500)),
                ('answer', models.CharField(blank=True, default='', max_length=500)),
                ('solved', models.DateTimeField(blank=True, db_index=True, null=True)),
                ('status', models.CharField(blank=True, default='', max_length=500)),
                ('is_meta', models.BooleanField(default=False, help_text='Can only be edited directly when there are no feeder puzzles. Adding feeder puzzles will also set this field.')),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='puzzle_created_set', to=settings.AUTH_USER_MODEL)),
                ('feeders', models.ManyToManyField(related_name='metas', through='structure.MetaFeeder', to='structure.Puzzle')),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='puzzle_modified_set', to=settings.AUTH_USER_MODEL)),
                ('solved_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='puzzle_solved_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('slug', autoslug.fields.AutoSlugField(editable=False, max_length=500, populate_from='name', primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=500)),
                ('link', models.CharField(blank=True, default='', help_text='Can be path relative to hunt root', max_length=500)),
                ('original_link', models.CharField(blank=True, default='', editable=False, help_text='Link upon creation. (Used to ensure scraper does not duplicate)', max_length=500)),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('modified', models.DateTimeField(auto_now=True, db_index=True)),
                ('hidden', models.BooleanField(default=False, help_text='Hidden objects will not be shown.')),
                ('notes', models.TextField(blank=True)),
                ('tags', django.contrib.postgres.fields.hstore.HStoreField(default=dict, help_text='Keys with optional values.')),
                ('discord_text_channel_id', models.BigIntegerField(blank=True, null=True)),
                ('discord_voice_channel_id', models.BigIntegerField(blank=True, null=True)),
                ('sheet_link', models.CharField(blank=True, default='', max_length=500)),
                ('auto_assign_puzzles_to_meta', models.BooleanField(default=True, help_text='Should be true when the entire round corresponds to one meta.')),
                ('discord_category_id', models.BigIntegerField(blank=True, null=True)),
                ('round_tags', django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=500), default=list, help_text='Tag categories that should be displayed / set for each puzzle in the round.', size=None)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='round_created_set', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='round_modified_set', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('created',),
                'get_latest_by': 'created',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RoundPuzzle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('order', models.PositiveSmallIntegerField(blank=True, help_text='Order of puzzles (0-indexed). Will default to last.')),
                ('puzzle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='round_relations', to='structure.puzzle')),
                ('round', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='puzzle_relations', to='structure.round')),
            ],
            options={
                'ordering': ['order'],
                'get_latest_by': 'created',
                'abstract': False,
                'required_db_features': {'supports_deferrable_unique_constraints'},
            },
        ),
        migrations.AddField(
            model_name='round',
            name='puzzles',
            field=models.ManyToManyField(related_name='rounds', through='structure.RoundPuzzle', to='structure.Puzzle'),
        ),
        migrations.AddField(
            model_name='metafeeder',
            name='feeder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='meta_relations', to='structure.puzzle'),
        ),
        migrations.AddField(
            model_name='metafeeder',
            name='meta',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feeder_relations', to='structure.puzzle'),
        ),
        migrations.AddConstraint(
            model_name='roundpuzzle',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('round', 'puzzle'), name='unique_puzzle'),
        ),
        migrations.AddConstraint(
            model_name='roundpuzzle',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('round', 'order'), name='unique_puzzle_order'),
        ),
        migrations.AddConstraint(
            model_name='metafeeder',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, meta=django.db.models.expressions.F('feeder')), name='meta_ne_feeder'),
        ),
        migrations.AddConstraint(
            model_name='metafeeder',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('meta', 'feeder'), name='unique_feeder'),
        ),
        migrations.AddConstraint(
            model_name='metafeeder',
            constraint=models.UniqueConstraint(deferrable=django.db.models.constraints.Deferrable['DEFERRED'], fields=('meta', 'order'), name='unique_feeder_order'),
        ),
    ]
