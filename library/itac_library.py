# ITAC library
# input for self class ITAC should be station number and restAPI address
# restAPI=http://acz-itac/mes/imsapi/rest/actions/

from requests import post
from ctypes import windll
from library.logger_library import Logger


class Itac:
    """
    Itac library, communication via rest.
    login,
    sn_info,
    sn_state,
    upload,
    logout
    :param args: station_number, rest_address
    """
    def __init__(self, *args):
        # init for all components needed for library to work
        self.login = 'regLogin'
        self.sn_info = 'trGetSerialNumberInfo'
        self.sn_state = 'trCheckSerialNumberState'
        self.upload = 'trUploadResultDataAndRecipe'
        self.logout = 'regLogout'
        self.headers = {'content-type': 'application/json'}
        self.timeout = 5
        self.stationNumber = args[0]
        self.restAPI = args[1]
        self.function = None
        self.body = None

    def login(self):
        """
        Login
        :return: sessionId, persId, locale as global vars
        """
        # Itac login
        body = """{"sessionValidationStruct":
                    {"stationNumber":""" + self.stationNumber + """,
                    "stationPassword":"",
                    "user":"",
                    "password":"",
                    "client":"01",
                    "registrationType":"S",
                    "systemIdentifier":"Test"}}"""
        js = (Itac.data_post(self, self.login, body).replace(' ', '').replace('\r\n', '')
              .replace('{"result":{"return_value":0', '').split(','))
        globals()['sessionId'] = js[1].replace('sessionContext":{', '').split(':')[1]
        globals()['persId'] = js[2].split(':')[1]
        globals()['locale'] = js[3].replace('}}}', '').replace('"', '').split(':')[1]

    def sn_info(self, *args):
        """
        SN info
        :param args: sn
        :return: part_no, part_dest, wa, sn_pos
        """
        # serial number information
        sn = args[0]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "serialNumberResultKeys": ["PART_NUMBER","PART_DESC","WORKORDER_NUMBER","SERIAL_NUMBER_POS"]}"""
        data = (Itac.data_post(self, self.sn_info, body).replace(' ', '')
                .replace('\r\n', '').replace('"', '').split(','))
        part_no = str(data[1]).split('[')[1]
        part_desc = str(data[2])
        wa = str(data[3])
        sn_pos = str(data[4].split(']')[0])
        return part_no, part_desc, wa, sn_pos

    def sn_state(self, *args):
        """
        Interlocking
        :param args: sn
        :return: status
        """
        # Interlocking
        sn = args[0]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "processLayer":"-1",
                    "checkMultiBoard":"0",
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "serialNumberStateResultKeys": ["ERROR_CODE"]}"""
        status = Itac.data_post(self, self.sn_state, body).replace(' ', '').replace('\r\n', '').split(',')[1]
        status = status.replace('"', '').replace('}', '').replace('[', '').replace(']', '').split(':')[1]
        if status != '0' and status != '212':
            windll.user32.MessageBoxW(0, 'iTAC AOI ' + status, 'iTAC Message', 0x1000)
        return status

    def upload(self, *args):
        """
        Upload of the results
        :param args: sn, sn_pos, test_result, cycle_time, upload_values
        """
        # Upload state and result
        process_layer = args[0]
        sn = args[1]
        sn_pos = args[2]
        test_result = args[3]
        cycle_time = args[4]
        upload_values = args[5]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "processLayer":""" + process_layer + """,
                    "recipeVersionId":-1,
                    "serialNumberRef":""" + '"' + sn + '"' + """,
                    "serialNumberRefPos":""" + '"' + sn_pos + '"' + """,
                    "serialNumberState":""" + test_result + """,
                    "duplicateSerialNumber":0,
                    "bookDate":-1,
                    "cycleTime":""" + cycle_time + """,
                    "recipeVersionMode":0,
                    "resultUploadKeys": ["MEASURE_TYPE","ERROR_CODE","MEASURE_FAIL_CODE","UNIT","MEASURE_NAME",
                    "MEASURE_VALUE","LOWER_LIMIT","UPPER_LIMIT","TEST_STEP_NUMBER"],
                    "resultUploadValues": [""" + upload_values + """]}"""
        Itac.data_post(self, self.upload, body)

    def logout(self):
        """
        Logout
        """
        # Logout
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """}}"""
        Itac.data_post(self, self.logout, body)

    # Modify sending all the iTAC through the single function
    def data_post(self, *args):
        """
        Send data to server
        :param args: function, body
        :return: 'req.text'
        """
        # Function for sent data to restAPI
        function = args[0]
        body = args[1]
        req = post(self.restAPI + function, headers=self.headers, data=body, timeout=self.timeout)
        if req.status_code != 200:
            windll.user32.MessageBoxW(0, 'Error 0x300 iTAC' + self.function + 'problem ' +
                                      str(req.status_code), 'iTAC Message', 0x1000)
            Logger.log_event(Logger(), 'Error 0x305 iTAC' + self.function + 'problem ' + str(req.status_code))
        return req.text
