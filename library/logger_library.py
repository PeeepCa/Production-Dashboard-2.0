# Logger library

from datetime import datetime


class Logger:
    def __init__(self):
        self.config = open(Logger.time_stamp().split(' ')[0].replace('.', '') + '_log.txt', 'a')

    @staticmethod
    def time_stamp():
        actual_time = datetime.now()
        actual_time = actual_time.strftime('%d.%m.%Y %H:%M:%S')
        return str(actual_time)

    def log_event(self, *args):
        content = args[0]
        self.config.write(Logger.time_stamp() + ': ' + content + '\n')
        self.config.close()
