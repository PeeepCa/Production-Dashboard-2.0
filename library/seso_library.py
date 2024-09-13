# SESO library
# input for self class SESO should be station number and restAPI address
# sesoData=https://seso.apag-elektronik.com/api/prod/
# sesoOperator=https://seso.apag-elektronik.com/api/

from ctypes import windll
from requests import post, exceptions
from library.logger_library import Logger


class Seso:
    """
    Communication with SESO via restAPI. Second parameter is restAPI address.
    upload,
    operator_without_reader,
    operator_with_reader
    login_logout,
    update_prod_data
    :param args: station_number, rest_api
    """
    def __init__(self, *args):
        self.station_number = args[0]
        self.rest_api = args[1]
        self.timeout = 5

    def upload(self, *args):
        """
        Upload results to SESO.
        :param args: serial_number, work_order, status, description
        :return:
        """
        try:
            # Uploading the results to SESO
            serial_number = args[0]
            work_order = args[1]
            status = args[2]
            description = args[3]
            work_order = work_order.strip(' ')
            if work_order != 'locale':
                if status == 'fail':
                    status = '0'
                else:
                    status = '1'
                payload = {'type': 'production', 'itac': '0', 'station': self.station_number, 'wa': work_order,
                           'module': description, 'ap': serial_number, 'result': status}
                post(self.rest_api, data=payload, timeout=self.timeout, verify=False)
        except exceptions.MissingSchema:
            Logger.log_event(Logger(), 'Wrong URL at upload.')
            windll.user32.MessageBoxW(0, 'Error 0x401 URL for upload.', 'SESO Message', 0x1000)

    def operator_without_reader(self):
        """
        Operator info based on station number.
        :return: op_id, op_name, unlock, training
        """
        try:
            # Function which returns the card number and operator name for tester without reader
            # If its secondary machine, then it does not want trainings
            payload = {'type': 'station-info', 'station': self.station_number}
            req = post(self.rest_api, data=payload, timeout=self.timeout, verify=False)
            op_id = req.text.split(',')[5].split(':')[1].split('-')[0].replace('"', '')
            op_name = req.text.split(',')[4].split(':')[1].split('-')[0].replace('"', '')
            if list(op_id)[0] == '0':
                op_id = op_id[-3:]
            if len(op_id) > 1:
                training = 'Secondary'
                unlock = True
            else:
                training = 'Secondary'
                unlock = False
            return op_id, op_name, unlock, training
        except exceptions.MissingSchema:
            Logger.log_event(Logger(), 'Wrong URL at operatorWithoutReader.')
            windll.user32.MessageBoxW(0, 'Error 0x402 URL for operatorWithoutReader.', 'SESO Message', 0x1000)
    
    def operator_with_reader(self, *args):
        """
        Operator info based on card number.
        :param args: card_id, use_training
        :return: op_id, op_name, unlock, training
        """
        try:
            # This function checks the trainings for primary machine and returns back operator name and id
            # sesoOperator
            card_id = args[0]
            use_training = args[1]
            payload = {'type': 'card', 'id': card_id, 'station': self.station_number}
            req = post(self.rest_api, data=payload, timeout=self.timeout, verify=False)
            data = req.text.split(',')
            op_id = data[2].split(':')[1].replace('"', '')
            op_name = data[1].split(':')[1].replace('"', '') + ' ' + data[0].split(':')[2].replace('"', '')
            data = (req.text.split('[')[1].replace('[', '').replace(']', '')
                    .replace('{', '').replace('}', '').replace('"', '').split(','))
            # This ll be obsolete after the DMS ll work correctly
            if list(op_id)[0] == '0':
                op_id = op_id[-3:]
            if use_training is True:
                if len(data) > 1:
                    training = 'Training OK'
                    unlock = True
                else:
                    training = 'Training NOK'
                    unlock = False
            else:
                training = 'Turned OFF'
                unlock = True
            return op_id, op_name, unlock, training
        except exceptions.MissingSchema:
            Logger.log_event(Logger(), 'Wrong URL at operatorWithReader.')
            windll.user32.MessageBoxW(0, 'Error 0x403 URL for operatorWithReader.', 'SESO Message', 0x1000)
        except IndexError:
            return '0', '0', False, ''

    def login_logout(self, *args):
        """
        Login / Logout for operator.
        :param args: op_name, op_id, in_out
        :return: logged
        """
        try:
            # Login / Logout for operator
            op_name = args[0]
            op_id = args[1]
            in_out = args[2]
            payload = {'type': 'operator', 'station': self.station_number, 'perName': op_name, 'perNr': op_id,
                       'action': in_out}
            post(self.rest_api, data=payload, timeout=self.timeout, verify=False)
            if in_out == 'IN':
                logged = True
            else:
                logged = False
            return logged
        except exceptions.MissingSchema:
            Logger.log_event(Logger(), 'Wrong URL at loginLogout.')
            windll.user32.MessageBoxW(0, 'Error 0x404 URL for loginLogout.', 'SESO Message', 0x1000)
    
    def update_prod_data(self):
        """
        Performance info from SESO based on station number.
        :return: pass_count, fail_count, fpy, instruction_list, module, lrf, curr_perf
        """
        try:
            # Production data display
            # There ll be probably changes since we do not need to calculate everything here
            # Time ll show
            # sesoData
            payload = {'action': 'hourly', 'station': self.station_number}
            data = post(self.rest_api, data=payload, timeout=self.timeout, verify=False).text.split(',')
            working = int(data[3].split(':')[1]) + int(data[4].split(':')[1])
            tester_type = data[0].split(':')[1].replace('"', '')
            if 'ICT' in tester_type:
                instruction_list = [*range(60, 64, 1)]
            else:
                instruction_list = {*range(65, 69, 1)}
            if working == 0:
                pass_count = 0
                fail_count = 0
                fpy = 0
                module = ''
                lrf = 0
                curr_perf = 0
            else:
                pass_count = int(float(data[3].split(':')[1]))
                fail_count = int(float(data[4].split(':')[1]))
                module = data[2].split(':')[1].replace('"', '')
                if '[]' not in data[9]:
                    try:
                        fpy = int(float(data[9].split(':')[1]))
                        lrf = int(float(data[10].split(':')[1].replace('"', '')))
                    except IndexError:
                        fpy = 0
                        lrf = 0
                else:
                    fpy = 0
                    lrf = 0
                if fpy > 0 and len(data) == 15:
                    curr_perf = int(float(data[14].split(':')[1].replace('"', '').replace('}', '').replace(']', '')))
                else:
                    curr_perf = 0
            return pass_count, fail_count, fpy, instruction_list, module, lrf, curr_perf
        except exceptions.MissingSchema:
            Logger.log_event(Logger(), 'Wrong URL at updateProdData.')
            windll.user32.MessageBoxW(0, 'Error 0x405 URL for updateProdData.', 'SESO Message', 0x1000)
