from ctypes import windll
from library.logger_library import logger

class config:
    def __init__(self, *args):
        file = open(args[0], 'r')
        self.temp = file.read(-1).splitlines()
        self.station_number = ''
        self.path = ''
        self.thread_number = ''
        self.rest_api = ''
        self.remove_file = ''
        self.seso_data = ''
        self.seso_operator = ''
        self.use_seso = ''
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
        
    def read_config(self):
        try:
            for x in self.temp:
                if '##' in x:
                    continue
                elif 'stationNumber' in x:
<<<<<<< Updated upstream
                    stationNumber = x.split('=')[1]
                elif 'logPATH' in x:
                    PATH = x.split('=')[1]
=======
                    self.station_number = x.split('=')[1]
                elif 'logPATH' in x:
                    self.path = x.split('=')[1]
>>>>>>> Stashed changes
                elif 'thread_number' in x:
                    self.thread_number = int(x.split('=')[1])
                elif 'restAPI' in x:
<<<<<<< Updated upstream
                    restAPI = x.split('=')[1]
=======
                    self.rest_api = x.split('=')[1]
>>>>>>> Stashed changes
                elif 'remove_file' in x:
                    self.remove_file = x.split('=')[1]
                    if self.remove_file == 'False':
                        self.remove_file = ''
                elif 'sesoData' in x:
<<<<<<< Updated upstream
                    sesoData = x.split('=')[1]
                elif 'sesoOperator' in x:
                    sesoOperator = x.split('=')[1]
                elif 'SESO' in x:
                    useSESO = x.split('=')[1]
                    if useSESO == 'False':
                        useSESO = ''
                elif 'parse' in x:
                    parselog = x.split('=')[1]
                    if parselog == 'False':
                        parselog = ''
                elif 'useReader' in x:
                    useReader = x.split('=')[1]
                    if useReader == 'False':
                        useReader = ''
                elif 'COM' in x:
                    COM = x.split('=')[1]
                elif 'Baud' in x:
                    BAUD = x.split('=')[1]
                elif 'greenFPY' in x:
                    greenFPY = x.split('=')[1]
                elif 'orangeFPY' in x:
                    orangeFPY = x.split('=')[1]
                elif 'instrGEN' in x:
                    serverInstrGen = x.split('=')[1]
                elif 'showInstr' in x:
                    showIntr = x.split('=')[1]
                    if showIntr == 'False':
                        showIntr = ''
                elif 'useLogin' in x:
                    useLogin = x.split('=')[1]
                    if useLogin == 'False':
                        useLogin = ''
=======
                    self.seso_data = x.split('=')[1]
                elif 'sesoOperator' in x:
                    self.seso_operator = x.split('=')[1]
                elif 'SESO' in x:
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
>>>>>>> Stashed changes
                elif 'company_logo' in x:
                    self.company_logo = x.split('=')[1]
                elif 'useTraining' in x:
<<<<<<< Updated upstream
                    useTraining = x.split('=')[1]
                    if useTraining == 'False':
                        useTraining = ''
=======
                    self.use_training = x.split('=')[1]
                    if self.use_training == 'False':
                        self.use_training = ''
>>>>>>> Stashed changes
                elif 'log_format' in x:
                    self.log_format = x.split('=')[1]
                elif 'background_main' in x:
<<<<<<< Updated upstream
                    canvasBack = x.split('=')[1]
                elif 'background_second' in x:
                    rectBack = x.split('=')[1]
                elif 'default_graph' in x:
                    graphBack = x.split('=')[1]
                elif 'text_color' in x:
                    textColor = x.split('=')[1]
                elif 'background_graph' in x:
                    graphColor = x.split('=')[1]

            return stationNumber, PATH, thread_number, restAPI, bool(remove_file), sesoData, bool(useSESO), bool(parselog), bool(useReader), COM, BAUD, int(greenFPY), int(orangeFPY), bool(showIntr), bool(useLogin), company_logo, sesoOperator, bool(useTraining), log_format, serverInstrGen, canvasBack, rectBack, graphBack, textColor, graphColor
=======
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
                    self.seso_data, bool(self.use_seso), bool(self.parse_log), bool(self.use_reader), self.com,
                    self.baud, int(self.green_fpy), int(self.orange_fpy), bool(self.show_instr),
                    bool(self.use_login), self.company_logo, self.seso_operator, bool(self.use_training),
                    self.log_format, self.server_instr_gen, self.canvas_back, self.rect_back, self.graph_back,
                    self.text_color, self.graph_color)
>>>>>>> Stashed changes
    
        except UnboundLocalError:
            windll.user32.MessageBoxW(0, 'Error 0x101 Variable not found in config.', 'Error', 0x1000)
            logger.log_event(logger(), 'Variable not found in config.')
        except NameError:
            windll.user32.MessageBoxW(0, 'Error 0x102 Variable not found in return of function.', 'Error', 0x1000)
            logger.log_event(logger(), 'Variable not found in return of function.')