from ctypes import windll
from library.logger_library import Logger


class Config:
    def __init__(self, *args):
        file = open(args[0], 'r')
        self.temp = file.read(-1).splitlines()
        
    def read_config(self):
        try:
            for x in self.temp:
                if '##' in x:
                    continue
                elif 'stationNumber' in x:
                    station_number = x.split('=')[1]
                elif 'logPATH' in x:
                    path = x.split('=')[1]
                elif 'thread_number' in x:
                    thread_number = int(x.split('=')[1])
                elif 'restAPI' in x:
                    rest_api = x.split('=')[1]
                elif 'remove_file' in x:
                    remove_file = x.split('=')[1]
                    if remove_file == 'False':
                        remove_file = ''
                elif 'sesoData' in x:
                    seso_data = x.split('=')[1]
                elif 'sesoOperator' in x:
                    seso_operator = x.split('=')[1]
                elif 'SESO' in x:
                    use_seso = x.split('=')[1]
                    if use_seso == 'False':
                        use_seso = ''
                elif 'parse' in x:
                    parse_log = x.split('=')[1]
                    if parse_log == 'False':
                        parse_log = ''
                elif 'useReader' in x:
                    use_reader = x.split('=')[1]
                    if use_reader == 'False':
                        use_reader = ''
                elif 'COM' in x:
                    com = x.split('=')[1]
                elif 'Baud' in x:
                    baud = x.split('=')[1]
                elif 'greenFPY' in x:
                    green_fpy = x.split('=')[1]
                elif 'orangeFPY' in x:
                    orange_fpy = x.split('=')[1]
                elif 'instrGEN' in x:
                    server_instr_gen = x.split('=')[1]
                elif 'showInstr' in x:
                    show_instr = x.split('=')[1]
                    if show_instr == 'False':
                        show_instr = ''
                elif 'useLogin' in x:
                    use_login = x.split('=')[1]
                    if use_login == 'False':
                        use_login = ''
                elif 'company_logo' in x:
                    company_logo = x.split('=')[1]
                elif 'useTraining' in x:
                    use_training = x.split('=')[1]
                    if use_training == 'False':
                        use_training = ''
                elif 'log_format' in x:
                    log_format = x.split('=')[1]
                elif 'background_main' in x:
                    canvas_back = x.split('=')[1]
                elif 'background_second' in x:
                    rect_back = x.split('=')[1]
                elif 'default_graph' in x:
                    graph_back = x.split('=')[1]
                elif 'text_color' in x:
                    text_color = x.split('=')[1]
                elif 'background_graph' in x:
                    graph_color = x.split('=')[1]

            return (station_number, path, thread_number, rest_api, bool(remove_file), seso_data, bool(use_seso),
                    bool(parse_log), bool(use_reader), com, baud, int(green_fpy), int(orange_fpy), bool(show_instr),
                    bool(use_login), company_logo, seso_operator, bool(use_training), log_format, server_instr_gen,
                    canvas_back, rect_back, graph_back, text_color, graph_color)
    
        except UnboundLocalError:
            windll.user32.MessageBoxW(0, 'Error 0x101 Variable not found in config.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in config.')
        except NameError:
            windll.user32.MessageBoxW(0, 'Error 0x102 Variable not found in return of function.', 'Error', 0x1000)
            Logger.log_event(Logger(), 'Variable not found in return of function.')
