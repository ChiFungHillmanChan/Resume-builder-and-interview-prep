# Generated by Django 5.1.2 on 2024-10-18 19:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prep_app', '0003_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='workexperience',
            options={'ordering': ['order', '-start_date']},
        ),
        migrations.RenameField(
            model_name='workexperience',
            old_name='country',
            new_name='company',
        ),
        migrations.RemoveField(
            model_name='workexperience',
            name='description',
        ),
        migrations.RemoveField(
            model_name='workexperience',
            name='employer',
        ),
        migrations.CreateModel(
            name='WorkExperienceDescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=500)),
                ('order', models.IntegerField(default=0)),
                ('work_experience', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='description_points', to='prep_app.workexperience')),
            ],
            options={
                'ordering': ['order'],
            },
        ),
    ]
