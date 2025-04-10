# Filter Telegram Members

## Giới thiệu
Đây là một chương trình Python thu thập thông tin về người dùng trong một nhóm Telegram. Chương trình này sẽ theo dõi người dùng hoạt động trong khoảng thời gian được chỉ định và xuất thông tin của họ ra tệp CSV, đồng thời gửi danh sách người dùng đến một chat Telegram thông qua bot.

## Tính năng
- Thu thập thông tin người dùng từ nhóm Telegram (tên, tên người dùng, trạng thái hoạt động)
- Lọc người dùng hoạt động trong khoảng thời gian được chỉ định
- Lưu thông tin người dùng vào tệp CSV
- Gửi danh sách người dùng đến một chat Telegram qua bot

## Yêu cầu
- Python 3.6 trở lên
- Thư viện Telethon
- Thư viện python-telegram-bot
- Thư viện pandas

## Cài đặt
```bash
pip install telethon python-telegram-bot pandas
```

## Cách sử dụng
**Vui lòng liên hệ trong thông tin liên hệ**

## Kết quả
- Chương trình sẽ tạo một file CSV với tên là tên của nhóm Telegram
- File CSV chứa thông tin về tên người dùng (username), tên, trạng thái hoạt động của thành viên trong nhóm
- Danh sách người dùng hoạt động gần đây sẽ được gửi đến chat thông qua bot Telegram

## Lưu ý
- Chương trình sẽ chỉ thu thập thông tin của người dùng có tên người dùng (username)
- Đảm bảo tài khoản của bạn có quyền xem thành viên, tin nhắn trong nhóm
- Quá trình thu thập dữ liệu có thể mất thời gian tùy thuộc vào kích thước của nhóm và giới hạn cấu hình
