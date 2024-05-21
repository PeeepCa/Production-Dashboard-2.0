# Finnish iTAC
# Finnish logging - Done
# Finnish reader - Done
# Finnish offline mode
# Finnish muster
# Try exe build - Done
# Multithreading - Partially done
# Add locking screen
# Add when data send to itac and timeout try again

import tkinter
import sys
from psutil import process_iter
from threading import Thread
from ctypes import windll
from os import path
from socket import gethostname
from time import sleep
from PIL import ImageTk, Image
from library.seso_library import Seso
from library.logger_library import Logger
from library.config_library import Config
from library.hw_library import Hw


class App:
    def __init__(self):
        # init for all the default data + readout of the config file
        Logger.log_event(Logger(), 'Logging started.')
        if getattr(sys, 'frozen', False):
            application_path = path.dirname(sys.executable)
        elif __file__:
            application_path = path.dirname(__file__)
        else:
            application_path = None
        temp = Config.read_config(Config(application_path + '/Configuration/' + gethostname() + '.ini'))
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
        self.op_name = None
        self.unlock = False
        self.training = None
        self.card_id = '0'
        self.window_width = None
        self.window_height = None
        self.screen_width = None
        self.screen_height = None
        if self.useReader:
            self.useReader = Hw.rfid_open(Hw(self.COM, self.BAUD))

    @staticmethod
    def check_app_status():
        n = 0
        for p in process_iter(attrs=['pid', 'name']):
            if p.info['name'] == 'production.exe':
                n = n + 1
                if n > 2:
                    windll.user32.MessageBoxW(0, 'Error 0x204 App is already running', 'Error', 0x1000)
                    sys.exit()

    def ui(self):
        top = tkinter.Tk()
        self.window_width = 400 - self.dsh_offset
        self.window_height = 250
        self.screen_width = int(top.winfo_screenwidth() - self.window_width)
        self.screen_height = int(top.winfo_screenheight() - self.window_height - 40)
        top.title('Dashboard')
        top.geometry(f'{self.window_width}x{self.window_height}+{self.screen_width}+{self.screen_height}')
        top.config(bg='#484179')
        top.attributes('-alpha', 0.8)
        top.overrideredirect(True)
        top.anchor('center')
        top.attributes('-topmost', 1)
        c = tkinter.Canvas(width=400, height=250, bg=self.canvasBack, bd=-2)
        c.create_rectangle(0, 0, 80, 250, tags='ch', fill=self.rectBack, width=0)
        c.pack()

        def main_exit(*args):
            # just the exit which stops the main loop
            Logger.log_event(Logger(), 'App exit by button.')
            if self.useReader:
                self.useReader = Hw.rfid_close()
            self.run = False

        def minimize(*args):
            # minimise the window
            if self.dsh_offset == 320:
                self.dsh_offset = 0
            else:
                self.dsh_offset = 320
            self.window_width = 400 - self.dsh_offset
            self.window_height = 250
            self.screen_width = int(top.winfo_screenwidth() - self.window_width)
            self.screen_height = int(top.winfo_screenheight() - self.window_height - 40)
            top.geometry(f'{self.window_width}x{self.window_height}+{self.screen_width}+{self.screen_height}')
            c.coords(app_alive, 390 - self.dsh_offset, 0, 400 - self.dsh_offset, 10)
            c.coords(app_minimize, 380 - self.dsh_offset, 0, 390 - self.dsh_offset, 10)
            c.coords(app_minimize_ico, 380 - self.dsh_offset, 5, 390 - self.dsh_offset, 5)
            c.pack()

        def update_data():
            # update function for seso and other dynamic data
            if self.useReader:
                self.card_id = Hw.rfid_read(self)
            if self.useSeso:
                (self.pass_count, self.fail_count, self.fpy_perf, instr_list, module, self.lrf_perf,
                 curr_perf) = Seso.update_prod_data(Seso(self.stationNo, self.sesoData))
                if int(self.card_id) == 0:
                    self.op_id, self.op_name, self.unlock, self.training = Seso.operator_without_reader(
                        Seso(self.stationNo, self.sesoOperator))
                if self.useReader is True and int(self.card_id) > 0:
                    self.op_id, self.op_name, self.unlock, self.training = Seso.operator_with_reader(
                        Seso(self.stationNo, self.sesoOperator), self.card_id, False)
            else:
                # Placeholder
                pass
            current_color = c.itemcget(app_alive, 'fill')
            if current_color == 'black':
                c.itemconfig(app_alive, fill='white')
            else:
                c.itemconfig(app_alive, fill='black')
            if self.fpy_perf >= self.greenFpy:
                c.itemconfig(fpy_graph, fill='#72BE77')
            elif self.fpy_perf >= self.orangeFpy:
                c.itemconfig(fpy_graph, fill='#DF9F69')
            else:
                c.itemconfig(fpy_graph, fill='#df6f69')
            if self.lrf_perf >= 100:
                c.itemconfig(lrf_graph, fill='#72BE77')
            else:
                c.itemconfig(lrf_graph, fill='#4954D7')
            total_pcbs.config(text='Total: ' + str(self.pass_count + self.fail_count))
            pass_pcbs.config(text='Passed: ' + str(self.pass_count))
            fail_pcbs.config(text='Failed: ' + str(self.fail_count))
            operator.config(text=self.op_id)
            c.itemconfig(fpy_graph, extent=180 / 100 * self.fpy_perf)
            if self.lrf_perf > 100:
                self.lrf_perf = 100
            c.itemconfig(lrf_graph, extent=180 / 100 * self.lrf_perf)
            sleep(0.5)

        instr_button = tkinter.Button(top, text='Instruction', command='', width=9, bd=0, bg=self.graphBack,
                                      font='Arial 9', fg='black')
        instr_button.place(x=5, y=224)

        gen_instr_button = tkinter.Button(top, text='General ins.', command='', width=9, bd=0, bg=self.graphBack,
                                          font='Arial 9', fg='black')
        gen_instr_button.place(x=5, y=201)

        app_alive = c.create_rectangle(390 - self.dsh_offset, 0, 400 - self.dsh_offset, 10, tags='APP_ALIVE')
        c.tag_bind('APP_ALIVE', '<Button-1>', main_exit)

        app_minimize = c.create_rectangle(380 - self.dsh_offset, 0, 390 - self.dsh_offset, 10, tags='app_minimize')
        app_minimize_ico = c.create_line(380 - self.dsh_offset, 5, 390 - self.dsh_offset, 5, tags='app_minimize',
                                         fill='white')
        c.tag_bind('app_minimize', '<Button-1>', minimize)
        c.tag_bind('app_minimize_ico', '<Button-1>', minimize)
        c.itemconfig(app_minimize, fill='black')

        app_name = tkinter.Label(top, text='Production Dashboard', bg=self.canvasBack, font='Arial 10',
                                 fg=self.textColor)
        app_name.place(x=240, y=10, anchor='center')

        operator = tkinter.Label(top, text=self.op_id, bg=self.canvasBack, font='Arial 14', fg=self.textColor)
        operator.place(x=240, y=30, anchor='center')

        c.create_arc(-60, 0, 220, 250, start=270, extent=180, fill=self.graphBack, outline='')
        fpy_graph = c.create_arc(-60, 0, 220, 250, start=270, extent=180, fill=self.graphColor, outline='')
        c.create_arc(-20, 35, 180, 215, start=270, extent=180, fill=self.graphBack, outline='')
        lrf_graph = c.create_arc(-20, 35, 180, 215, start=270, extent=180, fill=self.graphColor, outline='')
        c.create_arc(20, 70, 140, 180, start=270, extent=180, fill=self.rectBack, outline='')

        total_pcbs = tkinter.Label(top, text='Total: ' + str(self.pass_count + self.fail_count), bg=self.canvasBack,
                                   font='Arial 8', fg=self.textColor)
        pass_pcbs = tkinter.Label(top, text='Passed: ' + str(self.pass_count), bg=self.canvasBack, font='Arial 8',
                                  fg=self.textColor)
        fail_pcbs = tkinter.Label(top, text='Failed: ' + str(self.fail_count), bg=self.canvasBack, font='Arial 8',
                                  fg=self.textColor)
        total_pcbs.place(x=230, y=100)
        pass_pcbs.place(x=230, y=115)
        fail_pcbs.place(x=230, y=130)

        if self.companyLogo != 'False':
            # Company logo
            try:
                img = Image.open(self.companyLogo)
                img = img.resize((75, 45))
                photo_img = ImageTk.PhotoImage(img)
                logo = tkinter.Label(top, image=photo_img, height=45, width=75, borderwidth=0)
                logo.place(x=323, y=203)
            except FileNotFoundError:
                windll.user32.MessageBoxW(0, 'Error 0x001 Image not found. Please check image name.', 'Error', 0x1000)
                Logger.log_event(Logger(), 'Error 0x001 Image not found. ' + str(sys.exc_info()))

        top.protocol('WM_DELETE_WINDOW', main_exit)
        while self.run:
            try:
                # Main loop for update the GUI
                top.update()
                update_data()
            except KeyboardInterrupt:
                pass
            except:
                windll.user32.MessageBoxW(0, 'Error 0x000 Undefined error in main.', 'Error', 0x1000)
                Logger.log_event(Logger(), 'Error 0x000 Undefined error in main. ' + str(sys.exc_info()))

        top.destroy()

    @staticmethod
    def main():
        App.check_app_status()
        t0 = Thread(target=App.ui(App()))
        t0.start()


if __name__ == '__main__':
    sys.exit(App.main())
