from library.itac_library import itac
from library.seso_library import seso
from ui import UI

# sessionId, persId, locale = itac.login(itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'))
# itac.login(itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'))
# data = itac.sn_info(itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'), '#L003095410#AA#1001230133#06#1001244085#07#240320#03625A')
# itac.logout(itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'))
# print(data)

# data = seso.updateProdData(seso('40010021', 'https://seso.apag-elektronik.com/api/prod/'), 98, 90)
# print(data)
# data = seso.operatorWithoutReader(seso('40010021', 'https://seso.apag-elektronik.com/api/'))
# print(data)

UI.main(UI())