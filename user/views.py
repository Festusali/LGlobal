from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F
from django.views.generic import DetailView
from django.shortcuts import (render, redirect, reverse, get_object_or_404)

from coin.models import Referral, History
from coin.tools import join_downline
from permissions import IsOwnerMixin
from user.forms import CreateUserForm, VerifyEmailForm, EditProfileForm
from user.models import UserModel, Profile, VerifyCode
from user.tools import (confirm_mail, get_email_domain, get_referee, 
    verify_user_email)


def register(request):
    """Registers new user into the user model upon verifying that user data
    are correct and valid.
    
    If the entered details are valid, a confirmation email is sent to 
    registered email address to verify it is valid and that user has acces 
    to the email."""

    #If POST request method.
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        ref_code = int(request.POST.get('refcode', 0))
        referee = get_referee(UserModel, Profile, ref_code)
        if form.is_valid(): # Is all fields valid?
            data = form.cleaned_data 
            email = confirm_mail(data.get('email'), data.get('username'))
            new_user = UserModel.objects.create_user(
                username=data.get('username'), email=data.get('email'), 
                password=data.get('password1')
                )
            new_user.email_user(
                'Leading Wealth: Please Confirm Your Email Addresss.', email[0], 
                from_email='isfestus@gmail.com', html_message=email[1]
                )
            VerifyCode.objects.create(user=new_user, code=email[2]['code'])
            referred = Referral.objects.get(referred=new_user)
            referred.referee = referee
            referred.save()
            if referee:
                History.objects.filter(pk=1).update(
                    total_referral=F('total_referral')+1, 
                    total_users=F('total_users')+1
                )
            else:
                History.objects.filter(pk=1).update(
                    total_users=F('total_users')+1
                )
            messages.success(request, """Your account has been created 
            successfully. Please go to <a href='http://%s/'>your email address 
            </a> and follow the instructions contained in the email we sent you 
            to confirm the email you used for account registration. <br> 
            <p class='info'>Please note that failure to confirm the email 
            address within 48 hours will cause your newly created account to be 
            deactivated.</p>"""%get_email_domain(new_user.email))
            return redirect(settings.LOGIN_URL)
        else:
            messages.warning(request, """Something went wrong! Please review 
            the form you submitted to correct any errors before resubmitting.
            Pay attention to all highlighted part.""")
    
    else:
        # Capture reference code
        ref_code = request.GET.get('refcode', 0)
        form = CreateUserForm() #Render empty user registration form.
    return render(request, "user/register.html", {"form": form, 
        "ref_code": ref_code})
        

def verify_email(request, username):
    """This view manually verifies user email address by confirming the 
    verification code."""
    try:
        user = UserModel.objects.get(username__iexact=username)
    except UserModel.DoesNotExist:
        messages.warning(request, """This user does not or never existed. 
            Please consider registering a new account!""")
        return redirect(reverse('user:register'))
    if request.method == 'POST':
        form = VerifyEmailForm(request.POST, instance=user)
        if form.is_valid():
            if verify_user_email(user, VerifyCode, 
                int(form.cleaned_data.get("code"))):
                join_downline(user=user)
                messages.success(request, """Thank you for verifying your email 
                address.<br>You are now a full fledged Leading Wealth member. You 
                can now login to enjoy seemless benefits awaiting you.""")
                return redirect('%s?next=/dashboard/' % (settings.LOGIN_URL))
            else:
                messages.info(request, """The code you entered appears to be 
                    invalid or has expired. Please verify and try again.""")
    else:
        form = VerifyEmailForm()
    return render(request, "user/verify_email.html", {"form": form})


def auto_verify_email(request, username, token, code):
    """Automatic verification of user registered email address.
    If verification fails, the user is automatically redirected to manual 
    verification page."""
    try:
        user = UserModel.objects.get(username__iexact=username)
    except UserModel.DoesNotExist:
        messages.warning(request, """This user does not or never existed. 
            Please consider registering a new account!""")
        return redirect(reverse('user:register'))
    if verify_user_email(user, VerifyCode, code):
        join_downline(user=user)
        messages.success(request, """Thank you for verifying your email 
        address. <br>You are now a full fledged Leading Wealth member. You can 
        now login to your account and enjoy seemless benefits awaiting you.""")
        return redirect('%s?next=/dashboard/' % (settings.LOGIN_URL))
    else:
        messages.info(request, """We cannot verify your email address because 
        probably, the link is invalid or has expired. Please enter the code 
        contained in the email sent to you to manually verify your email 
        address.""")
        return redirect(reverse("user:verify-email", args=[user.username]))


@login_required
def edit_profile(request, username):
    """A view for displaying user personal details."""
    user = get_object_or_404(UserModel, username__iexact=username).profile_data
    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, """Your account information has been 
            updated successfully!""")
            return redirect(reverse('user:profile', args=[user.id]))
        return render(request, 'user/edit_profile.html', {'form': form})
    else:
        form = EditProfileForm(instance=user) 
    return render(request, 'user/edit_profile.html', {'form': form})


class UserDetail(LoginRequiredMixin, IsOwnerMixin, DetailView):
    model = Profile
    context_object_name = 'user_detail'
    template_name = 'user/profile.html'