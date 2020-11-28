import random

from django.db.models import F, Q


# Generate Invoice number for invoicing users.
def generate_invoice():
    """Generates random number between 2000000000 and 2999999999 to be used as 
    invoice unique number."""
    return random.randint(2000000000, 2999999999)


# Updates wallet records of invoice issuer and invoiced user
def update_to_earn_to_pay(invoice):
    """
    Updates wallet record of issuer and user invoiced.
    Parameter:
    invoice: Invoice instance from where issuer and invoiced user will be 
    determined.
    """
    from coin.models import Wallet, History

    #iss_wallet = Wallet.objects.get(user=invoice.issuer) #Issuer Wallet
    #iss_wallet.to_earn += invoice.amount
    #iss_wallet.save()
    Wallet.objects.filter(user=invoice.issuer).update(
        to_earn=F('to_earn')+invoice.amount
    )

    #inv_wallet = Wallet.objects.get(
    #    user=invoice.invoiced_to
    #) #Invoiced user wallet
    #inv_wallet.to_pay += invoice.amount
    #inv_wallet.save()
    Wallet.objects.filter(user=invoice.invoiced_to).update(
        to_pay=F('to_pay')+invoice.amount
    )

    History.objects.filter(id=1).update(total_invoiced=invoice.amount)
    return True


# Updates wallet records of invoice issuer and invoiced user
def update_balance_total_earning_total_payout(invoice):
    """
    Updates Invoice receiver's balance and total earnings.
    Updates Invoiced user's balance and total payouts.
    """
    from coin.models import Wallet, History

    #iss_wallet = Wallet.objects.get(user=invoice.issuer) #Issuer Wallet
    #iss_wallet.balance += invoice.amount
    #iss_wallet.total_earned += invoice.amount
    #iss_wallet.save()
    Wallet.objects.filter(user=invoice.issuer).update(
        balance=F('balance')+invoice.amount, 
        total_earned=F('total_earned')+invoice.amount
    ) 
    
    #inv_wallet = Wallet.objects.get(
    #    user=invoice.invoiced_to
    #) #Invoiced user wallet
    #inv_wallet.balance -= invoice.amount
    #inv_wallet.total_payout += invoice.amount
    #inv_wallet.save()
    Wallet.objects.filter(user=invoice.invoiced_to).update(
        balance=F('balance')-invoice.amount, 
        total_payout=F('total_payout')+invoice.amount
    ) 

    History.objects.filter(id=1).update(total_payout=invoice.amount)
    return True


# Issues invoice to user
def issue_invoice(issuer, invoiced_to, level, amount=0.0, description=''):
    """Generates invoice payable using the provided details.
    The amount payable is automatically determined by the provided level.
    Parameters:
    issuer: User instance that is issuing invoice.
    invoiced_to: User instance who will pay the invoice.
    level: Determines the level to upgrade to and the amount to pay.
    amount: Amount to be paid."""
    from coin.models import Invoice

    description = '''Thank you for helping make this investment reality. 
            It is required that you pay $%s for me to upgrade to next level. 
            This will also enable you upgrade to next level too.'''
    
    if level > 5:
        invoice = Invoice.objects.create(
            issuer=issuer, invoiced_to=invoiced_to, amount=20.00,
            description='''You are required to remit $20.00 only to system 
            account used for site maintenance purposes. Without which you will 
            not receive last payment of $250 each from your downline.'''
        )
        if invoice:
            update_to_earn_to_pay(invoice)
        return invoice
    if level == 3:
        invoice = Invoice.objects.create(
            issuer=issuer, invoiced_to=invoiced_to, amount=250.00, 
            description=description % str(250.00)
        )
        if invoice:
            update_to_earn_to_pay(invoice)
        return invoice
    elif level == 2:
        invoice = Invoice.objects.create(
            issuer=issuer, invoiced_to=invoiced_to, amount=100.00, 
            description=description % str(100.00)
        )
        if invoice:
            update_to_earn_to_pay(invoice)
        return invoice
    elif level == 1:
        invoice = Invoice.objects.create(
            issuer=issuer, invoiced_to=invoiced_to, amount=50.00, 
            description=description % str(50.00)
        )
        if invoice:
            update_to_earn_to_pay(invoice)
        return invoice
    else:
        invoice = Invoice.objects.create(
            issuer=issuer, invoiced_to=invoiced_to, amount=20.00, 
            description=description % str(20.00)
        )
        if invoice:
            update_to_earn_to_pay(invoice)
        return invoice


# Invoice User Downline
def invoice_downline(issuer, level, amount):
    """
    Issues invoice to users in the given user (issuer) downline. The amount 
    depends on the current level of the invoice issuer.
    Parameters:
    issuer: The user instance whose downline will be invoiced.
    level: The issuer level to determine the amount that will be invoiced.
    """
    from coin.models import DownLine, Invoice
    
    downline = DownLine.objects.get(leader=issuer)
    if not downline.user3:
        return 'User3 missing'
    elif not downline.user2:
        return 'User2 missing'
    elif not downline.user1:
        return 'User1 missing'
    
    invoices = Invoice.objects.filter(issuer=issuer, amount=amount)
    if not invoices.get(invoiced_to=downline.user1):
        issue_invoice(issuer, downline.user1, level)
    if not invoices.get(invoiced_to=downline.user2):
        issue_invoice(issuer, downline.user2, level)
    if not invoices.get(invoiced_to=downline.user3):
        issue_invoice(issuer, downline.user3, level)
    
    return True


# Add user to his/her referee downline or a random downline
def join_downline(user):
    """
    Adds user to the referee's downline if the downline is not up to three 
    users already. If it contains more, add the user to a random downline.
    The user will be issued referral invoice.
    Parameter:
    user: The user instance that will be added to a downline.
    """
    from coin.models import DownLine, Referral
    from user.models import UserModel
     
    referred = Referral.objects.get(referred=user)
    if referred.referee:
        referee = Referral.objects.get(referee=referred.referee, 
            referred=referred.referred)
        leader = UserModel.objects.get(referee=referee)
    else:
        leader = UserModel.objects.get(pk=1)
    downline = DownLine.objects.get(leader=leader)
    print("Downline: ", downline)
    if downline.user3: # Is the third slot already added?
        print("Downline3: ", downline.user3)
        downline = DownLine.objects.exclude(user3__isnull=False).exclude(
            leader=user 
        )
        downline = downline.order_by('?').first()
        print('Random downline: ', downline)
    if not downline.user1: # If there is no user in first downline.
        downline.user1 = user
    elif not downline.user2: # If there is no user in second downline.
        downline.user2 = user
    elif not downline.user3: # If there is no user in third downline.
        downline.user3 = user
    
    if downline:
        print("Final downline: ", downline)
        downline.save()
        print("After saving downline: ", downline, "Downline leader: ", downline.leader)
        issue_invoice(downline.leader, user, 0)
        return True
    return False


def can_upgrade(user, amount_payable, amount_receivable):
    """
    Determines if the user making the request is allowed to upgrade to 
    next level.
    Parameters:
    user: The user whose level will be upgraded or rolled over.
    amount_payable: The amount attached to the invoices to be checked.
    amount_receivable: The amount that is to be received by user.
    """
    if not get_invoice_payable(user, amount_payable).paid:
        return 1
    else:
        invoices_receivable = get_invoices_receivable(
            user, amount_receivable
        )
        if not invoices_receivable.count() == 3:
            return 2
        for invoice in invoices_receivable:
            if not invoice.paid:
                return 3
        return 'YES'
    return 4


def rollback(user):
    """
    Reverts user level to 0 to enable him/her sponsor other users who have not 
    reached the top.
    The function is responsible for migrating all invoices to InvoiceArchive, 
    deleting users in old Downline and updating account details.
    """
    from coin.models import Invoice
    backup_invoices(
        Invoice.objects.filter(Q(issuer=user) | Q(invoiced_to=user)).exclude(
            paid=False
        )
    )
    delete_downline(get_downline(user))
    join_downline(user)
    user.profile_data.level = '0'
    user.profile_data.circles += 1
    user.save()
    return True


def backup_invoices(invoices):
    """Copies given invoices to Invoice Archive."""
    from coin.models import InvoiceArchive
    for inv in invoices:
        InvoiceArchive.objects.create(
            issuer=inv.issuer, invoiced_to=inv.invoiced_to, number=inv.number, 
            paid_from_wallet=inv.paid_from_wallet, description=inv.description, 
            amount=inv.amount, paid=inv.paid, pay=inv.pay, 
            pay_confirm=inv.pay_confirm, issue_date=inv.issue_date, 
            pay_date=inv.pay_date
        )
        inv.delete()
    return True


def delete_downline(downline):
    """Removes all users in the given downline."""
    downline.user1 = ''
    downline.user2 = ''
    downline.user3 = ''
    downline.save()
    return downline


def get_downline(user):
    """Returns downline where user is the leader."""
    from coin.models import DownLine
    return Downline.objects.get(leader=user)


def get_invoice_payable(user, amount):
    """Returns invoice payable by user.
    Parameter:
    amount: The amount to be paid.
    """
    from coin.models import Invoice
    return Invoice.objects.get(invoiced_to=user, amount=amount)

def get_invoices_receivable(user, amount):
    """Returns all invoices that the user is due to be paid based on the 
    amount given. All paid invoices are excluded.
    Parameter:
    amount: The amount to be paid.
    """
    from coin.models import Invoice
    return Invoice.objects.filter(
        issuer=user, amount=amount, paid=False
    )