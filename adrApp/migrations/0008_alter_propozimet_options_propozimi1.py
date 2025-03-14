# Generated by Django 5.1.6 on 2025-03-04 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrApp', '0007_propozimet_cv'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='propozimet',
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Propozimi1',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('choice', models.CharField(choices=[('Po', 'Po'), ('Jo', 'Jo')], max_length=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('propozim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adrApp.propozimet')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adrApp.anetaret')),
            ],
            options={
                'unique_together': {('propozim', 'user')},
            },
        ),
    ]
