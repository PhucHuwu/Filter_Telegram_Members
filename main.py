from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, UserStatusOffline, UserStatusOnline
from telegram import Bot
from datetime import datetime, timedelta, timezone
import re
import os
import pandas as pd
from config import bot_token, chat_id, api_hash, api_id, phone_number, day_target, group_link, member_limit, messeges_limit

client = TelegramClient('session_name', api_id, api_hash)


async def main():
    await client.start(phone_number)

    target_group = await client.get_entity(group_link)
    print(f"Đang lấy thông tin nhóm: {target_group.title}, vui lòng đợi...")

    name_group = re.sub(r'[^\w\s-]', '', target_group.title, flags=re.UNICODE)
    name_group = re.sub(r'\s+', '_', name_group)
    if not os.path.exists(f"{name_group}.csv"):
        data = {
            "ID": [],
            "Tên": [],
            "Trạng thái hoạt động": [],
            "Ghi chú (muốn làm gì ở cột này thì làm)": []
        }
        df = pd.DataFrame(data)
        df.to_csv(f"{name_group}.csv", index=False)

    offset = 0
    limit = member_limit
    all_participants = []

    while True:
        participants = await client(GetParticipantsRequest(
            channel=target_group.id,
            filter=ChannelParticipantsSearch(''),
            offset=offset,
            limit=limit,
            hash=0
        ))

        if not participants.users:
            break

        all_participants.extend(participants.users)
        offset += len(participants.users)

    now = datetime.now(timezone.utc)
    recent_users = []
    messages = set()

    for user in all_participants:
        status = user.status
        if isinstance(status, UserStatusOnline):
            last_seen = now
            status_str = 'Online'
        elif isinstance(status, UserStatusOffline):
            last_seen = status.was_online
            status_str = f'Offline - {last_seen.strftime("%d-%m-%Y")}'
        else:
            continue

        if (now - last_seen) <= timedelta(days=day_target) and user.username:
            name = f"{user.first_name or ''} {user.last_name or ''}".strip()
            recent_users.append({
                'ID': user.username,
                'Tên': name,
                'Trạng thái hoạt động': status_str
            })
            messages.add(f"[{name}](t.me/{user.username})")

    messages_his = await client.get_messages(target_group, limit=messeges_limit)

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
                else:
                    break

    bot = Bot(bot_token)
    messages = list(messages)
    chunk_size = 50
    for i in range(0, len(messages), chunk_size):
        chunk = messages[i:i+chunk_size]
        await bot.send_message(
            chat_id=chat_id,
            text='\n'.join(chunk),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )

    df_new = pd.DataFrame(recent_users)
    if os.path.exists(f"{name_group}.csv"):
        df_old = pd.read_csv(f"{name_group}.csv")
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.drop_duplicates(subset=['ID'], keep='last', inplace=True)
    df_all.to_csv(f"{name_group}.csv", index=False)

    print("Đã gửi tin nhắn")
    print(f"Đã lưu {len(recent_users)} người dùng hoạt động gần đây vào {name_group}.csv")
    print("Nhấn Enter để thoát")
    if input() == "":
        exit()

with client:
    client.loop.run_until_complete(main())
