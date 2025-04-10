from datetime import timedelta
from telethon.tl.types import User


async def filter_active_from_messages(client, target_group, now, day_target, messeges_limit):
    messages_his = await client.get_messages(target_group, limit=messeges_limit)
    recent_users = []
    messages = set()

    for message in messages_his:
        if message.sender_id:
            entity = await client.get_entity(message.sender_id)
            if isinstance(entity, User) and entity.username:
                name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                sent_time = message.date
                if now - sent_time <= timedelta(days=day_target):
                    sent_time_str = sent_time.strftime("%d-%m-%Y")
                    recent_users.append({
                        'ID': entity.username,
                        'Tên': name,
                        'Trạng thái hoạt động': sent_time_str
                    })
                    messages.add(f"[{name}](t.me/{entity.username})")

    return recent_users, messages
