# Generated by Django 5.1.6 on 2025-03-04 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrApp', '0005_remove_anetaret_status_anetaret_shkolla_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anetaret',
            name='status_i_katës',
            field=models.CharField(choices=[('Aktiv', 'Aktiv'), ('I heshtur', 'I heshtur')], default='Aktiv', max_length=10),
        ),
    ]
