def has_phonenum(user):
    return user.phone is not None


def filter_by_phonenum(users, require_phonenum=True):
    if require_phonenum:
        return [user for user in users if has_phonenum(user)]
    else:
        return users
