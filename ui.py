# Dodělat iTAC
# Dodělat Logování
# Dodělat čtečku

import tkinter
import ctypes
from time import sleep
from PIL import ImageTk, Image
from library.seso_library import seso
from library.logger_library import logger

class UI:
    def __init__(self):
        self.canvasBack = 'white'
        self.rectBack = '#1f1fc2'
        self.graphBack = '#766fd2'
        self.textColor = '#1f1fc2'
        self.graphColor = '#4954D7'
        self.company_logo = '//fs/gs/IndustrialEngineering/Public/04_Testing/01_APPs/production/Configuration/apag logo.bmp'
        self.run = True
        self.dsh_offset = 0
        self.op_id = 0
        self.fpy_perf = 0
        self.lrf_perf = 0
        self.pass_count = 0
        self.fail_count = 0

    def main(self):
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
            self.run = False

        def minimize(*args):
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
            self.pass_count, self.fail_count, self.fpy_perf, instr_list, module, self.lrf_perf, curr_perf = seso.updateProdData(seso('40010021', 'https://seso.apag-elektronik.com/api/prod/'))
            current_color = c.itemcget(APP_ALIVE, 'fill')
            if current_color == 'black':
                c.itemconfig(APP_ALIVE, fill = 'white')
            else:
                c.itemconfig(APP_ALIVE, fill = 'black')
            if self.fpy_perf >= 98:
                c.itemconfig(fpy_graph, fill = '#72BE77')
            elif self.fpy_perf >= 95:
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
            c.itemconfig(fpy_graph, extent = 180 / 100 * self.fpy_perf)
            if self.lrf_perf > 100:
                self.lrf_perf = 100
            c.itemconfig(lrf_graph, extent = 180 / 100 * self.lrf_perf)
            sleep(1)

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

        if self.company_logo != 'False':
            try:
                img = Image.open(self.company_logo)
                img = img.resize((75,45))
                photoImg =  ImageTk.PhotoImage(img)
                logo = tkinter.Label(top , image = photoImg , height = 45 , width = 75 , borderwidth = 0)
                logo.place(x = 323 , y = 203)
            except FileNotFoundError:
                ctypes.windll.user32.MessageBoxW(0, 'Error 0x202 Image not found. Please check image name.', 'Error', 0x1000)
                logger.log_event(logger(), 'Error 0x202 Image not found.')

        top.protocol('WM_DELETE_WINDOW', main_exit)
        while self.run:
            top.update()
            update_data()
        top.quit()
        top.destroy()
        exit(0)

UI.main(UI())