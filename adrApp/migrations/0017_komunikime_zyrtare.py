# Generated by Django 5.1.6 on 2025-03-07 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrApp', '0016_kandidatperdeputet_alter_event_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='Komunikime_Zyrtare',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titull', models.CharField(blank=True, max_length=200, null=True)),
                ('text', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
