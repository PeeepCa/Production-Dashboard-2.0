import itac_library as ITAC

sessionId, persId, locale = ITAC.itac.login(ITAC.itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'))
ITAC.itac.sninfo(ITAC.itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'), sessionId, persId, locale, '#L003095410#AA#1001230133#06#1001244085#07#240320#03625A')
ITAC.itac.logout(ITAC.itac('40010011', 'http://acz-itac/mes/imsapi/rest/actions/'), sessionId, persId, locale)