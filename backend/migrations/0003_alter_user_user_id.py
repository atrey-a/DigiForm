# Generated by Django 5.0.3 on 2024-06-05 21:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0002_alter_user_consent_for_digiform_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_id',
            field=models.UUIDField(auto_created=True, primary_key=True, serialize=False),
        ),
    ]