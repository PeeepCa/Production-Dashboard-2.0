from ctypes import windll
from library.logger_library import Logger


class Config:
    def __init__(self, *args):
        self.station_number = ''
        self.path = ''
        self.thread_number = ''
        self.rest_api = ''
        self.remove_file = ''
        self.seso_data = ''
        self.seso_operator = ''
        self.use_seso = ''
        self.use_itac = ''
        self.parse_log = ''
        self.use_reader = ''
        self.com = ''
        self.baud = ''
        self.green_fpy = ''
        self.orange_fpy = ''
        self.server_instr_gen = ''
        self.show_instr = ''
        self.use_login = ''
        self.company_logo = ''
        self.use_training = ''
        self.log_format = ''
        self.canvas_back = ''
        self.rect_back = ''
        self.graph_back = ''
        self.text_color = ''
        self.graph_color = ''

        file = open(args[0], 'r')
        self.temp = file.read(-1).splitlines()
        
    def read_config(self):
        try:
            for x in self.temp:
                if '##' in x:
                    continue
                elif 'stationNumber' in x:
                    self.station_number = x.split('=')[1]
                elif 'logPATH' in x:
                    self.path = x.split('=')[1]
                elif 'thread_number' in x:
                    self.thread_number = int(x.split('=')[1])
                elif 'restAPI' in x:
                    self.rest_api = x.split('=')[1]
                elif 'remove_file' in x:
                    self.remove_file = x.split('=')[1]
                    if self.remove_file == 'False':
                        self.remove_file = ''
                elif 'sesoData' in x:
                    self.seso_data = x.split('=')[1]
                elif 'sesoOperator' in x:
                    self.seso_operator = x.split('=')[1]
                elif 'SESO' in x:
                    self.use_itac = x.split('=')[1]
                    if self.use_itac == 'False':
                        self.use_itac = ''
                elif 'ITAC' in x:
                    self.use_seso = x.split('=')[1]
                    if self.use_seso == 'False':
                        self.use_seso = ''
                elif 'parse' in x:
                    self.parse_log = x.split('=')[1]
                    if self.parse_log == 'False':
                        self.parse_log = ''
                elif 'useReader' in x:
                    self.use_reader = x.split('=')[1]
                    if self.use_reader == 'False':
                        self.use_reader = ''
                elif 'COM' in x:
                    self.com = x.split('=')[1]
                elif 'Baud' in x:
                    self.baud = x.split('=')[1]
                elif 'greenFPY' in x:
                    self.green_fpy = x.split('=')[1]
                elif 'orangeFPY' in x:
                    self.orange_fpy = x.split('=')[1]
                elif 'instrGEN' in x:
                    self.server_instr_gen = x.split('=')[1]
                elif 'showInstr' in x:
                    self.show_instr = x.split('=')[1]
                    if self.show_instr == 'False':
                        self.show_instr = ''
                elif 'useLogin' in x:
                    self.use_login = x.split('=')[1]
                    if self.use_login == 'False':
                        self.use_login = ''
                elif 'company_logo' in x:
                    self.company_logo = x.split('=')[1]
                elif 'useTraining' in x:
                    self.use_training = x.split('=')[1]
                    if self.use_training == 'False':
                        self.use_training = ''
                elif 'log_format' in x:
                    self.log_format = x.split('=')[1]
                elif 'background_main' in x:
                    self.canvas_back = x.split('=')[1]
                elif 'background_second' in x:
                    self.rect_back = x.split('=')[1]
                elif 'default_graph' in x:
                    self.graph_back = x.split('=')[1]
                elif 'text_color' in x:
                    self.text_color = x.split('=')[1]
                elif 'background_graph' in x:
                    self.graph_color = x.split('=')[1]

            return (self.station_number, self.path, self.thread_number, self.rest_api, bool(self.remove_file),
                    self.seso_data, bool(self.use_seso), bool(self.parse_log), bool(self.use_reader),
                    self.com, self.baud, int(self.green_fpy), int(self.orange_fpy), bool(self.show_instr),
                    bool(self.use_login), self.company_logo, self.seso_operator, bool(self.use_training),
                    self.log_format, self.server_instr_gen, self.canvas_back, self.rect_back, self.graph_back,
                    self.text_color, self.graph_color), bool(self.use_itac)
    
        except UnboundLocalError:
            windll.user32.MessageBoxW(0, 'Error 0x101 Variable not found in config.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in config.')
        except NameError:
            windll.user32.MessageBoxW(0, 'Error 0x102 Variable not found in return of function.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in return of function.')
