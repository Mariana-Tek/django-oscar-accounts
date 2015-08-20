from django.apps import AppConfig
from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = _("Accounts")

    def ready(self):
        Account = get_model('accounts', 'Account')
        Transfer = get_model('accounts', 'Transfer')



# from accounts import exceptions, core


