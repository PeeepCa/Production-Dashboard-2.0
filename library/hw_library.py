# HW library
# so far only the RFID reader

import serial
import ctypes
from library.logger_library import logger

class hw:
    def __init__(self, *args):
        # input of COM and BAUD // COM8, 9600
        self.msg_show = 1
        self.COM = args[0]
        self.BAUD = args[1]

    def rfid_open(self):
        try:
            globals()['ser'] = serial.Serial(self.COM, self.BAUD, timeout=0.5)
            useReader = True
        except serial.serialutil.SerialException:
            if self.msg_show == 1:
                dec = ctypes.windll.user32.MessageBoxW(0, 'Error 0x203 Reader at: ' + self.COM + ' cannot be found.\rContinue withour reader?', 'HW Error', 0x1001)
                logger.log_event(logger(), 'RFID reader at ' + self.COM + ' doesnt work. POPUP for continue or exit')
                if dec == 1:
                    useReader = False
                else:
                    exit(0)
            else:
                useReader = True
        return useReader

    def rfid_read(self):
        # readout of CARD id
        try:
            ser.write(b'0500100\r')
            serialString = ser.readline()
            if len(serialString) == 21:
                serialString = str(int(serialString.decode('utf-8')[-9:], 16))
            else:
                serialString = '0'
            return serialString

        except serial.serialutil.SerialException:
            logger.log_event(logger(), 'RFID reader trying to reconnect.')
            HW.rfid_close()
            self.msg_show = 0
            HW.rfid_open(self.COM, self.BAUD)
            self.msg_show = 1

    def rfid_close(self):
        ser.close()