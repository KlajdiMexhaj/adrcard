# Generated by Django 5.1.6 on 2025-03-07 08:48

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adrApp', '0018_anetaret_guid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='anetaret',
            name='guid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
