from ctypes import windll
from library.logger_library import logger

class config:
    def __init__(self, *args):
        file = open(args[0], 'r')
        self.temp = file.read(-1).splitlines()
        
    def read_config(self):
        try:
            for x in self.temp:
                if '##' in x:
                    continue
                elif 'stationNumber' in x:
                    stationNumber = x.split('=')[1]
                elif 'logPATH' in x:
                    PATH = x.split('=')[1]
                elif 'thread_number' in x:
                    thread_number = int(x.split('=')[1])
                elif 'restAPI' in x:
                    restAPI = x.split('=')[1]
                elif 'remove_file' in x:
                    remove_file = x.split('=')[1]
                    if remove_file == 'False':
                        remove_file = ''
                elif 'sesoData' in x:
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
                elif 'company_logo' in x:
                    company_logo = x.split('=')[1]
                elif 'useTraining' in x:
                    useTraining = x.split('=')[1]
                    if useTraining == 'False':
                        useTraining = ''
                elif 'log_format' in x:
                    log_format = x.split('=')[1]
                elif 'background_main' in x:
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
    
        except UnboundLocalError:
            windll.user32.MessageBoxW(0, 'Error 0x101 Variable not found in config.', 'Error', 0x1000)
            logger.log_event(logger(), 'Variable not found in config.')
        except NameError:
            windll.user32.MessageBoxW(0, 'Error 0x102 Variable not found in return of function.', 'Error', 0x1000)
            logger.log_event(logger(), 'Variable not found in return of function.')