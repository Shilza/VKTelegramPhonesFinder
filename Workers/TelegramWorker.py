import datetime
import random
import time
from queue import Queue

import telethon
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactRequest
from telethon.tl.types import InputPhoneContact

from Workers.DatabaseWorker import DatabaseWorker


class TelegramWorker:
    def __init__(self, queue: Queue):
        self.client = TelegramClient('test', 'app_id', 'app_hash')
        self.client.start()
        self.db = DatabaseWorker()
        self.queue = queue

    def _add(self, phone):
        try:
            contact = self.client(ImportContactsRequest([InputPhoneContact(client_id=0, phone=phone,
                                                  first_name="TEST", last_name="test")])).imported
        except telethon.errors.rpcerrorlist.FloodWaitError as error:
            print('Telegram exception error')
            time.sleep(error.seconds + random.uniform(1, 3))
            return self._add(phone)
        return contact

    def _remove(self, id):
        self.client(DeleteContactRequest(id))

    def _check(self, phone):
        contact = self._add(phone)
        if len(contact) > 0:
            self._remove(contact[0].user_id)
            return True
        return False

    def checkNumbers(self, users):
        print('Telegram process starts ' + str(datetime.datetime.now()))
        for user in users:
            if user[1] is not None and self._check(user[1]):
                self.db.addPhone(str(user[0]), user[1])
            if user[2] is not None and self._check(user[2]):
                self.db.addPhone(str(user[0]), user[2])

            time.sleep(random.uniform(1, 3))

    def checkInQueue(self):
        while True:
            user = self.queue.get()
            print('Check user in Telegram: ' + str(user['id']))
            if 'mobile_phone' in user.keys() and self._check(user['mobile_phone']):
                self.db.addPhone(str(user['id']), user['mobile_phone'])
            if 'home_phone' in user.keys() and self._check(user['home_phone']):
                self.db.addPhone(str(user['id']), user['home_phone'])

