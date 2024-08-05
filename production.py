# Production dashboard
#
# App is using SESO, ITAC, and it parses log files in defined folder.
# Everything is defined in config files.
# Config files are located in main folder in folder configuration.
# Updates are done by checking up production.bat, if version was changed it ll automatically restart app.
# New repo is on GitHub.
# Implemented FIFO for log files.

# TODO
#  Finnish iTAC - DONE
#  Finnish logging - DONE
#  Finnish reader - DONE
#  Finnish offline mode - DONE
#  Finnish muster
#  Try exe build - DONE
#  Multithreading - DONE
#  Add locking screen - DONE
#  Add when data send to itac and timeout try again
#  Add autoupdating - DONE
#  Add sharepoint support for instructions
#  When they swap cards too fast, it wont relog the operator - DONE
#  Add ACA testers


import tkinter
import sys
import library.shared_varriables

from psutil import process_iter
from threading import Thread
from ctypes import windll
from os import path, chdir, startfile
from socket import gethostname
from time import sleep
from PIL import ImageTk, Image
from traceback import format_exc

from library.seso_library import Seso
from library.logger_library import Logger
from library.config_library import Config
from library.hw_library import Hw
from library.parser_library import Parser


class App:
    def __init__(self):
        # init for all the default data + readout of the config file
        Logger.log_event(Logger(), 'Logging started.')
        if getattr(sys, 'frozen', False):
            self.application_path = path.dirname(sys.executable)
        elif __file__:
            self.application_path = path.dirname(__file__)
        else:
            self.application_path = None
        try:
            temp = Config.read_config(Config(self.application_path.rsplit('\\', 1)[0] + '/Configuration/'
                                             + gethostname() + '.ini'))
        except FileNotFoundError:
            windll.user32.MessageBoxW(0, 'Error 0x100 Config file not found', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Error 0x100 Config file not found. ' + format_exc())
            sys.exit()
        self.stationNo = temp[0]
        self.path = temp[1]
        self.threadCount = temp[2]
        self.itac_restApi = temp[3]
        self.remove_file = temp[4]
        self.sesoData = temp[5]
        self.useSeso = temp[6]
        self.parse_log = temp[7]
        self.useReader = temp[8]
        self.COM = temp[9]
        self.BAUD = temp[10]
        self.greenFpy = temp[11]
        self.orangeFpy = temp[12]
        self.useLogin = temp[14]
        self.companyLogo = temp[15]
        self.sesoOperator = temp[16]
        self.useTraining = temp[17]
        self.log_format = temp[18]
        self.canvasBack = temp[20]
        self.rectBack = temp[21]
        self.graphBack = temp[22]
        self.textColor = temp[23]
        self.graphColor = temp[24]
        self.useItac = temp[25]
        self.processLayer = temp[26]

        self.run = True
        self.dsh_offset = 0
        self.label_offset = 0
        self.operator_offset = 0
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
        self.logged = False
        self.lock_timeout = 0
        self.primary = False
        self.card_id_prev = self.card_id
        self.unlock_after = False

        App.check_app_status()

        if self.useSeso:
            if self.useLogin:
                self.logged = Seso.login_logout(Seso(self.stationNo,
                                                     self.sesoOperator),
                                                self.op_name,
                                                self.op_id, self.unlock, 'OUT')
        if self.useReader:
            self.useReader = Hw.rfid_open(Hw(self.COM, self.BAUD))
        if self.threadCount > 8:
            self.threadCount = 8
        elif self.threadCount <= 1:
            self.threadCount = 1

    @staticmethod
    def update_app(self):
        # Update procedure
        # Checking if folder name is actually same as name inside the production.bat
        if getattr(sys, 'frozen', False):
            app_version = self.application_path.rsplit('\\', 1)[1]
            batch_location = self.application_path.rsplit('\\', 1)[0] + '\\production.bat'
            file = open(batch_location, 'r')
            temp = file.read(-1).splitlines()[11].rsplit('\\', 2)[1]
            if temp != app_version:
                Logger.log_event(Logger(), 'App update to version: ' + temp + '.')
                chdir(self.application_path.rsplit('\\', 1)[0])
                startfile('update.bat')
                if self.useReader:
                    self.useReader = Hw.rfid_close()
                library.shared_varriables.run_thread = False
                self.run = False

    @staticmethod
    def check_app_status():
        # On the beginning there s check if app is already running
        n = 0
        for p in process_iter(attrs=['pid', 'name']):
            if p.info['name'] == 'production.exe':
                n = n + 1
                if n > 2:
                    windll.user32.MessageBoxW(0, 'Error 0x204 App is already running', 'Error', 0x1000)
                    Logger.log_event(Logger(), 'Error 0x204 App is already running. ' + format_exc())
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

        # Lockscreen
        lock = tkinter.Tk()
        lock.geometry()
        lock.config(bg='white')
        lock.attributes('-alpha', 0.8)
        lock.overrideredirect(True)
        lock.anchor('center')
        lock_text = tkinter.Label(lock, text=self.training, font='Helvetica 40 bold', bg='white')
        lock_text.place(x=self.screen_width / 2, y=self.screen_height / 2)

        def main_exit(*_):
            # just the exit which stops the main loop
            Logger.log_event(Logger(), 'App exit by button.')
            if self.useReader:
                self.useReader = Hw.rfid_close()
            library.shared_varriables.run_thread = False
            self.run = False

        def minimize(*_):
            # minimise the window
            if self.dsh_offset == 320:
                self.dsh_offset = 0
                self.label_offset = 0
                self.operator_offset = 0
                total_pcbs.config(fg=self.textColor, bg=self.canvasBack)
                pass_pcbs.config(fg=self.textColor, bg=self.canvasBack)
                fail_pcbs.config(fg=self.textColor, bg=self.canvasBack)
                operator.config(fg=self.textColor, bg=self.canvasBack)
            else:
                self.dsh_offset = 320
                self.label_offset = 225
                self.operator_offset = 200
                total_pcbs.config(fg=self.canvasBack, bg=self.textColor)
                pass_pcbs.config(fg=self.canvasBack, bg=self.textColor)
                fail_pcbs.config(fg=self.canvasBack, bg=self.textColor)
                operator.config(fg=self.canvasBack, bg=self.textColor)
            self.window_width = 400 - self.dsh_offset
            self.window_height = 250
            self.screen_width = int(top.winfo_screenwidth() - self.window_width)
            self.screen_height = int(top.winfo_screenheight() - self.window_height - 40)
            top.geometry(f'{self.window_width}x{self.window_height}+{self.screen_width}+{self.screen_height}')
            c.coords(app_alive, 390 - self.dsh_offset, 0, 400 - self.dsh_offset, 10)
            c.coords(app_minimize, 380 - self.dsh_offset, 0, 390 - self.dsh_offset, 10)
            c.coords(app_minimize_ico, 380 - self.dsh_offset, 5, 390 - self.dsh_offset, 5)
            c.pack()
            total_pcbs.place(x=230 - self.label_offset, y=100)
            pass_pcbs.place(x=230 - self.label_offset, y=115)
            fail_pcbs.place(x=230 - self.label_offset, y=130)
            operator.place(x=240 - self.operator_offset, y=30)

        def screen_lock():
            # Screen lock
            top.attributes('-topmost', 0)
            lock.geometry(f'{int(top.winfo_screenwidth())}x{int(top.winfo_screenheight())}')
            lock.attributes('-topmost', 1)

        def screen_unlock():
            # Screen unlock
            lock.geometry('0x0')
            lock.attributes('-topmost', 0)
            top.attributes('-topmost', 1)

        def operator_perf():
            # Update colors and data for frontend
            if self.useSeso:
                (self.pass_count, self.fail_count, self.fpy_perf, instr_list, module, self.lrf_perf,
                 curr_perf) = Seso.update_prod_data(Seso(self.stationNo, self.sesoData))
            else:
                # Offline mode
                self.pass_count = library.shared_varriables.pass_count
                self.fail_count = library.shared_varriables.fail_count
                self.fpy_perf = (((self.pass_count + self.fail_count) - self.fail_count) /
                                 (self.pass_count + self.fail_count) * 100)
                self.lrf_perf = 0
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
            lock_text.config(text=self.training)
            c.itemconfig(fpy_graph, extent=180 / 100 * self.fpy_perf)
            if self.lrf_perf > 100:
                self.lrf_perf = 100
            c.itemconfig(lrf_graph, extent=180 / 100 * self.lrf_perf)

        def update_data():
            if self.useSeso:
                if self.useReader:
                    try:
                        self.card_id = Hw.rfid_read(self)
                        if len(self.card_id) >= 4:
                            # Added because they sometimes swap the cards before timer ends
                            # Check the card ID and if its different then before it ll log out operator
                            if self.card_id_prev != self.card_id:
                                self.op_id, self.op_name, self.unlock, self.training = Seso.operator_with_reader(
                                    Seso(self.stationNo, self.sesoOperator), self.card_id_prev, self.useTraining)
                                self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                     self.sesoOperator),
                                                                self.op_name, self.op_id, 'OUT')
                                self.card_id_prev = self.card_id
                            else:
                                self.op_id, self.op_name, self.unlock, self.training = Seso.operator_with_reader(
                                    Seso(self.stationNo, self.sesoOperator), self.card_id, self.useTraining)
                                self.card_id_prev = self.card_id
                            if self.useLogin and self.unlock:
                                if self.logged is False:
                                    self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                         self.sesoOperator),
                                                                    self.op_name, self.op_id, 'IN')
                                    screen_unlock()
                                    self.primary = True
                                elif self.unlock_after:
                                    screen_unlock()
                                    self.unlock_after = False
                                self.lock_timeout = 10
                        else:
                            self.training = 'Card disconnected'
                            self.op_id = str(self.lock_timeout)
                            if self.lock_timeout > 0:
                                self.lock_timeout -= 1
                                screen_unlock()
                            if self.lock_timeout == 0:
                                screen_lock()
                                if self.useLogin and self.logged:
                                    self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                         self.sesoOperator),
                                                                    self.op_name, self.op_id, 'OUT')
                                    self.primary = False
                        if self.primary is False:
                            self.op_id, self.op_name, self.unlock, self.training = Seso.operator_without_reader(
                                Seso(self.stationNo, self.sesoOperator))
                            if self.useLogin:
                                if self.unlock:
                                    if self.logged is False:
                                        self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                             self.sesoOperator),
                                                                        self.op_name, self.op_id, 'IN')
                                        screen_unlock()
                                    self.lock_timeout = 10
                                else:
                                    self.training = 'Not logged in'
                                    screen_lock()
                                    if self.logged:
                                        self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                             self.sesoOperator),
                                                                        self.op_name, self.op_id, 'OUT')
                            else:
                                screen_unlock()
                    except TypeError:
                        sleep(1)
                        self.training = 'Card reader error'
                        screen_lock()
                        self.unlock_after = True
                else:
                    self.op_id, self.op_name, self.unlock, self.training = Seso.operator_without_reader(
                        Seso(self.stationNo, self.sesoOperator))
                    if self.useLogin:
                        if self.unlock:
                            if self.logged is False:
                                self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                     self.sesoOperator),
                                                                self.op_name, self.op_id, 'IN')
                                screen_unlock()
                            self.lock_timeout = 10
                        else:
                            self.training = 'Not logged in'
                            screen_lock()
                            if self.logged:
                                self.logged = Seso.login_logout(Seso(self.stationNo,
                                                                     self.sesoOperator),
                                                                self.op_name, self.op_id, 'OUT')
                    else:
                        screen_unlock()
            else:
                screen_unlock()
                if self.useReader is False:
                    sleep(0.5)
            operator_perf()
            App.update_app(self)
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
                Logger.log_event(Logger(), 'Error 0x001 Image not found. ' + format_exc())

        top.protocol('WM_DELETE_WINDOW', main_exit)
        while self.run:
            try:
                # Main loop for update the GUI
                top.update()
                update_data()
            except FileNotFoundError:
                windll.user32.MessageBoxW(0, 'Error 0x201 Instruction not found.', 'Error', 0x1000)
                Logger.log_event(Logger(), 'Error 0x201 Instruction not found. ' + format_exc())
                continue
            except IOError:
                if self.useSeso:
                    if self.useLogin and self.logged:
                        self.logged = Seso.login_logout(Seso(self.stationNo,
                                                             self.sesoOperator),
                                                        self.op_name, self.op_id, 'OUT')
                continue
            except tkinter.TclError:
                self.logged = Seso.login_logout(Seso(self.stationNo,
                                                     self.sesoOperator),
                                                self.op_name, self.op_id, 'OUT')
                main_exit()
            except KeyboardInterrupt:
                pass
            except (Exception, BaseException):
                windll.user32.MessageBoxW(0, 'Error 0x000 Undefined error in main.' + format_exc(), 'Error', 0x1000)
                Logger.log_event(Logger(), 'Error 0x000 Undefined error in main. ' + format_exc())
        top.destroy()

    def main(self):
        t0 = Thread(target=self.ui)
        t0.start()
        if self.parse_log:
            if self.threadCount == 1:
                t1 = Thread(target=Parser.main, daemon=True, args=(Parser(self.run, self.path, self.log_format,
                                                                          self.useItac, self.useSeso,
                                                                          self.remove_file, self.stationNo,
                                                                          self.itac_restApi, self.sesoData,
                                                                          self.processLayer),))
                t1.start()
                t0.join(1)
                t1.join(1)
            else:
                for i in range(1, self.threadCount):
                    t = Thread(target=Parser.main, daemon=True, args=(Parser(self.run, self.path, self.log_format,
                                                                             self.useItac, self.useSeso,
                                                                             self.remove_file, self.stationNo,
                                                                             self.itac_restApi, self.sesoData,
                                                                             self.processLayer),))
                    t.start()


if __name__ == '__main__':
    sys.exit(App.main(App()))
