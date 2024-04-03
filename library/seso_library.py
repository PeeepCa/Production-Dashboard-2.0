# SESO library
# input for self class SESO should be station number and restAPI adress
# sesoData=https://seso.apag-elektronik.com/api/prod/
# sesoOperator=https://seso.apag-elektronik.com/api/

import requests

class seso:
    def __init__(self, *args):
        self.stationNumber = args[0]
        self.restAPI = args[1]
        self.tmout = 5

    def upload(self, *args):
        # Uploading the results to SESO
        serialNumber = args[0]
        workOrder = args[1]
        status = args[2]
        description = args[3]
        workOrder = workOrder.strip(' ')
        if workOrder != 'locale':
            if status == 'fail':
                status = '0'
            else:
                status = '1'
            payload = {'type': 'production', 'itac': '0', 'station': self.stationNumber, 'wa': workOrder, 'module': description, 'ap': serialNumber, 'result': status}
            req = requests.post(self.restAPI, data = payload, timeout = self.tmout)

    def operatorWithoutReader(self):
        # Function which returns the card number and operator name for tester without reader
        # If its secondary machine, then it doenst want trainings
        payload = {'type': 'station-info', 'station': self.stationNumber}
        req = requests.post(self.restAPI, data = payload, timeout = self.tmout)
        op_id = req.text.split(',')[5].split(':')[1].split('-')[0].replace('"','')
        op_name = req.text.split(',')[4].split(':')[1].split('-')[0].replace('"','')
        if list(op_id)[0] == '0':
            op_id = op_id[-3:]
        if len(op_id) > 1:
            training = 'Secondary'
            unlock = True
        else:
            training = 'Secondary'
            unlock = False

        return op_id, op_name, training, unlock
    
    def operatorWithReader(self, *args):
        # This function checks the trainings for primary machine and returns back operator name and id
        cardReader = args[0]
        useTraining = args[1]
        payload = {'type': 'card', 'id': cardReader, 'station': self.stationNumber}
        req = requests.post(self.restAPI, data = payload, timeout = self.tmout)
        data = (req.text).split(',')
        op_id = data[2].split(':')[1].replace('"','')
        op_name = data[1].split(':')[1].replace('"','') + ' ' + data[0].split(':')[2].replace('"','')
        data = (req.text).split('[')[1].replace('[','').replace(']','').replace('{','').replace('}','').replace('"','').split(',')
        # This ll be obsolite after the DMS ll work correctly
        if list(op_id)[0] == '0':
            op_id = op_id[-3:]
        if useTraining == True:
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
    
    def loginLogout(self, *args):
        # Login / Logout for operator
        op_name = args[0]
        op_id = args[1]
        inOut = args[2]
        payload = {'type': 'operator', 'station': self.stationNumber, 'perName': op_name, 'perNr': op_id, 'action': inOut}
        req = requests.post(self.restAPI, data = payload, timeout = self.tmout)
        if inOut == 'IN':
            logged = True
        else:
            logged = False

        return logged
    
    def updateProdData(self, *args):
        # Production data display
        # There ll be probably changes since we dont need to calculate everything here
        # Time ll show
        greenFPY = args[0]
        orangeFPY = args[1]
        payload = {'action': 'hourly', 'station': self.stationNumber}
        data = requests.post(self.restAPI, data = payload, timeout = self.tmout).text.split(',')
        working = int(data[3].split(':')[1]) + int(data[4].split(':')[1])
        testerType = data[0].split(':')[1].replace('"','')
        if 'ICT' in testerType:
            instructionList = [*range(60,64,1)]
        else:
            instructionList = {*range(65,69,1)}
        if working == 0:
            pass_count = 0
            fail_count = 0
            fpy = 0
            fpy_color = '#ff8787'
            module = ''
            lrf = 0
            lrf_color = '#ff8787'
            curr_perf = 0
        else:
            pass_count = int(float(data[3].split(':')[1]))
            fail_count = int(float(data[4].split(':')[1]))
            module = data[2].split(':')[1].replace('"','')
            if '[]' not in data[9]:
                try:
                    fpy = int(float(data[9].split(':')[1]))
                    lrf = int(float(data[10].split(':')[1].replace('"','')))
                except:
                    fpy = 0
                    lrf = 1
            else:
                fpy = 0
                lrf = 1
            if fpy > 0:
                curr_perf = int(float(data[14].split(':')[1].replace('"','').replace('}','').replace(']','')))
            else:
                curr_perf = 0
            lrf_perc = lrf/100 * curr_perf
            if fpy >= greenFPY:
                fpy_color = '#539955'
            elif fpy >= orangeFPY:
                fpy_color = '#997753'
            else:
                fpy_color = '#995353'
            if lrf_perc < 80:
                lrf_color = '#995353'
            elif lrf_perc < 100:
                lrf_color = '#997753'
            else:
                lrf_color = '#539955'

        return pass_count, fail_count, fpy, fpy_color, instructionList, module, lrf, lrf_color, curr_perf