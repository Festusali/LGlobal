# Generated by Django 2.2 on 2019-09-30 23:34

import coin.tools
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('coin', '0002_auto_20190926_0127'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='downline',
            options={'ordering': ['-leader']},
        ),
        migrations.AlterField(
            model_name='invoice',
            name='paid',
            field=models.BooleanField(default=False, help_text='Is invoiced paid?'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='pay',
            field=models.BooleanField(default=False, help_text='Confirm you have paid for the invoice'),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='pay_confirm',
            field=models.BooleanField(default=False, help_text='Receiving user confirm payment received'),
        ),
        migrations.CreateModel(
            name='InvoiceArchive',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.BigIntegerField(default=coin.tools.generate_invoice, editable=False, help_text='Unique invoice number', unique=True)),
                ('paid_from_wallet', models.CharField(blank=True, help_text='Bitcoin wallet address used for payment', max_length=60, null=True)),
                ('description', models.CharField(blank=True, default='', help_text='Invoice description', max_length=200, null=True)),
                ('amount', models.DecimalField(decimal_places=3, default=0.0, help_text='Total amount to pay', max_digits=15)),
                ('paid', models.BooleanField(default=False, help_text='Is invoiced paid?')),
                ('pay', models.BooleanField(default=False, help_text='Confirm you have paid for the invoice')),
                ('pay_confirm', models.BooleanField(default=False, help_text='Receiving user confirm payment received')),
                ('issue_date', models.DateTimeField(blank=True, help_text='Date issued', null=True)),
                ('pay_date', models.DateTimeField(blank=True, help_text='Date paid', null=True)),
                ('invoiced_to', models.ForeignKey(help_text='Invoiced user', on_delete=django.db.models.deletion.CASCADE, related_name='a_invoiced_to', to=settings.AUTH_USER_MODEL)),
                ('issuer', models.ForeignKey(help_text='Invoice issuer', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['issue_date', '-pay_date'],
            },
        ),
    ]