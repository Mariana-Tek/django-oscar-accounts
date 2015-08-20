from accounts import names
from accounts.models import Account

def redemptions_account():
    return Account.objects.get(name=names.REDEMPTIONS)


def lapsed_account():
    return Account.objects.get(name=names.LAPSED)


def giftcard_source_account_for_orders():
    return Account.objects.get(name=names.BANK)

def giftcard_source_account_for_nonorders():
    return Account.objects.get(name=names.UNPAID_ACCOUNTS[0])
