import random, secrets
from datetime import timedelta

from django.conf import settings
from django.utils import timezone


# Upload paths
def pic_path(instance, filename):
    """Generates the path where user profile picture will be saved."""
    return "images/users/%s.%s" % (instance.user, filename.split('.')[-1])


# User Referral Code
def reference_code():
    """Generates random number between 100,000 to 999,999 used as user referral
    code."""
    return random.randint(100000, 999999)


# Random URL safe tokens for email confirmation
def make_token():
    """Generates and returns random token code and URL safe token URL."""
    code = random.randint(100000, 600000)
    token = secrets.token_urlsafe(40)
    return {"code": code, "token": token}


# Crafts confirmation email to be used in verifying user email address.
def confirm_mail(email, username):
    """Constructs confirmation email message to be sent to New User upon 
    registration to confirm User Email address is valid.
    
    All parameters are required.
    
    Upon success, returns token code."""
    token = make_token()
    
    txt = """Thank you for registering an account with Leading Wealth. \n
    This email address ({email}) was used to register a new account at 
    https://www.leadingwealthworldwide.com/ Leading Wealth.\n
    Please click this link to confirm your email to validate your registration
    https://www.leadingwealthworldwide.com/users/verify/{username}/{token}/{code}/ \n
    Alternatively, if the link above is not clickable, you can visit; 
    https://www.leadingwealthworldwide.com/users/verify/{username}/ 
    and enter {code} as your verification code.\n

    Note: This link expires automatically in 48hrs and becomes invalid after 
    the specified period.\n
    If you received this mail in error, please disregard it and we will never 
    contact you again.\n
    This is an automatically generated email and hence should not be replied.\n
    If you need further information, please visit; 
    https://www.leadingwealthworldwide.com/contact%20us/ or better still send a 
    mail to admin@leadingwealthworldwide.com.\n\n
    Kind regards,\n
    Leading Wealth.\n
    """.format(username=username, email=email, token=token["token"], 
            code=token["code"])


    html = """This email address ({email}) was used to register a new account 
    at <a href="https://www.leadingwealthworldwide.com/">Leading Wealth</a>.<br>
    <p>Please click below link to confirm your registration; <br> 
    <a href="https://www.leadingwealthworldwide.com/users/verify/{username}/{token}/{code}/">
    Confirm Email</a> </p>
    <p>Alternatively, if the link above is not clickable, you can visit; <br> 
    https://www.leadingwealthworldwide.com/users/verify/{username}/ 
    and enter <b>{code}</b> as your verification code. </p>
    <p><b>Note:</b> This link expires automatically in 48hrs and becomes 
    invalid after the specified period.</p>
    <p>If you received this mail in error, please disregard it and we will 
    never contact you again.</p>
    <p>This is an automatically generated email and hence should not be 
    replied.<br> If you need further information, please visit; <br> 
    https://www.leadingwealthworldwide.com/contact%20us/ or better still 
    send a mail to admin@leadingwealthworldwide.com.</p>
    <p>Kind regards,<br>
    Leading Wealth.</p>
    """.format(username=username, email=email, token=token["token"], 
            code=token["code"])
        
    return (txt, html, token)


# Get email domain/server address
def get_email_domain(email):
    """Generates email domain from given email address."""
    return "www."+email.split("@")[-1]


def verify_user_email(user, verify_code, code):
    """Verifies the user email address by checking the code against the user 
    verification code in the database.
    Parameters:
    user: The user instance whose email needs to be verified.
    verify_code: The model where user verification codes are stored.
    code: User verification code as sent to user's registered email."""
    try:
        verify_user = verify_code.objects.get(user=user, code=code)
        if timezone.now() - verify_user.date > timedelta(hours=48, minutes=1):
            # user.delete() # Deletes user for not verifying email within time.
            return False
        else:
            user.email_verified = True
            user.save()
            verify_user.delete()
            return True
    except verify_code.DoesNotExist:
        return False


def get_referee(user_model, profile, ref_code):
    """Returns the referee instance with given ref_code or None."""
    try:
        return user_model.objects.get(
            profile_data=profile.objects.get(ref_code=ref_code))
    except profile.DoesNotExist:
        return None
