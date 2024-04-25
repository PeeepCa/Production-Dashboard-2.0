# Dodělat iTAC
# Dodělat Logování - Hotovo
# Dodělat čtečku - Hotovo
# Dodělat offline režim
# Dodělat mustry
# Odzkošeno i jako exe
# Multithreading - částečně hotovo

import tkinter
import sys
from psutil import process_iter
from threading import Thread
from ctypes import windll
from os import path
from socket import gethostname
from time import sleep
from PIL import ImageTk, Image
from library.seso_library import seso
from library.logger_library import logger
from library.config_library import config
from library.hw_library import hw

class app:
    def __init__(self):
        # stationNumber, PATH, thread_number, restAPI, bool(remove_file), sesoData, bool(useSESO), bool(parselog), bool(useReader), COM, BAUD, int(greenFPY), int(orangeFPY), bool(showIntr), bool(useLogin), company_logo, sesoOperator, bool(useTraining), log_format, serverInstrGen
        # init for all the default data + readout of the config file
        logger.log_event(logger(), 'Logging started.')
        if getattr(sys, 'frozen', False):
            application_path = path.dirname(sys.executable)
        elif __file__:
            application_path = path.dirname(__file__)
        temp = config.read_config(config(application_path + '/Configuration/' + gethostname() + '.ini'))
        self.stationNo = temp[0]
        self.companyLogo = temp[15]
        self.greenFpy = temp[11]
        self.orangeFpy = temp[12]
        self.sesoData = temp[5]
        self.sesoOperator = temp[16]
        self.useSeso = temp[6]
        self.useReader = temp[8]
        self.COM = temp[9]
        self.BAUD = temp[10]
        self.canvasBack = temp[20]
        self.rectBack = temp[21]
        self.graphBack = temp[22]
        self.textColor = temp[23]
        self.graphColor = temp[24]
        self.threadCount = temp[2]
        self.run = True
        self.dsh_offset = 0
        self.op_id = 0
        self.fpy_perf = 0
        self.lrf_perf = 0
        self.pass_count = 0
        self.fail_count = 0
        self.msg_show = 1
        self.op_name = ''
        self.unlock = False
        self.training = ''
        if self.useReader == True:
            self.useReader = hw.rfid_open(hw(self.COM, self.BAUD))

    def checkAppStatus():
        n = 0
        for p in process_iter(attrs=['pid', 'name']):
            if p.info['name'] == 'production.exe':
                n = n + 1
                if n > 2:
                    windll.user32.MessageBoxW(0, 'Error 0x204 App is already running' , 'Error', 0x1000)
                    exit(0)

    def UI(self):
        top = tkinter.Tk()
        window_width = 400 - self.dsh_offset
        window_height = 250
        screen_width = int(top.winfo_screenwidth() - window_width)
        screen_height = int(top.winfo_screenheight() - window_height - 40)
        top.title('Dashboard')
        top.geometry(f'{window_width}x{window_height}+{screen_width}+{screen_height}')
        top.config(bg = '#484179')
        top.attributes('-alpha', 0.8)
        top.overrideredirect(True)
        top.anchor('center')
        top.attributes('-topmost', 1)
        c = tkinter.Canvas(width = 400, height = 250, bg = self.canvasBack, bd = -2)
        c.create_rectangle(0, 0, 80, 250, tags = 'ch', fill = self.rectBack, width = 0)
        c.pack()

        def main_exit(*args):
            # just the exit which stops the main loop
            logger.log_event(logger(), 'App exit by button.')
            if self.useSeso == True:
                self.useReader = hw.rfid_close(hw(self.COM, self.BAUD))
            self.run = False

        def minimize(*args):
            # minimise the window
            if self.dsh_offset == 320:
                self.dsh_offset = 0
            else:
                self.dsh_offset = 320
            window_width = 400 - self.dsh_offset
            window_height = 250
            screen_width = int(top.winfo_screenwidth() - window_width)
            screen_height = int(top.winfo_screenheight() - window_height - 40)
            top.geometry(f'{window_width}x{window_height}+{screen_width}+{screen_height}')
            c.coords(APP_ALIVE, 390 - self.dsh_offset, 0, 400 - self.dsh_offset, 10)
            c.coords(APP_MINIMIZE, 380 - self.dsh_offset, 0, 390 - self.dsh_offset, 10)
            c.coords(APP_MINIMIZE_ICO, 380 - self.dsh_offset, 5, 390 - self.dsh_offset, 5)
            c.pack()

        def update_data():
            # update function for seso and other dynamic data
            if self.useReader == True:
                self.card_id = hw.rfid_read(hw(self.COM, self.BAUD))
            if self.useSeso == True:
                self.pass_count, self.fail_count, self.fpy_perf, instr_list, module, self.lrf_perf, curr_perf = seso.updateProdData(seso(self.stationNo, self.sesoData))
                if int(self.card_id) == 0:
                    self.op_id, self.op_name, self.unlock, self.training = seso.operatorWithoutReader(seso(self.stationNo, self.sesoOperator))
                if self.useReader == True and int(self.card_id) > 0:
                    self.op_id, self.op_name, self.unlock, self.training = seso.operatorWithReader(seso(self.stationNo, self.sesoOperator), self.card_id, False)
            else:
                # Placeholder
                pass
            current_color = c.itemcget(APP_ALIVE, 'fill')
            if current_color == 'black':
                c.itemconfig(APP_ALIVE, fill = 'white')
            else:
                c.itemconfig(APP_ALIVE, fill = 'black')
            if self.fpy_perf >= self.greenFpy:
                c.itemconfig(fpy_graph, fill = '#72BE77')
            elif self.fpy_perf >= self.orangeFpy:
                c.itemconfig(fpy_graph, fill = '#DF9F69')
            else:
                c.itemconfig(fpy_graph, fill = '#4954D7')
            if self.lrf_perf >= 100:
                c.itemconfig(lrf_graph, fill = '#72BE77')
            else:
                c.itemconfig(lrf_graph, fill = '#4954D7')
            TOTAL_PCBS.config(text = 'Total: ' + str(self.pass_count + self.fail_count))
            PASS_PCBS.config(text = 'Passed: ' + str(self.pass_count))
            FAIL_PCBS.config(text = 'Failed: ' + str(self.fail_count))
            operator.config(text = self.op_id)
            c.itemconfig(fpy_graph, extent = 180 / 100 * self.fpy_perf)
            if self.lrf_perf > 100:
                self.lrf_perf = 100
            c.itemconfig(lrf_graph, extent = 180 / 100 * self.lrf_perf)
            sleep(0.5)

        instr_button = tkinter.Button(top, text = 'Instruction', command = '', width = 9, bd = 0, bg = self.graphBack, font = ('Arial 9'), fg = 'black')
        instr_button.place(x = 5, y = 224)

        gen_instr_button = tkinter.Button(top, text = 'General ins.', command = '', width = 9, bd = 0, bg = self.graphBack, font = ('Arial 9'), fg = 'black')
        gen_instr_button.place(x = 5, y = 201)

        APP_ALIVE = c.create_rectangle(390 - self.dsh_offset, 0, 400 - self.dsh_offset, 10, tags = 'APP_ALIVE')
        c.tag_bind('APP_ALIVE', '<Button-1>', main_exit)

        APP_MINIMIZE = c.create_rectangle(380 - self.dsh_offset, 0, 390 - self.dsh_offset, 10, tags = 'APP_MINIMIZE')
        APP_MINIMIZE_ICO = c.create_line(380 - self.dsh_offset, 5, 390 - self.dsh_offset, 5, tags = 'APP_MINIMIZE', fill = 'white')
        c.tag_bind('APP_MINIMIZE', '<Button-1>', minimize)
        c.tag_bind('APP_MINIMIZE_ICO', '<Button-1>', minimize)
        c.itemconfig(APP_MINIMIZE, fill = 'black')
        
        APP_NAME = tkinter.Label(top, text = 'Production Dashboard', bg = self.canvasBack, font = ('Arial 10'), fg = self.textColor)
        APP_NAME.place(x = 240, y = 10, anchor = 'center')
        
        operator = tkinter.Label(top, text = self.op_id, bg = self.canvasBack, font = ('Arial 14'), fg = self.textColor)
        operator.place(x = 240, y = 30, anchor = 'center')
        
        c.create_arc(-60, 0, 220, 250, start = 270, extent = 180, fill = self.graphBack, outline = '')
        fpy_graph = c.create_arc(-60, 0, 220, 250, start = 270, extent = 180, fill = self.graphColor, outline = '')
        c.create_arc(-20, 35, 180, 215, start = 270, extent = 180, fill = self.graphBack, outline = '')
        lrf_graph = c.create_arc(-20, 35, 180, 215, start = 270, extent = 180, fill = self.graphColor, outline = '')
        c.create_arc(20, 70, 140, 180, start = 270, extent = 180, fill = self.rectBack, outline = '')

        TOTAL_PCBS = tkinter.Label(top, text = 'Total: ' + str(self.pass_count + self.fail_count), bg = self.canvasBack, font = ('Arial 8'), fg = self.textColor)
        PASS_PCBS = tkinter.Label(top, text = 'Passed: ' + str(self.pass_count), bg = self.canvasBack, font = ('Arial 8'), fg = self.textColor)
        FAIL_PCBS = tkinter.Label(top, text = 'Failed: ' + str(self.fail_count), bg = self.canvasBack, font = ('Arial 8'), fg = self.textColor)
        TOTAL_PCBS.place(x = 230, y = 100)
        PASS_PCBS.place(x = 230, y = 115)
        FAIL_PCBS.place(x = 230, y = 130)

        if self.companyLogo != 'False':
            # Company logo
            try:
                img = Image.open(self.companyLogo)
                img = img.resize((75,45))
                photoImg =  ImageTk.PhotoImage(img)
                logo = tkinter.Label(top , image = photoImg , height = 45 , width = 75 , borderwidth = 0)
                logo.place(x = 323 , y = 203)
            except FileNotFoundError:
                windll.user32.MessageBoxW(0, 'Error 0x001 Image not found. Please check image name.', 'Error', 0x1000)
                logger.log_event(logger(), 'Error 0x001 Image not found.')

        # top.protocol('WM_DELETE_WINDOW', main_exit)

        while self.run:
            try:
                # Main loop for update the GUI
                top.update()
                update_data()
            except:
                windll.user32.MessageBoxW(0, 'Error 0x000 Undefined error in main.', 'Error', 0x1000)
                logger.log_event(logger(), 'Error 0x000 Undefined error in main.')

    def main():
        app.checkAppStatus()
        t0 = Thread(target = app.UI(app()))
        t0.start()

if __name__ == '__main__':
    sys.exit(app.main())