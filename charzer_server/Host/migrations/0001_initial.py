# Generated by Django 3.1.2 on 2021-06-11 10:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('customer', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostNotification',
            fields=[
                ('N_id', models.AutoField(primary_key=True, serialize=False)),
                ('N_Title', models.CharField(default='', max_length=500)),
                ('N_date_time', models.DateTimeField(auto_now_add=True, null=True)),
                ('N_Description', models.CharField(default='', max_length=500)),
                ('N_status', models.BooleanField(default=True)),
                ('N_Host', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='customer.host')),
            ],
        ),
    ]
