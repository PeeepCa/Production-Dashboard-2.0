import library.shared_varriables

from datetime import date, datetime
from threading import BoundedSemaphore
from time import sleep, time
from os import listdir, replace, path, remove
from ctypes import windll
from sys import exc_info
from re import match, split
from glob import iglob
from traceback import format_exc

from library.itac_library import Itac
from library.seso_library import Seso
from library.logger_library import Logger


class Parser:
    """
    Read config. Path should be sent as first argument
    :param run: Boolean value if thread should run
    :param log_path: Path to read
    :param what_to_handle: What to handle
    :param use_itac: Boolean value if itac should be used
    :param use_seso: Boolean value if seso should be used
    :param remove_file: Boolean value if file should be removed
    :param station_number: station number
    :param itac_restapi: itac rest api
    :param seso_restapi: seso rest api
    :param process_layer: process layer
    """
    def __init__(self, run, log_path, what_to_handle, use_itac, use_seso, remove_file, station_number, itac_restapi,
                 seso_restapi, process_layer):
        self.run = run
        self.path = log_path
        self.what_to_handle = what_to_handle
        self.use_itac = use_itac
        self.use_seso = use_seso
        self.remove_file = remove_file
        self.station_number = station_number
        self.itac_restApi = itac_restapi
        self.seso_restApi = seso_restapi
        self.process_layer = process_layer
        self.start_number = None
        self.split_path = None
        self.tLock = BoundedSemaphore(value=1)
        self.sn = None
        self.multi_panel = None
        self.pos = None
        self.meas_fail_code = None
        self.itac_pos = None
        self.test_result = None
        self.itac_desc = None
        self.itac_wa = None
        self.status = None
        if self.use_itac:
            Itac.login(Itac(self.station_number, self.itac_restApi))

    def rexxam_handle(self):
        while self.run:
            sleep(0.001)
            self.run = library.shared_varriables.run_thread
            # We do not want to crash if the production does not run
            # This ll crash only till the production start
            try:
                date_v = str(date.today()).replace('-', '') + '\\'
                if len(listdir(path=self.path + date_v)) > 0:
                    try:
                        start_time = time()
                        ########################################################
                        self.tLock.acquire()
                        ########################################################
                        # Main function definition
                        ########################################################
                        upload_values = ''
                        number_of_records = 0
                        name_prev = ''
                        name_a = 0
                        name_b = 0
                        name_c = 0
                        name_d = 0
                        name_e = 0

                        oldest = min(iglob(self.path + date + '*.[Dd][Aa][Tt]'), key=path.getctime)

                        with open(oldest, 'r') as file_opened:
                            data = file_opened.read(-1)
                            data = data.splitlines()
                            size = len(data)

                        if self.remove_file:
                            self.split_path = oldest.rsplit('\\', 1)
                            replace(oldest, self.split_path[0][:-8] + '\\PROBLEMS\\' + str(start_time) +
                                    self.split_path[1])

                        self.tLock.release()

                        result_data = data[0].split(',')
                        if 'OK' in result_data[8] and 'OK' in result_data[9]:
                            self.test_result = '0'
                            self.status = 'pass'
                        else:
                            self.test_result = '1'
                            self.status = 'fail'
                        self.sn = data[0].split(',')
                        self.sn = self.sn[5] + self.sn[4] + 'E9'

                        if self.use_itac:
                            if Itac.sn_state(Itac(self.station_number, self.itac_restApi),
                                             self.sn) != '0' and Itac.sn_state(self, self.sn) != '212':
                                continue

                            itac_data = Itac.sn_info(Itac(self.station_number,
                                                          self.itac_restApi), self.sn)
                            self.itac_wa = itac_data[2]
                            self.itac_desc = itac_data[1]
                            self.itac_pos = itac_data[3]

                            for x in range(size):
                                raw_data = data[x].replace(' ', '').split(',')
                                if 'CP=' not in raw_data[9]:
                                    name = raw_data[1].replace('MR', 'R').replace('MC', 'C')
                                    value = raw_data[13]
                                    unit = raw_data[14]

                                    if raw_data[15] == '*PASS*':
                                        self.meas_fail_code = '0'
                                    elif raw_data[15] == '':
                                        continue
                                    else:
                                        self.meas_fail_code = '1'

                                    if name == 'T1':
                                        name = name + '_' + str(name_a)
                                        name_a += 1

                                    if name == 'XT801M':
                                        name = name + '_' + str(name_b)
                                        name_b += 1

                                    if name == 'XT1M':
                                        name = name + '_' + str(name_c)
                                        name_c += 1

                                    if name == 'DB101':
                                        name = name + '_' + str(name_d)
                                        name_d += 1

                                    if 'IC' in name:
                                        name = name + '_' + str(name_e)
                                        name_e += 1

                                    if name == name_prev:
                                        name += '_1'

                                    if str(raw_data[13]) == '':
                                        value = '0'

                                    if '%' in raw_data[10]:
                                        h_limit = int(value.split('.')[0]) + (int(value.split('.')[0]) / 100 *
                                                                              int(raw_data[9].split('.')[0]))
                                    else:
                                        h_limit = raw_data[9]

                                    if '%' in raw_data[12]:
                                        l_limit = int(value.split('.')[0]) + (int(value.split('.')[0]) / 100 *
                                                                              int(raw_data[11].split('.')[0]))
                                    else:
                                        l_limit = raw_data[11]

                                    unit_format = (str(unit[:1]).replace('M', 'E+6').replace('G', 'E+9')
                                                   .replace('K', 'E+3').replace('m', 'E-3').replace('u', 'E-6')
                                                   .replace('n', 'E-9').replace('p', 'E-12'))

                                    if 'o' in unit[-1:]:
                                        unit = 'Ohm'
                                    elif 'F' in unit[-1:]:
                                        unit = 'F'
                                    elif 'V' in unit[-1:]:
                                        unit = 'V'
                                    elif 'A' in unit[-1:]:
                                        unit = 'A'
                                    else:
                                        unit = ''

                                    if len(unit_format) <= 1:
                                        unit_format = ''

                                    name_prev = name

                                    number_of_records += 1

                                    upload_values += (',"T",0,"' + self.meas_fail_code + '","' + str(unit) + unit_format
                                                      + '","' + str(name) + '","' + str(value) + '","' + str(l_limit)
                                                      + '","' + str(h_limit) + '",' + str(number_of_records))

                            upload_values = upload_values.replace(',', '', 1)

                            if self.use_itac:
                                Itac.upload(Itac(self.station_number, self.itac_restApi), self.process_layer,
                                            self.sn, self.itac_pos, self.test_result, '20', upload_values)
                            Seso.upload(Seso(self.station_number, self.seso_restApi),
                                        self.sn, self.itac_wa, self.status, self.itac_desc)

                            if self.use_seso is False:
                                if self.status == 'pass':
                                    library.shared_varriables.pass_count += 1
                                else:
                                    library.shared_varriables.fail_count += 1

                        if self.remove_file:
                            remove(self.split_path[0][:-8] + '\\PROBLEMS\\' + str(start_time) + self.split_path[1])

                    except ValueError:
                        try:
                            if 'max' in str(exc_info()):
                                self.tLock.release()
                                continue
                            else:
                                windll.user32.MessageBoxW(0, 'Error 0x101 ' + format_exc(), 'Error', 0x1000)
                                Logger.log_event(Logger(), 'Error 0x101. ' + format_exc())
                                self.tLock.release()
                                continue
                        except ValueError:
                            continue

                    except PermissionError:
                        try:
                            self.tLock.release()
                            continue
                        except ValueError:
                            continue

                    except UnboundLocalError:
                        try:
                            windll.user32.MessageBoxW(0, 'Error 0x103 ' + format_exc(), 'Error', 0x1000)
                            Logger.log_event(Logger(), 'Error 0x103. ' + format_exc())
                            self.tLock.release()
                            continue
                        except ValueError:
                            continue

                    except FileNotFoundError:
                        try:
                            self.tLock.release()
                            continue
                        except ValueError:
                            continue

                    except IndexError:
                        try:
                            windll.user32.MessageBoxW(0, 'Error 0x105 ' + format_exc(), 'Error', 0x1000)
                            Logger.log_event(Logger(), 'Error 0x105. ' + format_exc())
                            self.tLock.release()
                            continue
                        except ValueError:
                            continue

                    except (Exception, BaseException):
                        try:
                            windll.user32.MessageBoxW(0, 'Error 0x100 ' + str(exc_info()), 'Error', 0x1000)
                            Logger.log_event(Logger(), 'Error 0x100. ' + str(exc_info()))
                            self.tLock.release()
                            continue
                        except ValueError:
                            continue
            except FileNotFoundError:
                continue
        Itac.login(Itac(self.station_number, self.itac_restApi))

    def stdf_handle(self):
        while self.run:
            sleep(0.001)
            self.run = library.shared_varriables.run_thread
            if len(listdir(path=self.path)) > 1:
                try:
                    start_time = time()
                    ########################################################
                    self.tLock.acquire()
                    ########################################################
                    # Main function definition
                    ########################################################
                    comp = 0
                    start_array = {}
                    times = {}
                    name_prev = ''
                    count = 0
                    time_count = 0

                    oldest = min(iglob(self.path + '*.[TtLl][XxOo][TtGg]'), key=path.getctime)

                    with open(oldest, 'r') as file_opened:
                        data = file_opened.read(-1)
                        data = data.splitlines()
                        size = len(data)

                    if self.remove_file:
                        self.split_path = oldest.rsplit('\\', 1)
                        replace(oldest, self.split_path[0] + '\\PROBLEMS\\' + str(start_time) + self.split_path[1])
                    ########################################################
                    self.tLock.release()
                    ########################################################

                    for x in range(size):
                        if '@' in data[x]:
                            self.start_number = x
                            break

                    for x in range(size):
                        if any(['"' in data[x], '/' in data[x] and ('/P' not in data[x] and 'P/N' not in data[x]
                                                                    and '/S' not in data[x] and '/W' not in data[x])]):
                            start_array[count] = x + 1
                            count = count + 1

                    for i in range(count):
                        upload_values = ''
                        number_of_records = 0
                        contact_c = 0
                        if self.start_number > start_array[i]:
                            start_array[i] = len(data)

                        for x in range(self.start_number, start_array[i]):
                            if any(['<' in data[x], '>' in data[x]]):
                                self.test_result = '1'
                                self.status = 'fail'
                                break
                            else:
                                self.test_result = '0'
                                self.status = 'pass'

                        for x in range(self.start_number, start_array[i]):
                            if 'SN ' in data[x]:
                                self.sn = data[x].split(' ')
                                self.sn = self.sn[4]
                                if '_' not in self.sn:
                                    self.sn = self.sn + '_1'
                                    self.multi_panel = False
                                else:
                                    self.multi_panel = True
                                self.sn = self.sn.split('_')
                                self.pos = self.sn[1]
                                self.sn = self.sn[0]
                                break
                            elif 'SERIALNUMBER' in data[x]:
                                self.sn = data[x].split(' ')
                                self.sn = self.sn[1]
                                if '_' not in self.sn:
                                    self.sn = self.sn + '_1'
                                    self.multi_panel = False
                                else:
                                    self.multi_panel = True
                                self.sn = self.sn.split('_')
                                self.pos = self.sn[1]
                                self.sn = self.sn[0]
                                break
                            else:
                                self.sn = ''

                        if self.sn == '':
                            windll.user32.MessageBoxW(0, 'Error 0x106 DMX read error', 'Error', 0x1000)
                            if self.remove_file:
                                remove(self.split_path[0] + '\\PROBLEMS\\' + str(start_time) + self.split_path[1])
                            continue

                        if self.use_itac:
                            if Itac.sn_state(Itac(self.station_number, self.itac_restApi),
                                             self.sn) != '0' and Itac.sn_state(Itac(self.station_number,
                                                                                    self.itac_restApi),
                                                                               self.sn) != '212':
                                continue

                            itac_data = Itac.sn_info(Itac(self.station_number, self.itac_restApi), self.sn)
                            self.itac_wa = itac_data[2]
                            self.itac_desc = itac_data[1]
                            self.itac_pos = itac_data[3]

                            if any([self.itac_desc == 'M830', self.itac_desc == 'M830-001',
                                    self.itac_desc == 'M830-002', self.itac_desc == 'M830-003']):
                                if int(self.itac_pos) in range(0, 10):
                                    comp = 0
                                elif int(self.itac_pos) in range(10, 19):
                                    comp = 9
                                elif int(self.itac_pos) in range(19, 28):
                                    comp = 18
                                else:
                                    comp = 27

                            elif any([self.itac_desc == 'M951', self.itac_desc == 'M951-001', self.itac_desc == 'M952',
                                      self.itac_desc == 'M952-001', self.itac_desc == 'M953',
                                      self.itac_desc == 'M953-001']):
                                if int(self.itac_pos) in range(0, 18):
                                    comp = 0
                                else:
                                    comp = 18

                            elif any([self.itac_desc == 'M976-002-HAUPTPL.', self.itac_desc == 'M976-001-HAUPTPL.']):
                                if int(self.itac_pos) in range(0, 43):
                                    comp = 0
                                else:
                                    comp = 42

                            if len(self.sn) == 13:
                                self.sn = self.sn.strip('AP')
                                if self.multi_panel:
                                    self.sn = int(self.sn) - int(self.itac_pos) + comp + int(self.pos)
                                self.sn = str(self.sn)
                                self.sn = 'AP' + self.sn.zfill(11)

                            elif len(self.sn) == 26:
                                sn_rest = self.sn[-10:]
                                sn_num = self.sn[:16]
                                self.sn = int(sn_num) - int(self.itac_pos) + comp + int(self.pos)
                                self.sn = str(self.sn) + str(sn_rest)

                        for x in range(self.start_number, start_array[i]):
                            if match('.*-.*-.*:.*:.*', data[x]):
                                times[time_count] = data[x]
                                times[time_count] = times[time_count].split(' ')[2]
                                time_count = time_count + 1
                            if any(['<' in data[x], '=' in data[x], '>' in data[x], '**' in data[x], '~' in data[x]]):
                                name = split('[=<>]', data[x])
                                if '<' in data[x]:
                                    self.meas_fail_code = '1'
                                elif '>' in data[x]:
                                    self.meas_fail_code = '2'
                                elif '=' in data[x]:
                                    self.meas_fail_code = '0'
                                if 'ON MEASURED VALUE' in data[x]:
                                    continue
                                if 'CONTINUITY' in data[x]:
                                    name[0] = ('CONTINUITY_' + str(contact_c) + '='
                                               + data[x + 3].replace('TP', 'tp').split(' ')[2] + '( , )')
                                    name = name[0].split('=')
                                    contact_c += 1
                                    self.meas_fail_code = '1'
                                    self.test_result = '1'
                                    self.status = 'fail'
                                if 'OPEN PIN GROUPS' in data[x]:
                                    name[0] += '=' + data[x + 2]
                                    name[0] = (name[0].replace('**', '').replace('~', '')
                                               .replace('(', '').replace('(', '')
                                               .replace(',', ':').replace(')', '')
                                               .replace(' OPEN PIN GROUPS ', 'CONTACT_' + str(contact_c)))
                                    name = name[0].split('=')
                                    name[1] = name[1].replace(' ', ',', 1).replace(' ', '')
                                    name[1] = name[1] + '( , )'
                                    contact_c += 1
                                    self.meas_fail_code = '1'
                                    self.test_result = '1'
                                    self.status = 'fail'
                                if 'NAILS NOT MAKING CONTACT' in data[x]:
                                    name[0] += '=' + data[x + 3]
                                    name[0] = (name[0].replace('**', '').replace('(', '').replace('(', '')
                                               .replace(',', ':').replace(')', '').
                                               replace(' NAILS NOT MAKING CONTACT ', 'CONTACT_' + str(contact_c))
                                               + '( , )')
                                    name = name[0].split('=')
                                    contact_c += 1
                                    self.meas_fail_code = '1'
                                    self.test_result = '1'
                                    self.status = 'fail'
                                if 'Shorted Nails' in data[x]:
                                    name[0] += '=' + data[x + 1]
                                    name[0] = (name[0].replace('**', '').replace('~', '')
                                               .replace('(', '').replace('(', '')
                                               .replace(',', ':').replace(';', '')
                                               .replace(')', '').replace(' Shorted Nails ', 'SHORT' + str(contact_c))
                                               + '( , )')
                                    name = name[0].split('=')
                                    contact_c += 1
                                    self.meas_fail_code = '1'
                                    self.test_result = '1'
                                    self.status = 'fail'
                                if len(name) < 2:
                                    continue
                                if name[1] == '':
                                    name[1] = '  ( , )'
                                if name[0] == '':
                                    continue
                                if 'LIMITS' in name[0]:
                                    continue
                                if '(,)' in name[1]:
                                    continue
                                if self.multi_panel is True:
                                    name[0] = name[0].replace('-', '_').rsplit('_', 1)
                                    name[0] = name[0][0]
                                if 'P/N' in name[0]:
                                    continue
                                if name[0] == name_prev:
                                    name[0] += '_1'
                                if ' ' in name[0]:
                                    continue
                                name_prev = name[0]
                                value = name[1].split('(')
                                value[0] = (value[0].replace('MEG', 'E+6').replace('G', 'E+9').replace('K', 'E+3')
                                            .replace('M', 'E-3').replace('U', 'E-6').replace('N', 'E-9')
                                            .replace('P', 'E-12'))
                                l_limit = value[1].split(',')
                                l_limit[0] = (l_limit[0].replace('MEG', 'E+6').replace('G', 'E+9').replace('K', 'E+3')
                                              .replace('M', 'E-3').replace('U', 'E-6').replace('N', 'E-9')
                                              .replace('P', 'E-12'))
                                h_limit = l_limit[1].split(')')
                                h_limit[0] = (h_limit[0].replace('MEG', 'E+6').replace('G', 'E+9').replace('K', 'E+3')
                                              .replace('M', 'E-3').replace('U', 'E-6').replace('N', 'E-9')
                                              .replace('P', 'E-12'))
                                if 'R' in h_limit[1]:
                                    unit = 'Ohm'
                                elif 'C' in h_limit[1]:
                                    unit = 'F'
                                elif 'V' in h_limit[1]:
                                    unit = 'V'
                                elif 'A' in h_limit[1]:
                                    unit = 'A'
                                else:
                                    unit = ''
                                number_of_records += 1
                                upload_values += (',"T",0,"' + self.meas_fail_code + '","' + unit + '","' + name[0]
                                                  + '","' + value[0] + '","' + l_limit[0] + '","' + h_limit[0] + '",'
                                                  + str(number_of_records))

                        upload_values = upload_values.replace(',', '', 1)
                        self.start_number = start_array[i]
                        cycle_time = (datetime.strptime(times[1], '%H:%M:%S')
                                      - datetime.strptime(times[0], '%H:%M:%S'))
                        cycle_time = str(cycle_time.total_seconds())

                        if self.use_itac:
                            Itac.upload(Itac(self.station_number, self.itac_restApi), self.process_layer,
                                        self.sn, self.itac_pos, self.test_result, cycle_time, upload_values)
                        Seso.upload(Seso(self.station_number, self.seso_restApi),
                                    self.sn, self.itac_wa, self.status, self.itac_desc)

                    # End of main function definition
                    ########################################################
                        if self.use_seso is False:
                            if self.status == 'pass':
                                library.shared_varriables.pass_count += 1
                            else:
                                library.shared_varriables.fail_count += 1

                    if self.remove_file:
                        remove(self.split_path[0] + '\\PROBLEMS\\' + str(start_time) + self.split_path[1])

                except ValueError:
                    try:
                        if 'max' in str(exc_info()):
                            self.tLock.release()
                            continue
                        else:
                            windll.user32.MessageBoxW(0, 'Error 0x101 ' + format_exc(), 'Error', 0x1000)
                            Logger.log_event(Logger(), 'Error 0x101. ' + format_exc())
                            self.tLock.release()
                            continue
                    except ValueError:
                        continue

                except PermissionError:
                    try:
                        self.tLock.release()
                        continue
                    except ValueError:
                        continue

                except UnboundLocalError:
                    try:
                        windll.user32.MessageBoxW(0, 'Error 0x103 ' + format_exc(), 'Error', 0x1000)
                        Logger.log_event(Logger(), 'Error 0x103. ' + format_exc())
                        self.tLock.release()
                        continue
                    except ValueError:
                        continue

                except FileNotFoundError:
                    try:
                        self.tLock.release()
                        continue
                    except ValueError:
                        continue

                except IndexError:
                    try:
                        windll.user32.MessageBoxW(0, 'Error 0x105 ' + format_exc(), 'Error', 0x1000)
                        Logger.log_event(Logger(), 'Error 0x105. ' + format_exc())
                        self.tLock.release()
                        continue
                    except ValueError:
                        continue

                except (Exception, BaseException):
                    try:
                        windll.user32.MessageBoxW(0, 'Error 0x100 ' + format_exc(), 'Error', 0x1000)
                        Logger.log_event(Logger(), 'Error 0x100. ' + format_exc())
                        self.tLock.release()
                        continue
                    except ValueError:
                        continue
        Itac.login(Itac(self.station_number, self.itac_restApi))

    def main(self):
        if self.what_to_handle == 'stdf':
            Parser.stdf_handle(self)
        elif self.what_to_handle == 'rexxam':
            Parser.rexxam_handle(self)
