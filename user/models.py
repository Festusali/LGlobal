from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.urls import reverse

from coin.models import (Wallet, History, Referral, DownLine)
from user.tools import (pic_path, reference_code)


GENDERS = (
    ("M", "Male"),
    ("F", "Female"),
    ("T", "Transgender"),
    ("O", "Other"),
)

STATUSES = (
    ("M", "Married"),
    ("S", "Single"),
    ("E", "Engaged"),
    ("D", "Divorced"),
    ("O", "Others"),
)

LEVELS = (
    ("0", "Level 0"),
    ("1", "Level 1"),
    ("2", "Level 2"),
    ("3", "Level 3"),
    ("4", "Level 4"),
    ("5", "Level 5"),
)


class UserModelManager(UserManager):
    """Extends UserManager to ensure that CaSe InsenSItiVE username can be 
    registered."""
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(
            self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    
class UserModel(AbstractUser):
    """Extends AbstractUser and adds one extra required field to help with user
    registration and verification."""

    email_verified = models.BooleanField(help_text="Is user email verified?",
        default=False)

    objects = UserModelManager()


class Profile(models.Model):
    """
    Adds more fields to the user object by allowing to include extra
    required fields.

    This model is just a basic extention of the Default User model.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, related_name="profile_data",
        help_text="More user data")
    board_member = models.BooleanField(help_text="Is the user Board Member?",
        default=False)
    level = models.CharField(max_length=2, choices=LEVELS,
        help_text="What is the user level?", default="0")
    circles = models.PositiveIntegerField(default=1,
        help_text='Number of circles completed')
    gender = models.CharField(max_length=2, choices=GENDERS,
        help_text="Gender", blank=True)
    status = models.CharField(max_length=2, choices=STATUSES,
        help_text="Marital Status", blank=True)
    phone = models.BigIntegerField(help_text="Mobile number", blank=True,
        null=True)
    wallet = models.CharField(max_length=60, blank=True, null=True, 
        help_text='Bitcoin wallet address')
    ref_code = models.IntegerField(unique=True, help_text='Reference code',
        default=reference_code, editable=False)
    avatar = models.ImageField(upload_to=pic_path, help_text="Profile Picture",
        blank=True)
    modified = models.DateTimeField(auto_now=True, help_text="Last modifield")


    def __str__(self):
        return self.user.username

    
    def get_absolute_url(self):
        return reverse('user:profile', kwargs={'pk': self.user.pk})

    
    def full_name(self):
        return self.user.get_full_name() or self.user.username

    
    def get_avatar(self):
        """Returns avatar url of the profile instance."""
        try:
            return self.avatar.url
        except:
            return "/static/images/users/defaultavatar.png"
    

class VerifyCode(models.Model):
    """Manages the verification of user email address."""
    user = models.OneToOneField(settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, help_text="Temporal user")
    code = models.IntegerField(unique=True, help_text='Verification code')
    date = models.DateTimeField(auto_now_add=True, help_text='Date created')

    def __str__(self):
        return self.user.username

    class Meta:
        ordering = ['-date', 'user']


@receiver(post_save, sender=UserModel)
def create_basic_models(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
        Wallet.objects.create(user=instance)
        Referral.objects.create(referred=instance)
        DownLine.objects.create(leader=instance)

    
@receiver(post_save, sender=UserModel)
def save_profile(sender, instance, **kwargs):
    instance.profile_data.save()
