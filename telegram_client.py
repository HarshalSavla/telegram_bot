#!/usr/bin/python3

import time
import configparser
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from datetime import date, datetime
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch

from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.functions.messages import (SendMessageRequest)
from telethon.tl.types import (
PeerChannel
)


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)



# Reading Configs
config = configparser.ConfigParser()
config.read("/home/ec2-user/telegram_notfier_bot/config.ini")

# Setting configuration values
api_id = config['Telegram']['api_id']
api_hash = config['Telegram']['api_hash']

api_hash = str(api_hash)

phone = config['Telegram']['phone']
username = config['Telegram']['username']

# Create the client and connect
client = TelegramClient(username, api_id, api_hash)
#client.start()

group_to_notify = "https://t.me/+jeJeil0jyM0wZDk5" #H1 notifications.

async def main(phone):
    await client.start()
    print("Client Created")
    # Ensure you're authorized
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()



    user_input_channel = "https://t.me/H1B_H4_Visa_Dropbox_slots"

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)
    #put_channel = await client.get_entity(group_to_notify)

    offset_id = 0
    limit = 100
    all_messages = []
    total_messages = 0
    total_count_limit = 1000
    todays_date = datetime.date(datetime.now())
    messages_date = datetime.date(datetime.now())
    notify = False
    open_slot_keywords = {"open", "open slots", "bulk", "bulk open", "slots open"}
    start_time = int(time.time())

    while True:
        print("Current Offset ID is:", offset_id, "; Total Messages:", total_messages)
        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        messages = history.messages
        for message in messages:
            all_messages.append(message.to_dict())
            #messages_date = datetime.date(message["date"])
        offset_id = messages[len(messages) - 1].id
        total_messages = len(all_messages)
        if total_count_limit != 0 and total_messages >= total_count_limit:
            break
    
    for message in all_messages:
        message_text = message.get("message")
        for key in open_slot_keywords:
            if message_text and key in message_text.lower():
                notify = True
                print(f"{datetime.now(), message_text}")
                break
        messages_date = datetime.date(message.get("date"))
    if notify:
        print(f"{datetime.now()} Notifying to group")
        resp = await client(SendMessageRequest(
            await client.get_entity("t.me/h1_notifier_bot"),
            f"BOT: H1 slots may be available at {datetime.now()}"
        ))
    notify=False

with client:
    client.loop.run_until_complete(main(phone))





