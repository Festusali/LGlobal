# Generated by Django 2.2 on 2019-10-02 00:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('coin', '0003_auto_20191001_0034'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='history',
            options={'ordering': ['total_commission'], 'verbose_name_plural': 'histories'},
        ),
        migrations.RemoveField(
            model_name='history',
            name='total_balance',
        ),
        migrations.RemoveField(
            model_name='history',
            name='total_earnings',
        ),
        migrations.RemoveField(
            model_name='history',
            name='total_payouts',
        ),
        migrations.RemoveField(
            model_name='history',
            name='user',
        ),
        migrations.AddField(
            model_name='history',
            name='total_commission',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount earned', max_digits=15),
        ),
        migrations.AddField(
            model_name='history',
            name='total_payout',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount paid out', max_digits=15),
        ),
        migrations.AlterField(
            model_name='history',
            name='total_invoiced',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount invoiced', max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoice',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount to pay', max_digits=15),
        ),
        migrations.AlterField(
            model_name='invoicearchive',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total amount to pay', max_digits=15),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='balance',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Total balance', max_digits=15),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='to_earn',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Amount to earn', max_digits=15),
        ),
        migrations.AlterField(
            model_name='wallet',
            name='to_pay',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Amount to pay', max_digits=15),
        ),
    ]