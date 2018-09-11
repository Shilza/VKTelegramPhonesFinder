import datetime
import random
import time
import re
from queue import Queue
from threading import Thread

import requests
from vk_api import vk_api

from Workers.DatabaseWorker import DatabaseWorker


class VKUsersWorker:

    def _auth(self):
        vk_session = vk_api.VkApi('login', 'pass')
        vk_session.auth()

        self.vk = vk_session.get_api()

    def __init__(self, settings: dict, queue: Queue):
        self._auth()

        self.receivingFinished = False
        self.usersQueue = Queue()
        self.queue = queue

        self.startId = settings.get('startId')
        self.finishId = settings.get('finishId')
        self.cityId = settings.get('cityId')
        self.ageFrom = settings.get('ageFrom')
        self.ageTo = settings.get('ageTo')
        self.sex = settings.get('sex')


    def start(self):
        thr = Thread(target=self._usersQueueProcessing)
        thr.start()

        for i in range(self.startId, self.finishId+1000, 1000):
            time.sleep(random.uniform(1, 3))

            try:
                for user in self.vk.users.get(user_ids=VKUsersWorker._makeUserIds(i), fields='contacts,city,bdate,sex'):
                    self.usersQueue.put(user)
            except (requests.exceptions.ConnectionError, ConnectionResetError, TimeoutError):
                print('Exception ' + str(datetime.datetime.now()))
                self._auth()
                i -= 1000
                time.sleep(60)
                continue
            print("Id: " + str(i) + ' ' + str(datetime.datetime.now()))
        self.receivingFinished = True
        thr.join()

    @staticmethod
    def _makeNormalPhone(phone: str):
        new = re.sub('[^+\d]', '', phone)
        length = len(new)

        if length == 10 and new[0] == '9':
            return '+7' + new
        elif length == 11 and (new[0] == '7' or new[0] == '8'):
            return '+7' + new[1:]
        elif length == 12 and new[0:3] == '+79':
            return new

        return None

    def _usersQueueProcessing(self):
        db = DatabaseWorker()
        while not self.receivingFinished or not self.usersQueue.empty():
            user = self._validateUser(self.usersQueue.get())
            if user is not None:
                self.queue.put(user)
                db.addUser(user)

    def _isAgeValid(self, age):

        if self.ageTo is not None:
            return age in range(self.ageFrom, self.ageTo + 1)
        if self.ageFrom != 0:
            return age > self.ageFrom

        return False

    def _validateUser(self, user: dict):
        obj = {}

        if self.cityId is not None:
            if 'city' in user.keys():
                if user['city']['id'] != self.cityId:
                    return None
            else:
                return None

        if self.sex is not None:
            if 'sex' not in user.keys() or user['sex'] != self.sex:
                return None

        if self.ageFrom != 0 or self.ageTo is not None:
            if 'bdate' in user.keys():
                bdateArray = user['bdate'].split('.')
                if (len(bdateArray) != 3
                        or not self._isAgeValid(datetime.datetime.now().year - int(user['bdate'].split('.')[2]))):
                    return None
            else:
                return None

        if 'home_phone' in user.keys():
            phone = VKUsersWorker._makeNormalPhone(user['home_phone'])
            if phone is not None:
                obj['home_phone'] = phone

        if 'mobile_phone' in user.keys():
            phone = VKUsersWorker._makeNormalPhone(user['mobile_phone'])
            if phone is not None:
                obj['mobile_phone'] = phone

        if len(obj.keys()) > 0:
            obj['id'] = user['id']
            return obj

        return None

    @staticmethod
    def _makeUserIds(offset: int):
        userIds = ''
        for i in range(offset, offset + 1000):
            userIds += (str(i) + ',')
        return userIds[:-1]
