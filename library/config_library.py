from ctypes import windll
from library.logger_library import Logger
from traceback import format_exc


class Config:
    """
    Read config. Path should be sent as first argument.
    :param file: Config file to read.
    """
    def __init__(self, file):
        self.station_number = None
        self.path = None
        self.thread_number = None
        self.rest_api = None
        self.remove_file = None
        self.seso_data = None
        self.seso_operator = None
        self.use_seso = None
        self.use_itac = None
        self.parse_log = None
        self.use_reader = None
        self.com = None
        self.baud = None
        self.green_fpy = None
        self.orange_fpy = None
        self.server_instr_gen = None
        self.show_instr = None
        self.use_login = None
        self.company_logo = None
        self.use_training = None
        self.log_format = None
        self.canvas_back = None
        self.rect_back = None
        self.graph_back = None
        self.text_color = None
        self.graph_color = None
        self.process_layer = None

        file = open(file, 'r')
        self.temp = file.read(-1).splitlines()
        
    def read_config(self):
        """
        Read config. Path should be sent as first argument
        :return: 0-station_number, 1-path, 2-thread_number, 3-rest_api, 4-remove_file,
                    5-seso_data, 6-use_seso, 7-parse_log, 8-use_reader,
                    9-com, 10-baud, 11-green_fpy, 12-orange_fpy, 13-show_instr,
                    14-use_login, 15-company_logo, 16-seso_operator, 17-use_training,
                    18-log_format, 19-server_instr_gen, 20-canvas_back, 21-rect_back, 22-graph_back,
                    23-text_color, 24-graph_color, 25-use_itac, 26-process_layer
        """
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
                    self.use_seso = x.split('=')[1]
                    if self.use_seso == 'False':
                        self.use_seso = ''
                elif 'ITAC' in x:
                    self.use_itac = x.split('=')[1]
                    if self.use_itac == 'False':
                        self.use_itac = ''
                elif 'processLayer' in x:
                    self.process_layer = x.split('=')[1]
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
                    self.text_color, self.graph_color, bool(self.use_itac), self.process_layer)
    
        except UnboundLocalError:
            windll.user32.MessageBoxW(0, 'Error 0x101 Variable not found in config.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in config. ' + format_exc())
        except NameError:
            windll.user32.MessageBoxW(0, 'Error 0x102 Variable not found in return of function.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in return of function. ' + format_exc())
