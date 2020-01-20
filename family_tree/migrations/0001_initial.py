# Generated by Django 3.0 on 2020-01-18 07:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Connection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('relation', models.CharField(blank=True, choices=[('Grand Parent', 'grand_parent'), ('Parent', 'parent'), ('Children', 'children'), ('Sibling', 'sibling'), ('Cousin', 'cousin')], max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='People',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True)),
                ('last_name', models.CharField(blank=True, max_length=25, null=True)),
                ('phone_numner', models.CharField(blank=True, max_length=15, null=True)),
                ('email', models.EmailField(blank=True, max_length=255, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('dob', models.DateField(blank=True, null=True)),
                ('relations', models.ManyToManyField(related_name='_people_relations_+', through='family_tree.Connection', to='family_tree.People')),
            ],
        ),
        migrations.AddField(
            model_name='connection',
            name='people',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actor', to='family_tree.People'),
        ),
        migrations.AddField(
            model_name='connection',
            name='related_person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='related_person', to='family_tree.People'),
        ),
    ]
