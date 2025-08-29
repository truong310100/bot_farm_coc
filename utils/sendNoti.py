"""
Done! Congratulations on your new bot. You will find it at t.me/Noti_coc_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, when you've finished creating your cool bot, ping our Bot Support if you want a better username for it. Just make sure the bot is fully operational before you do this.

Use this token to access the HTTP API:
8259479953:AAHmX3EpnCrRE3MkF-orAszpb9wbFUVD7TA
Keep your token secure and store it safely, it can be used by anyone to control your bot.

For a description of the Bot API, see this page: https://core.telegram.org/bots/api
"""

"""
get chat_id go to url
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
"""

import requests
TOKEN = "8259479953:AAHmX3EpnCrRE3MkF-orAszpb9wbFUVD7TA"
CHAT_ID = "5983095594"

def send_telegram_message(message, parse_mode=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    if parse_mode:
        data["parse_mode"] = parse_mode
    try:
        requests.post(url, data=data, timeout=5)
    except Exception as e:
        print(f"Send telegram error: {e}")

# message = f"Đã hoàn thành fam \n<a style=\"color: blue;\" href=\"https://qr.myu.vn/anydesk-fx504\">Kiểm tra AnyDesk</a>"
# send_telegram_message(message, parse_mode="HTML")