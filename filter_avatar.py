def has_avatar(user):
    return user.photo is not None


def filter_by_avatar(users, require_avatar=True):
    if require_avatar:
        return [user for user in users if has_avatar(user)]
    else:
        return users
