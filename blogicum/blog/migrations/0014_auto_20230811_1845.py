# Generated by Django 3.2.16 on 2023-08-11 18:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0013_auto_20230811_1842'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='image',
        ),
        migrations.AddField(
            model_name='post',
            name='images',
            field=models.ImageField(blank=True, upload_to='posts_images', verbose_name='Фото'),
        ),
    ]