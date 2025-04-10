from telethon.sync import TelegramClient
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telegram import Bot
from datetime import datetime, timezone
import pandas as pd
import os
import re
import asyncio
import threading


from filter_members import filter_active_members
from filter_messages import filter_active_from_messages


auth_phone = None
auth_code = None
auth_ready = threading.Event()
auth_code_ready = threading.Event()
client = None


async def main(config_dict):
    global client, auth_phone, auth_code

    bot_token = config_dict.get('bot_token', '')
    chat_id = config_dict.get('chat_id', '')
    api_hash = config_dict.get('api_hash', '')
    api_id = config_dict.get('api_id', '')
    phone_number = config_dict.get('phone_number', '')
    group_link = config_dict.get('group_link', '')
    messages_limit = int(config_dict.get('messages_limit', 1000))
    member_limit = int(config_dict.get('member_limit', 1000))
    day_target = int(config_dict.get('day_target', 0))
    locmess = config_dict.get('locmess', 'y')
    locmember = config_dict.get('locmember', 'y')
    locavatar = config_dict.get('locavatar', 'n')
    locphonenum = config_dict.get('locphonenum', 'n')

    client = TelegramClient('session_name', api_id, api_hash)

    try:
        async def code_callback():
            print("Vui lòng nhập mã xác thực được gửi về Telegram")
            auth_code_ready.clear()
            auth_code_ready.wait()
            return auth_code

        session_exists = os.path.exists(os.path.join(os.getcwd(), 'session_name.session'))

        if not session_exists:
            print("Vui lòng nhập số điện thoại để đăng nhập")
            auth_ready.clear()
            auth_ready.wait()
            entered_phone = auth_phone
            print(f"Đang sử dụng số điện thoại: {entered_phone}")

            await client.start(phone=entered_phone, code_callback=code_callback)
        else:
            print("Đang sử dụng phiên có sẵn...")
            try:
                await client.connect()
                if not await client.is_user_authorized():
                    print("Phiên đã có nhưng chưa đăng nhập. Vui lòng nhập số điện thoại để đăng nhập")
                    auth_ready.clear()
                    auth_ready.wait()
                    entered_phone = auth_phone
                    print(f"Đang sử dụng số điện thoại: {entered_phone}")

                    await client.start(phone=entered_phone, code_callback=code_callback)
                else:
                    print("Đã xác thực thành công")
            except Exception as e:
                print(f"Phiên hiện tại không hoạt động. Lỗi: {e}")
                print("Vui lòng đăng nhập lại...")

                if os.path.exists(os.path.join(os.getcwd(), 'session_name.session')):
                    os.remove(os.path.join(os.getcwd(), 'session_name.session'))

                print("Vui lòng nhập số điện thoại")
                auth_ready.clear()
                auth_ready.wait()
                entered_phone = auth_phone
                print(f"Đang sử dụng số điện thoại: {entered_phone}")

                await client.start(phone=entered_phone, code_callback=code_callback)

        print("Hoàn tất đăng nhập Telegram")

        target_group = await client.get_entity(group_link)
        print(f"Đang lấy thông tin nhóm: {target_group.title}, vui lòng đợi...")

        name_group = re.sub(r'[^\w\s-]', '', target_group.title, flags=re.UNICODE)
        name_group = re.sub(r'\s+', '_', name_group)
        if not os.path.exists(f"{name_group}.csv"):
            df = pd.DataFrame(columns=["ID", "Tên", "Trạng thái hoạt động", "Ghi chú (muốn làm gì ở cột này thì làm)"])
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

        if locmember == 'y':
            require_avatar = locavatar == 'y'
            require_phonenum = locphonenum == 'y'

            r_users, r_messages = filter_active_members(
                all_participants,
                now,
                day_target,
                require_avatar=require_avatar,
                require_phonenum=require_phonenum
            )
            recent_users.extend(r_users)
            messages.update(r_messages)

        if locmess == 'y':
            r_users, r_messages = await filter_active_from_messages(client, target_group, now, day_target, messages_limit)
            recent_users.extend(r_users)
            messages.update(r_messages)

        if messages:
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
        print("Hoàn thành!")

    except Exception as e:
        print(f"Lỗi trong quá trình thực thi: {str(e)}")
        return False
    finally:
        if client and client.is_connected():
            await client.disconnect()

    return True


def run_telegram_client(config_dict):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        success = loop.run_until_complete(main(config_dict))
        return success
    except Exception as e:
        print(f"Error running Telegram client: {e}")
        return False
    finally:
        loop.close()
