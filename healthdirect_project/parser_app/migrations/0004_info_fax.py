# Generated by Django 4.2.2 on 2023-07-19 12:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('parser_app', '0003_info_email_info_website'),
    ]

    operations = [
        migrations.AddField(
            model_name='info',
            name='fax',
            field=models.CharField(blank=True, max_length=256, null=True),
        ),
    ]