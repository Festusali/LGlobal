from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import ImproperlyConfigured
    

# Ensure only owner can view object.
class IsOwnerMixin(UserPassesTestMixin):
    """Ensures that objects can only be viewed by users who created it."""
    
    permission_denied_message = '''You are restricted from viewing or 
    updating other user's account. Please avoid breaching peoples privacy.'''

    def test_func(self):
        return self.request.user == self.get_object().user

    def get_login_url(self):
        """
        Returns url for redirecting user if test fail.
        """
        #login_url = self.login_url or settings.LOGIN_URL
        if not self.login_url:
            raise ImproperlyConfigured(
                '''{0} is missing the login_url attribute. Define 
                {0}.login_url, settings.LOGIN_URL, or override 
                {0}.get_login_url().'''.format(self.__class__.__name__)
            )
        return '/dashboard/'
