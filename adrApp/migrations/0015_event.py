# Generated by Django 5.1.6 on 2025-03-06 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrApp', '0014_rename_status_i_katës_anetaret_status_i_kartës'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('text', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
