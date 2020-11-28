from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import (render, redirect, reverse, 
    get_object_or_404)
from django.utils import timezone
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView

from coin.models import (Wallet, Invoice, Referral, History, DownLine)
from coin.tools import (join_downline, can_upgrade, issue_invoice, rollback,
    get_invoice_payable, get_invoices_receivable, 
    update_balance_total_earning_total_payout
)
from permissions import IsOwnerMixin
from user.models import Profile, UserModel



def index(request):
    """This View Should return the home page of Leading Wealth but at this 
    stage, it redirects to user dashboard until the home page is designed."""
    return render(request, 'coin/index.html')


@login_required
def dashboard(request):
    """User dashboard view that hosts the summary of all user activities in 
    Leading Wealth website."""
    profile = get_object_or_404(Profile, user=request.user)
    wallet = Wallet.objects.get(user=request.user)
    history = History.objects.get(pk=1)
    referrals = Referral.objects.filter(referee=request.user).count()
    invoices = Invoice.objects.filter(issuer=request.user).count()
    return render(request, 'coin/dashboard.html', {'profile': profile, 
        'wallet': wallet, 'history': history, 'referrals': referrals, 
        'invoices': invoices})

    
class InvoiceList(LoginRequiredMixin, ListView):
    """View for listing all invoices and linking to individual invoice 
    detail page. It returns both the invoices issued by the logged in user and 
    the one issued to him/her by other users."""
    template_name = 'coin/invoice-list.html'
    context_object_name = 'invoices'
    ordering = ['-issue_date',]
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(
            Q(invoiced_to=self.request.user, paid=False) | Q(
                issuer=self.request.user, paid=False))
    

class InvoicedToList(LoginRequiredMixin, ListView):
    """Just like invoice list, except that it only lists invoices issued by 
    currently logged in user."""
    template_name = 'coin/invoiced-invoices.html'
    context_object_name = 'invoices'
    ordering = ['-issue_date',]
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(
            invoiced_to=self.request.user, paid=False
        )
    

class IssuedInvoiceList(LoginRequiredMixin, ListView):
    """Just like invoice list, except that it only lists invoices issued by 
    other user to the currently logged in user."""
    template_name = 'coin/issued-invoices.html'
    context_object_name = 'invoices'
    ordering = ['-issue_date',]
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(issuer=self.request.user, paid=False)


class InvoiceDetail(LoginRequiredMixin, DetailView):
    """Returns details of given invoice."""
    model = Invoice
    template_name = 'coin/invoice.html'
    context_object_name = 'invoice_detail'

    def get_queryset(self):
        return Invoice.objects.filter(
            Q(invoiced_to=self.request.user) | Q(issuer=self.request.user))


class PayInvoice(LoginRequiredMixin, UpdateView):
    """View for paying specified invoice."""
    model = Invoice
    fields = ['pay', 'paid_from_wallet']
    template_name = 'coin/pay_invoice.html'

    def get_queryset(self):
        return Invoice.objects.filter(
            invoiced_to=self.request.user, paid=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_detail'] = self.model.objects.get(
            pk=self.kwargs['pk']
        )
        return context
    
    def form_valid(self, form):
        messages.success(
            self.request, '''Thank you for paying the invoice. Please wait for 
            confirmation from your referee.'''
        )
        return super().form_valid(form)


class ConfirmInvoicePaid(LoginRequiredMixin, UpdateView):
    """View for confirming specified invoice payment has been received."""
    model = Invoice
    fields = ['pay_confirm']
    template_name = 'coin/confirm_invoice_paid.html'

    def get_queryset(self):
        return Invoice.objects.filter(
            issuer=self.request.user, paid=False)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['invoice_detail'] = self.model.objects.get(
            pk=self.kwargs['pk']
        )
        return context
    
    def form_valid(self, form):
        form.instance.paid = True
        form.instance.pay_date = timezone.now()
        update_balance_total_earning_total_payout(form.instance)
        messages.success(
            self.request, '''You have confirmed receiving payment for this 
            invoice. You may proceed to print the receipt.'''
        )
        return super().form_valid(form)


class ReceiptList(LoginRequiredMixin, ListView):
    template_name = 'coin/receipt-list.html'
    context_object_name = 'receipts'
    ordering = ['-issue_date',]
    paginate_by = 10

    def get_queryset(self):
        return Invoice.objects.filter(
            Q(invoiced_to=self.request.user, paid=True) | Q(
                issuer=self.request.user, paid=True))


class ReceiptDetail(LoginRequiredMixin, DetailView):
    """Returns details of given Receipt."""
    template_name = 'coin/receipt.html'
    context_object_name = 'receipt_detail'

    def get_queryset(self):
        return Invoice.objects.filter(
            Q(invoiced_to=self.request.user, paid=True) | Q(
                issuer=self.request.user, paid=True))


class ReferralList(LoginRequiredMixin, ListView):
    template_name = 'coin/referral-list.html'
    context_object_name = 'referrals'
    ordering = ['-date',]
    paginate_by = 10

    def get_queryset(self):
        #self.user = get_object_or_404(UserModel, username=self.request.user)
        return Referral.objects.filter(
            Q(referee=self.request.user) | Q(referred=self.request.user))
    

class LevelView(LoginRequiredMixin, IsOwnerMixin, DetailView):
    """Shows current user level and provides details of pending invoices to be
     paid before upgrading to next level."""
    model = Profile
    template_name = 'coin/level.html' 
    context_object_name = 'profile_detail'

    def get_context_data(self, **kwargs): 
        context = super().get_context_data(**kwargs)
        context['downline'] = DownLine.objects.get(leader=self.request.user)
        context['invoices'] = Invoice.objects.filter(
            issuer=self.request.user, paid=False
        )
        return context 


@login_required
def upgrade_level(request):
    """View for allowing user upgrade his or her level.
    The user is allowed to upgrade to a higher level only if (s)he meets the 
    required criteria. E.g. When he has paid his referer (Downline leader)."""

    profile = get_object_or_404(Profile, user=request.user)
    current_level = int(profile.level)
    user_can_upgrade = False
    """downline = DownLine.objects.get(
        Q(user1=request.user) | Q(user2=request.user) | Q(user3=request.user)
    )"""
    success_url = reverse('coin:dashboard')
    fail_url = reverse('coin:invoices')

    if current_level == 0:
        invoice_payable = get_invoice_payable(request.user, 20.000)
        if invoice_payable.paid:
            profile.level = '1'
            profile.save()
            issue_invoice(invoice_payable.issuer, request.user, 1)
            messages.success(
                request, '''Thank you for being a dedicated member of Leading 
                Wealth.<br>You have successfully upgraded to %s.
                ''' % profile.get_level_display()
            )
            return redirect(success_url)
        user_can_upgrade = 1
    
    elif current_level == 1:
        invoice_payable = get_invoice_payable(request.user, 50.000)
        user_can_upgrade = can_upgrade(request.user, 50.000, 20.000)
        if user_can_upgrade == 'YES':
            profile.level = '2'
            profile.save()
            issue_invoice(invoice_payable.issuer, request.user, 2)
            messages.success(
                request, '''Thank you for your continued dedication to 
                acheving financial freedom through Leading Wealth.<b>You have 
                successfully upgraded to %s.''' % profile.get_level_display()
            )
            return redirect(success_url)
    
    elif current_level == 2:
        invoice_payable = get_invoice_payable(request.user, 100.000)
        user_can_upgrade = can_upgrade(request.user, 100.000, 50.000)
        sys_user = UserModel.objects.get(pk=1) #Get system user account
        if user_can_upgrade == 'YES':
            profile.level = '3'
            profile.save()
            issue_invoice(sys_user, request.user, 6) #Issue maintenance invoice
            issue_invoice(invoice_payable.issuer, request.user, 3)
            messages.success(
                request, '''%s, You have what it takes to hit it big. You are 
                ready to receive $100 into your wallet. With this upgrade, 
                your currently a %s member.''' % (request.user, 
                    profile.get_level_display())
            )
            return redirect(success_url)
    
    elif current_level == 3:
        invoice_payable = Invoice.objects.get(
            issuer__id=1, invoiced_to=request.user, amount=20.000
        )
        if not invoice_payable.paid:
            messages.warning(
                request, '''You have not paid the system maintenance fee. 
                <br>You are required to pay this fee before you can upgrade to 
                final level where you will earn $250*3.'''
            )
            return redirect(fail_url)
        invoice_receivable = get_invoices_receivable(request.user, 100.000)
        if not invoice_receivable.count() == 3:
            messages.warning(
                request, '''There seems to be less than three persons in your 
                downline. Please verify and merge more users into your downline 
                if that is the case. Then issue remaining invoices.'''
            )
            return redirect(fail_url)
        for invoice in invoice_receivable:
            if not invoice.paid:
                messages.warning(
                    request, '''You have not received complete payment from the 
                    three people in your downline. They must all pay before you 
                    can upgrade.'''
                )
                return redirect(fail_url)
        if invoice_payable.paid:
            profile.level = '4'
            profile.save()
            messages.success(
                request, '''Determination they say, leads to success. You're 
                ready to receive $750 from your downline. We are glad you made 
                it this far. Congrats!!!'''
            )
            return redirect(success_url)
        messages.info(
            request, '''You're only  a step away from earning $750. All that 
            is required is for you to pay system maintenance fee.<br>
            We encourage you to please pay up and upgrade instantly.'''
        )
        return redirect(fail_url)

    elif current_level == 4:
        invoice_payable = get_invoice_payable(request.user, 250.000)
        user_can_upgrade = can_upgrade(request.user, 250.000, 100.000)
        if user_can_upgrade == 'YES':
            profile.level = '0'
            profile.save()
            rollback(request.user)
            messages.success(
                request, '''What a milestone! Having reached the apex level 
                and rightly completing all requirements, you have roled back 
                to the beginner level to enable you earn more on Leading 
                Wealth.'''
            )
            return redirect(success_url)
    
    if user_can_upgrade == 1:
        messages.warning(
            request, '''You have not paid your upline leader. It is required 
            that your pay your upline before you can get paid.'''
        )
        return redirect(fail_url)
    elif user_can_upgrade == 2:
        messages.warning(
            request, '''There seems to be less than three persons in your 
            downline. Please verify and merge more users into your downline if 
            that is the case. Then issue remaining invoices.'''
        )
        return redirect(fail_url)
    elif user_can_upgrade == 3:
        messages.warning(
            request, '''You have not received complete payment from the three 
            people in your downline. They must all pay before you can upgrade. 
            '''
        )
        return redirect(fail_url)
        
    return redirect(reverse('coin:level', kwargs={'pk': request.user.id}))
    