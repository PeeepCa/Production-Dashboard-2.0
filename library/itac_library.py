# ITAC library
# input for self class ITAC should be station number and restAPI adress

from requests import post
import ctypes

class itac:
    def __init__(self, *args):
        # init for all components needed for lbrary to work
        self.login = 'regLogin'
        self.sn_info = 'trGetSerialNumberInfo'
        self.sn_state = 'trCheckSerialNumberState'
        self.upload = 'trUploadResultDataAndRecipe'
        self.logout = 'regLogout'
        self.headers = {'content-type': 'application/json'}
        self.tmout = 5
        self.stationNumber = args[0]
        self.restAPI = args[1]

    def login(self):
        # Login
        body = """{"sessionValidationStruct":
                    {"stationNumber":""" + self.stationNumber + """,
                    "stationPassword":"",
                    "user":"",
                    "password":"",
                    "client":"01",
                    "registrationType":"S",
                    "systemIdentifier":"Test"}}"""
        req = post(self.restAPI + self.login, headers = self.headers, data=body, timeout = self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x301 iTAC regLogin problem ' + str(req.status_code), 'iTAC Message', 0x1000)
        
        js = (req.text).replace(' ','').replace('\r\n','').replace('{"result":{"return_value":0','').split(',')
        globals()['sessionId'] = js[1].replace('sessionContext":{','').split(':')[1]
        globals()['persId'] = js[2].split(':')[1]
        globals()['locale'] = js[3].replace('}}}','').replace('"','').split(':')[1]

    def sn_info(self, *args):
        # SN information
        # Part number, parts desc, work order and SN pos
        sn = args[0]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "serialNumberResultKeys": ["PART_NUMBER","PART_DESC","WORKORDER_NUMBER","SERIAL_NUMBER_POS"]}"""
        req = post(self.restAPI + self.sn_info, headers = self.headers, data = body, timeout = self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x302 iTAC trGetSerialNumberInfo problem ' + str(req.status_code), 'iTAC Message', 0x1000)

        data = req.text.replace(' ','').replace('\r\n','').replace('"','').split(',')
        part_no = str(data[1]).split('[')[1]
        part_desc = str(data[2])
        wa = str(data[3])
        sn_pos = str(data[4].split(']')[0])
        return part_no, part_desc, wa, sn_pos

    def sn_state(self, *args):
        # SN information
        # Incerlocking
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
        req = post(self.restAPI + self.sn_state, headers = self.headers, data = body, timeout = self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x303 iTAC trCheckSerialNumberState problem ' + str(req.status_code), 'iTAC Message', 0x1000)
        
        status = req.text.replace(' ','').replace('\r\n','').split(',')[1]
        status = status.replace('"','').replace('}','').replace('[','').replace(']','').split(':')[1]
        if status != '0' and status != '212':
            ctypes.windll.user32.MessageBoxW(0, 'iTAC AOI ' + status, 'iTAC Message', 0x1000)
        return status

    def upload(self, *args):
        # Upload of SN result
        sn = args[0]
        sn_pos = args[1]
        test_result = args[2]
        cycle_time = args[3]
        upload_values = args[4]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "processLayer":0,
                    "recipeVersionId":-1,
                    "serialNumberRef":""" + '"' + sn + '"' + """,
                    "serialNumberRefPos":""" + '"' + sn_pos + '"' + """,
                    "serialNumberState":""" + test_result + """,
                    "duplicateSerialNumber":0,
                    "bookDate":-1,
                    "cycleTime":""" + cycle_time + """,
                    "recipeVersionMode":0,
                    "resultUploadKeys": ["MEASURE_TYPE","ERROR_CODE","MEASURE_FAIL_CODE","UNIT","MEASURE_NAME","MEASURE_VALUE","LOWER_LIMIT","UPPER_LIMIT","TEST_STEP_NUMBER"],
                    "resultUploadValues": [""" + upload_values + """]}"""
        req = post(self.restAPI + self.upload, headers = self.headers, data = body, timeout = self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x304 iTAC trUploadResultDataAndRecipe problem ' + str(req.status_code), 'iTAC Message', 0x1000)

    def logout(self):
        # Logout
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """}}"""
        req = post(self.restAPI + self.logout, headers=self.headers, data=body, timeout=self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x305 iTAC regLogout problem ' + str(req.status_code), 'iTAC Message', 0x1000)