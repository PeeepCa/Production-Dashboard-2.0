# Logger library

from datetime import datetime

class logger:
    def __init__(self):
        self.config = open(logger.timeStmp().split(' ')[0].replace('.','') + '_log.txt', 'a')

    def timeStmp():
        actualTime = datetime.now()
        actualTime = actualTime.strftime('%d.%m.%Y %H:%M:%S')
        return str(actualTime)

    def log_event(self, *args):
        content = args[0]
        self.config.write(logger.timeStmp() + ': ' + content + '\n')
        self.config.close()