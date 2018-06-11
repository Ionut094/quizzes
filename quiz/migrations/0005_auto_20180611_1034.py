# Generated by Django 2.0.5 on 2018-06-11 10:34

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0004_auto_20180531_0735'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeaturedQuestion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='FeaturedQuestionsPage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('created', models.DateField(default=datetime.date(2018, 6, 11))),
                ('active_until', models.DateField(blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='featuredquestion',
            name='featured_page',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='quiz.FeaturedQuestionsPage'),
        ),
        migrations.AddField(
            model_name='featuredquestion',
            name='question',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='quiz.Question'),
        ),
    ]