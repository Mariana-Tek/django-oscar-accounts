from django.db.models import get_model
from django.utils.translation import ugettext_lazy as _
from oscar.apps.payment.exceptions import UnableToTakePayment

from accounts import facade, exceptions, core, codes
from accounts.models import Account, Transfer

from jsonapi_response.errors import JSONAPIException
from revenue_core.models import DeferredRevenueEdge


def user_accounts(user):
    """
    Return accounts available to the passed user
    """
    return Account.active.filter(primary_user=user)


def redeem(order_number, user, allocations):
    """
    Is a variation of accounts.checkout.gateway.redeem, which uses pk instead of code in allocations.
    Also validates that the type is 6 :: deferred

    Settle payment for the passed set of account allocations

    Will raise UnableToTakePayment if any of the transfers is invalid
    """
    # First, we need to check if the allocations are still valid.  The accounts
    # may have changed status since the allocations were written to the
    # session.
    transfers = []
    destination = core.redemptions_account()

    for id, amount in allocations.items():
        try:
            account = Account.active.get(pk=id)
        except Account.DoesNotExist:
            raise JSONAPIException(status='422', code='ACCOUNT_REDEMPTION_DNE',
                                   title='Account Does Not Exist',
                                   detail="Account "+str(id)+" does not exist")

        if account.account_type.id != 6:
            raise JSONAPIException(status='422', code='ACCOUNT_REDEMPTION_MISTYPE',
                                   title='Account Type Is Invalid',
                                   detail="Account "+str(id)+" is not a valid type for redemption")

        # We verify each transaction
        try:
            Transfer.objects.verify_transfer(
                account, destination, amount, user)
        except exceptions.AccountException as e:
            raise JSONAPIException(status='422', code='ACCOUNT_REDEMPTION_FAIL',
                                   title='Account Redemption Failed',
                                   detail="Account redemption failed: "+str(e))

        transfers.append((account, destination, amount))

    # All transfers verified, now redeem
    for account, destination, amount in transfers:
        facade.transfer(account, destination, amount,
                        user=user, merchant_reference=order_number,
                        description="Redeemed to pay for order %s" % order_number)


def create_giftcard(order_number, user, amount):
    source = core.paid_source_account()
    code = codes.generate()
    destination = Account.objects.create(
        code=code
    )
    facade.transfer(source, destination, amount, user,
                    "Create new account")