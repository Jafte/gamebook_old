# Generated by Django 2.0 on 2017-12-11 16:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_auto_20171208_1633'),
    ]

    operations = [
        migrations.CreateModel(
            name='Gamelog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Date updated')),
                ('source', models.CharField(choices=[('u', 'user'), ('g', 'game')], default='g', max_length=1)),
                ('text', models.TextField(verbose_name='text')),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gamelogs', to='game.Session', verbose_name='session')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AlterField(
            model_name='game',
            name='status',
            field=models.CharField(choices=[('d', 'draft'), ('p', 'published')], default='d', max_length=1),
        ),
    ]