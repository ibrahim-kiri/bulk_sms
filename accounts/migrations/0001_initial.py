# Generated by Django 5.1.4 on 2024-12-15 08:46

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('user_id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=50, unique=True, verbose_name='Username')),
                ('full_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Full Name')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, unique=True, verbose_name='Email Address')),
                ('phone', models.CharField(blank=True, max_length=20, null=True, verbose_name='Phone Number')),
                ('address', models.TextField(blank=True, null=True, verbose_name='Address')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created At')),
                ('is_active', models.BooleanField(default=True)),
                ('is_staff', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
                'db_table': 'users',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('profile_id', models.AutoField(primary_key=True, serialize=False, verbose_name='Profile ID')),
                ('profile_picture', models.CharField(blank=True, max_length=500, null=True, verbose_name='Profile Picture Path')),
                ('users_user_id', models.OneToOneField(db_column='users_user_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Profile',
                'verbose_name_plural': 'Profiles',
                'db_table': 'profiles',
            },
        ),
    ]
