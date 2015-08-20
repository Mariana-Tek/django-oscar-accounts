from accounts import names


def redemptions_account():
    return Account.objects.get(name=names.REDEMPTIONS)


def lapsed_account():
    return Account.objects.get(name=names.LAPSED)
