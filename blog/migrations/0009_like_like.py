# Generated by Django 4.1.1 on 2024-02-21 18:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0008_customtoken_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='like',
            name='like',
            field=models.BooleanField(default=False),
        ),
    ]
