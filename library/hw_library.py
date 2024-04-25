# HW library
# so far only the RFID reader

import sys
from serial import Serial, serialutil
from ctypes import windll
from library.logger_library import Logger

msg_show = 1
ser = Serial()


class Hw:
    def __init__(self, *args):
        # input of COM and BAUD // COM8, 9600
        self.COM = args[0]
        self.BAUD = args[1]

    def rfid_open(self):
        try:
            globals()['ser'] = Serial(self.COM, self.BAUD, timeout=0.5)
            use_reader = True
        except serialutil.SerialException:
            if msg_show == 1:
                dec = windll.user32.MessageBoxW(0, 'Error 0x203 Reader at: ' + self.COM +
                                                ' cannot be found.\rContinue without reader?', 'HW Error', 0x1001)
                Logger.log_event(Logger(), 'RFID reader at ' + self.COM + ' doesnt work. POPUP for continue or exit')
                if dec == 1:
                    use_reader = False
                else:
                    sys.exit()
            else:
                use_reader = True
        return use_reader

    def rfid_read(self):
        # readout of CARD id
        try:
            ser.write(b'0500100\r')
            serial_string = ser.readline()
            if len(serial_string) == 21:
                serial_string = str(int(serial_string.decode('utf-8')[-9:], 16))
            else:
                serial_string = '0'
            print(serial_string)
            return serial_string

        except serialutil.SerialException:
            Logger.log_event(Logger(), 'RFID reader trying to reconnect.')
            Hw.rfid_close()
            global msg_show
            msg_show = 0
            Hw.rfid_open(Hw(self.COM, self.BAUD))
            msg_show = 1
            return '0'

    @staticmethod
    def rfid_close():
        ser.close()
