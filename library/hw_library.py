# HW library
# RFID and 232 library

import sys
from serial import Serial, serialutil
from ctypes import windll
from library.logger_library import Logger
from traceback import format_exc
msg_show = 1
ser = Serial()


class Hw:
    """
    Hardware handling for RFID reader and RS232.
    :param com: COM
    :param baud: BAUD
    """
    def __init__(self, com, baud):
        # input of COM and BAUD
        self.COM = com
        self.BAUD = baud

    def rfid_open(self):
        """
        Opening the RS232
        :return: use_reader
        """
        try:
            globals()['ser'] = Serial(self.COM, self.BAUD, timeout=0.5)
            use_reader = True
        except serialutil.SerialException:
            if msg_show == 1:
                dec = windll.user32.MessageBoxW(0, 'Error 0x203 Reader at: ' + self.COM +
                                                ' cannot be found.\rContinue without reader?', 'HW Error', 0x1001)
                Logger.log_event(Logger(), 'RFID reader at ' + self.COM +
                                 ' doesnt work. POPUP for continue or exit. ' + format_exc())
                if dec == 1:
                    use_reader = False
                else:
                    sys.exit()
            else:
                use_reader = True
        return use_reader

    def rfid_read(self):
        """
        RS232 read
        :return: serial_string
        """
        # readout of CARD id
        try:
            ser.write(b'0500100\r')
            serial_string = ser.readline()
            if len(serial_string) == 21:
                serial_string = str(int(serial_string.decode('utf-8')[-9:], 16))
            else:
                serial_string = '0'
            return serial_string

        except serialutil.SerialException:
            Logger.log_event(Logger(), 'RFID reader trying to reconnect. ' + format_exc())
            Hw.rfid_close()
            global msg_show
            msg_show = 0
            Hw.rfid_open(Hw(self.COM, self.BAUD))
            msg_show = 1

    @staticmethod
    def rfid_close():
        """
        Close the RFID
        """
        ser.close()

    def rs232_open(self):
        """
        Open the RS232
        """
        try:
            globals()['ser'] = Serial(self.COM, self.BAUD, timeout=0.5)
        except serialutil.SerialException:
            if msg_show == 1:
                windll.user32.MessageBoxW(0, 'Error 0x203 RS232 at: ' + self.COM + ' cannot be found.',
                                          'HW Error', 0x1000)
                Logger.log_event(Logger(), 'RS232 reader at ' + self.COM +
                                 ' doesnt work' + format_exc())

    def rs232_write(self, command):
        """
        RS232 write
        :param command: command
        :return: serial_string
        """
        try:
            ser.write(command.encode('utf-8'))

        except serialutil.SerialException:
            Logger.log_event(Logger(), 'RS232 reader trying to reconnect. ' + format_exc())
            Hw.rs232_close()
            global msg_show
            msg_show = 0
            Hw.rs232_open(Hw(self.COM, self.BAUD))
            msg_show = 1

    def rs232_read(self):
        """
        RS232 read
        :return: serial_string
        """
        try:
            serial_string = ser.readline()
            return serial_string
        except serialutil.SerialException:
            Logger.log_event(Logger(), 'RS232 reader trying to reconnect. ' + format_exc())
            Hw.rs232_close()
            global msg_show
            msg_show = 0
            Hw.rs232_open(Hw(self.COM, self.BAUD))
            msg_show = 1

    @staticmethod
    def rs232_close():
        """
        Close the RS232
        """
        ser.close()
