# ITAC library
# input for self class ITAC should be station number and restAPI adress

import requests
import ctypes

class itac:
    def __init__(self, *args):
        # init for all components needed for lbrary to work
        self.login = 'regLogin'
        self.sninfo = 'trGetSerialNumberInfo'
        self.snstate = 'trCheckSerialNumberState'
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
        req = requests.post(self.restAPI + self.login, headers = self.headers, data=body, timeout = self.tmout)

        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x301 iTAC regLogin problem ' + str(req.status_code), 'iTAC Message', 0x1000)

        js = (req.text).replace(' ','').replace('\r\n','').replace('{"result":{"return_value":0','').split(',')
        sessionId = js[1].replace('sessionContext":{','').split(':')[1]

        persId = js[2].split(':')[1]

        locale = js[3].replace('}}}','').replace('"','').split(':')[1]

        return sessionId, persId, locale

    def sninfo(self, *args):
        # SN information
        # Part number, parts desc, work order and SN pos
        sessionId = args[0]
        persId = args[1]
        locale = args[2]
        sn = args[3]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """},
                    "stationNumber":""" + self.stationNumber + """,
                    "serialNumber":""" + '"' + sn + '"' + """,
                    "serialNumberPos":"-1",
                    "serialNumberResultKeys": ["PART_NUMBER","PART_DESC","WORKORDER_NUMBER","SERIAL_NUMBER_POS"]}"""
        req = requests.post(self.restAPI + self.sninfo, headers = self.headers, data=body, timeout = self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x302 iTAC trGetSerialNumberInfo problem ' + str(req.status_code), 'iTAC Message', 0x1000)

        data = req.text.replace(' ','').replace('\r\n','').replace('"','').split(',')
        ITAC_part_no = str(data[1]).split('[')[1]
        ITAC_part_desc = str(data[2])
        ITAC_WA = str(data[3])
        ITAC_sn_pos = str(data[4].split(']')[0])

        return ITAC_part_no, ITAC_part_desc, ITAC_WA, ITAC_sn_pos

    # def check1(sn):
    #     body = """{"sessionContext":
    #                 {"sessionId":""" + sessionId + """,
    #                 "persId":""" + '"' + persId + '"' + """,
    #                 "locale":""" + '"' + locale + '"' + """},
    #                 "stationNumber":""" + stationNumber + """,
    #                 "processLayer":"-1",
    #                 "checkMultiBoard":"0",
    #                 "serialNumber":""" + '"' + sn + '"' + """,
    #                 "serialNumberPos":"-1",
    #                 "serialNumberStateResultKeys": ["ERROR_CODE"]}"""
    #     req = requests.post(restAPI + check1, headers=headers, data=body, timeout=tmout)
    #     if req.status_code != 200:
    #         ctypes.windll.user32.MessageBoxW(0, 'Error 0x303 iTAC trCheckSerialNumberState problem ' + str(req.status_code), 'iTAC Message', 0x1000)
    #     status = req.text.replace(' ','').replace('\r\n','').split(',')[1]
    #     status = status.replace('"','').replace('}','').replace('[','').replace(']','').split(':')[1]
    #     if status != '0' and status != '212':
    #         ctypes.windll.user32.MessageBoxW(0, 'iTAC AOI ' + status, 'iTAC Message', 0x1000)

    #     return status

    # def upload(stationNumber, sn, itac_pos, testresult, cycle_time, uploadvalues):
    #     body = """{"sessionContext":
    #                 {"sessionId":""" + sessionId + """,
    #                 "persId":""" + '"' + persId + '"' + """,
    #                 "locale":""" + '"' + locale + '"' + """},
    #                 "stationNumber":""" + stationNumber + """,
    #                 "processLayer":0,
    #                 "recipeVersionId":-1,
    #                 "serialNumberRef":""" + '"' + sn + '"' + """,
    #                 "serialNumberRefPos":""" + '"' + itac_pos + '"' + """,
    #                 "serialNumberState":""" + testresult + """,
    #                 "duplicateSerialNumber":0,
    #                 "bookDate":-1,
    #                 "cycleTime":""" + cycle_time + """,
    #                 "recipeVersionMode":0,
    #                 "resultUploadKeys": ["MEASURE_TYPE","ERROR_CODE","MEASURE_FAIL_CODE","UNIT","MEASURE_NAME","MEASURE_VALUE","LOWER_LIMIT","UPPER_LIMIT","TEST_STEP_NUMBER"],
    #                 "resultUploadValues": [""" + uploadvalues + """]}"""
    #     req = requests.post(restAPI + upload, headers=headers, data=body, timeout=tmout)
    #     if req.status_code != 200:
    #         ctypes.windll.user32.MessageBoxW(0, 'Error 0x304 iTAC trUploadResultDataAndRecipe problem ' + str(req.status_code), 'iTAC Message', 0x1000)

    def logout(self, *args):
        # Logout
        sessionId = args[0]
        persId = args[1]
        locale = args[2]
        body = """{"sessionContext":
                    {"sessionId":""" + sessionId + """,
                    "persId":""" + '"' + persId + '"' + """,
                    "locale":""" + '"' + locale + '"' + """}}"""
        req = requests.post(self.restAPI + self.logout, headers=self.headers, data=body, timeout=self.tmout)
        if req.status_code != 200:
            ctypes.windll.user32.MessageBoxW(0, 'Error 0x305 iTAC regLogout problem ' + str(req.status_code), 'iTAC Message', 0x1000)