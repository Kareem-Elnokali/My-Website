# Generated by Django 5.2.4 on 2025-07-23 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_age_customuser_help_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='age',
            field=models.PositiveSmallIntegerField(default=18, help_text='Your age (optional)', verbose_name='Age'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='help_text',
            field=models.TextField(default='-', help_text='Tell us how you can help us (optional)', verbose_name='How can you help us?'),
        ),
    ]
