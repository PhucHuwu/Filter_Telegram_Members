from telethon.tl.types import UserStatusOffline, UserStatusOnline
from datetime import timedelta
from filter_avatar import filter_by_avatar
from filter_phonenum import filter_by_phonenum


def filter_active_members(users, now, day_target, require_avatar=True, require_phonenum=True):
    recent_users = []
    messages = set()

    users = filter_by_avatar(users, require_avatar=require_avatar)
    users = filter_by_phonenum(users, require_phonenum=require_phonenum)

    for user in users:
        status = user.status
        if isinstance(status, UserStatusOnline):
            last_seen = now
            status_str = 'Online'
        elif isinstance(status, UserStatusOffline):
            last_seen = status.was_online
            status_str = f'Offline - {last_seen.strftime("%d-%m-%Y")}'
        else:
            continue

        if require_phonenum and user.phone:
            status_str = f'{user.phone} {status_str}'

        if (now - last_seen) <= timedelta(days=day_target) and user.username:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            recent_users.append({
                'ID': user.username,
                'Tên': name,
                'Trạng thái hoạt động': status_str
            })
            messages.add(f"[{name}](t.me/{user.username})")

    return recent_users, messages
