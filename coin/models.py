from django.conf import settings
from django.db import models
from django.urls import reverse

from coin.tools import generate_invoice 


User = settings.AUTH_USER_MODEL

class Referral(models.Model):
    """Referral model for creating, updating and or deleting referred users
    through the whole system."""
    referred = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Referred user')
    referee = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Refering user',
        related_name='referee', blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True, help_text='Date joined')

    def __str__(self):
        return self.referred.username

    class Meta:
        ordering = ['-date']


class Invoice(models.Model):
    """Manages invoice creation and payout."""
    issuer = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Invoice issuer')
    invoiced_to = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Invoiced user', 
        related_name='invoiced_to')
    number = models.BigIntegerField(unique=True, default=generate_invoice,
        help_text='Unique invoice number', editable=False)
    paid_from_wallet = models.CharField(max_length=60, blank=True, null=True, 
        help_text='Bitcoin wallet address used for payment')
    description = models.CharField(max_length=200, default='', null=True, 
        blank=True, help_text='Invoice description')
    amount = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount to pay', default=00.0)
    paid = models.BooleanField(help_text='Is invoiced paid?', default=False)
    pay = models.BooleanField(default=False, 
        help_text='Confirm you have paid for the invoice')
    pay_confirm = models.BooleanField(default=False, 
        help_text='Receiving user confirm payment received')
    issue_date = models.DateTimeField(auto_now_add=True, 
        help_text='Date issued')
    pay_date = models.DateTimeField(help_text='Date paid', null=True, 
        blank=True)
    
    class Meta:
        ordering = ['issue_date', '-pay_date']

    def __str__(self):
        return 'Invoice: ' + self.invoiced_to.username +'-'+ str(self.number)

    def get_absolute_url(self):
        return reverse('coin:invoice-detail', kwargs={'pk': self.pk})


class InvoiceArchive(models.Model):
    """Backup of invoices whose circle is completed."""
    issuer = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Invoice issuer')
    invoiced_to = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Invoiced user', 
        related_name='a_invoiced_to')
    number = models.BigIntegerField(unique=True, default=generate_invoice,
        help_text='Unique invoice number', editable=False)
    paid_from_wallet = models.CharField(max_length=60, blank=True, null=True, 
        help_text='Bitcoin wallet address used for payment')
    description = models.CharField(max_length=200, default='', null=True, 
        blank=True, help_text='Invoice description')
    amount = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount to pay', default=00.0)
    paid = models.BooleanField(help_text='Is invoiced paid?', default=False)
    pay = models.BooleanField(default=False, 
        help_text='Confirm you have paid for the invoice')
    pay_confirm = models.BooleanField(default=False, 
        help_text='Receiving user confirm payment received')
    issue_date = models.DateTimeField(null=True, blank=True,
        help_text='Date issued')
    pay_date = models.DateTimeField(help_text='Date paid', null=True, 
        blank=True)
    
    class Meta:
        ordering = ['issue_date', '-pay_date']

    def __str__(self):
        return 'Archived: ' + self.invoiced_to.username +'-'+ str(self.number)

    #def get_absolute_url(self):
    #    return reverse('coin:invoice-detail', kwargs={'pk': self.pk})


class Wallet(models.Model):
    """Manages user wallet, amount earned, paid, and amount to be paid."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Wallet oowner')
    balance = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total balance', default=00.0)
    to_earn = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Amount to earn', default=00.0)
    to_pay = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Amount to pay', default=00.0)
    total_payout = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount paid out', default=00.0)
    total_earned = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount ever earned', default=00.0)

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['balance']


class History(models.Model):
    """Keeps total record of every activity going on in the system."""
    total_visits = models.IntegerField(help_text='Total site visits', 
        default=0)
    total_referral = models.IntegerField(help_text='Total users referred', 
        default=0)
    total_users = models.IntegerField(help_text='Total registered users', 
        default=0)
    total_payout = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount paid out', default=00.0)
    total_invoiced = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount invoiced', default=00.0)
    total_commission = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Total amount earned', default=00.0)

    def __str__(self):
        return "Financial History"

    class Meta:
        ordering = ['total_commission']
        verbose_name_plural = 'histories'

'''
class PendingInvoice(models.Model):
    """Keeps record of pending invoice whose payment process has been 
    initiated."""
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, 
        help_text='Invoice payable')
    success_count = models.IntegerField( default=0,
        help_text='How many success callback from bitcoin')
    initiated = models.DateTimeField(auto_now=True, 
        help_text='Payment initiation date')
    paid_date = models.DateTimeField(help_text='Payment completion date')

    def __str__(self):
        return self.invoice.number
    
    class Meta:
        ordering = ['-paid_date',]

    
class PendingPayment(models.Model):
    """Keeps record of pending payouts to users."""
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True,
        help_text='Paid invoice warranting payout to user')
    amount = models.DecimalField(max_digits=15, decimal_places=2, 
        help_text='Amount payable')
    date = models.DateTimeField(blank=True, null=True, help_text='Date paid')

    def __str__(self):
        return str(self.invoice.number) + "     " + str(self.amount)

    class Meta:
        ordering = ['-date', '-amount']
'''

class DownLine(models.Model):
    """Model for managing users in a given downline.
    Each down line is limited to three persons at most."""
    leader = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Downline Leader',
        related_name='downline_leader'
    )
    user1 = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='First user in downline',
        related_name='downline_user1', blank=True, null=True
    )
    user2 = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Second user in downline',
        related_name='downline_user2', blank=True, null=True
    )
    user3 = models.ForeignKey(
        User, on_delete=models.CASCADE, help_text='Third user in downline',
        related_name='downline_user3', blank=True, null=True
    )

    def __str__(self):
        return self.leader.username
    
    class Meta:
        ordering = ['-leader']