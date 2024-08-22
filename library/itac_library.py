# ITAC library
# input for self class ITAC should be station number and restAPI address
# restAPI=http://acz-itac/mes/imsapi/rest/actions/

from requests import post
from ctypes import windll
from json import loads

from library.logger_library import Logger


class Itac:
    """
    Itac library, communication via rest.
    :param station_number: station_number from iTAC
    :param restapi: restapi address
    """
    def __init__(self, station_number, restapi):
        # init for all components needed for library to work
        self.login = 'regLogin'
        self.sn_info = 'trGetSerialNumberInfo'
        self.sn_state = 'trCheckSerialNumberState'
        self.upload = 'trUploadResultDataAndRecipe'
        self.get_result_data = 'trGetResultDataForSerialNumber'
        self.logout = 'regLogout'
        self.headers = {'content-type': 'application/json'}
        self.timeout = 5
        self.stationNumber = station_number
        self.restAPI = restapi
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
        js = loads(Itac.data_post(self, self.login, body))
        globals()['sessionId'] = str(js['result']['sessionContext']['sessionId'])
        globals()['persId'] = str(js['result']['sessionContext']['persId'])
        globals()['locale'] = str(js['result']['sessionContext']['locale'])

    def sn_info(self, sn):
        """
        SN info
        :param sn: serial number
        :return: part_no, part_dest, wa, sn_pos
        """
        # serial number information
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "serialNumberResultKeys": ["PART_NUMBER","PART_DESC","WORKORDER_NUMBER","SERIAL_NUMBER_POS"]}"""
        data = loads(Itac.data_post(self, self.sn_info, body))['result']['serialNumberResultValues']
        return data[0], data[1], data[2], data[3]

    def sn_state(self, sn):
        """
        Interlocking
        :param sn: serial number
        :return: status
        """
        # Interlocking
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
        status = str(loads(Itac.data_post(self, self.sn_state, body))['result']['serialNumberStateResultValues'][0])
        if status != '0' and status != '212':
            windll.user32.MessageBoxW(0, 'iTAC AOI ' + str(status), 'iTAC Message', 0x1000)
        return status

    def upload(self, process_layer, sn, sn_pos, test_result, cycle_time, upload_values):
        """
        Upload of the results
        :param sn: serial number
        :param process_layer: process layer
        :param sn_pos: serial number position
        :param test_result: test result
        :param cycle_time: cycle time
        :param upload_values: upload values
        """
        # Upload state and result
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

    def get_result_data(self, sn):
        """
        Get result data
        :param sn: serial number
        :return: measured_value
        """
        # Get results data
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "processLayer":"1",
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "type":"-1",
                    "name":"-1",
                    "allProductEntries":"0",
                    "onlyLastEntry":"0",
                    "resultDataKeys": ["MEASURE_VALUE"]}"""
        print(body)
        return loads(Itac.data_post(self, self.get_result_data, body))

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
    def data_post(self, function, body):
        """
        Send data to server
        :param function: function
        :param body: body
        :return: 'req.text'
        """
        # Function for sent data to restAPI
        req = post(self.restAPI + function, headers=self.headers, data=body, timeout=self.timeout)
        if req.status_code != 200:
            windll.user32.MessageBoxW(0, 'Error 0x300 iTAC' + str(self.function) + 'problem ' +
                                      str(req.status_code), 'iTAC Message', 0x1000)
            Logger.log_event(Logger(), 'Error 0x305 iTAC' + str(self.function) + 'problem ' + str(req.status_code))
        return req.text
