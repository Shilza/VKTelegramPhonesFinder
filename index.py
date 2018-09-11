from queue import Queue
from threading import Thread
from Workers.TelegramWorker import TelegramWorker
from Workers.VKUsersWorker import VKUsersWorker


def telegramWorkerProcessing():
    TelegramWorker(queue).checkInQueue()


queue = Queue()

settings = dict(
    startId=1,
    finishId=10000000,
    sex=1,
    ageFrom=17,
    ageTo=23,
    cityId=1
)

Thread(target=telegramWorkerProcessing).start()
VKUsersWorker(settings, queue=queue).start()






