from datetime import timedelta


async def filter_active_from_messages(client, target_group, now, day_target, messeges_limit):
    messages_his = await client.get_messages(target_group, limit=messeges_limit)
    recent_users = []
    messages = set()

    for message in messages_his:
        if message.sender_id:
            user = await client.get_entity(message.sender_id)
            if user.username:
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                sent_time = message.date
                if now - sent_time <= timedelta(days=day_target):
                    sent_time_str = sent_time.strftime("%d-%m-%Y")
                    recent_users.append({
                        'ID': user.username,
                        'Tên': name,
                        'Trạng thái hoạt động': sent_time_str
                    })
                    messages.add(f"[{name}](t.me/{user.username})")
                    
    return recent_users, messages
