"""#############################################################
   #         PublicApi-клиент TraderNet для Python 3. V 0.1.3  #
   #############################################################"""

import hashlib
import hmac
import json
import requests
import time
import urllib3


class PublicApiClient:
    """
    Имена приватных переменных класса должны начинаться
     на два подчеркивания: __
    """
    V1: int = 1
    V2: int = 2
    __apiUrl = str()
    __apiKey = str()
    __apiSecret = str()
    __version = int()
    __devMode: bool = False

    def __init__(self, apiKey=None, apiSecret=None, version=V1):
        """
        Инициализация экземпляра класса
        :param apiKey:
        :param apiSecret:
        :param version:
        """
        self.__apiUrl = 'https://tradernet.ru/api'
        self.__version = version
        self.__apiKey = apiKey
        self.__apiSecret = apiSecret

    def setApiUrl(self, _apiUrl):
        """
        подгружаем нужный URL, если не устраивает дефолтный
        :param _apiUrl:
        :return:
        """
        self.__apiUrl = _apiUrl

    def isDevMode(self):
        """
        Включаем режим разработки
        :return:
        """
        self.__devMode = True

    def preSign(self, d):
        """
        preSign используется для подписи с ключом
        :param d:
        :return: string
        """

        s = ''
        for i in sorted(d):
            if type(d[i]) == dict:
                s += i + '=' + self.preSign(d[i]) + '&'
            else:
                s += i + '=' + str(d[i]) + '&'
        return s[:-1]

    def httpencode(self, d):
        """
        httpencode - аналог функции http_build_query для URL-запроса,
        обновленный , с работой с вложенными списками
        :param d:
        :return: string
        """

        def _dict_flatter(exkey, d, exval=None):
            sub = ''
            for key, value in d.items():
                if isinstance(value, dict):
                    return sub + _dict_flatter(exkey, value, key)
                x = f'[{exval}]' if exval else ''
                sub += f'{exval}{x}[{key}]={value}&'
            return sub

        s = ''
        for k, v in sorted(d.items()):
            if isinstance(v, dict):
                return s + f'{_dict_flatter(k, v)}'
            else:
                s += f'{k}={str(v)}&'

        return s[:-1]

    def sendRequest(self, method, aParams=None, format='JSON'):
        """
        Отправка запроса
        :param method:
        :param aParams:
        :param format:
        :return: Responce
        """

        aReq = dict()
        aReq['cmd'] = method
        if aParams:
            aReq['params'] = aParams
        if (self.__version != self.V1) and (self.__apiKey):
            aReq['apiKey'] = self.__apiKey
        aReq['nonce'] = int(time.time() * 10000)

        preSig = self.preSign(aReq)
        Presig_Enc = self.httpencode(aReq)

        # Игнорим ошибки для локального соединения по ssl
        isVerify = True

        if self.__devMode:
            urllib3.disable_warnings()
            isVerify = False

        # Создание подписи и выполнение запроса в зависимости от V1 или V2
        if self.__version == self.V1:

            aReq['sig'] = hmac.new(
                key=self.__apiSecret.encode(),
                digestmod='SHA256'
            ).hexdigest()

            res = requests.post(self.__apiUrl, data={'q': json.dumps(aReq)},
                                verify=isVerify)
        else:
            apiheaders = {
                'X-NtApi-Sig': hmac.new(key=self.__apiSecret.encode(),
                                        msg=preSig.encode('utf-8'),
                                        digestmod=hashlib.sha256).hexdigest(),
                'Content-Type': 'application/x-www-form-urlencoded'
                # Нужно в явном виде указать Content-Type,
                # иначе не будет работать;
                # по какой-то причине requests.post не может сам это сделать
            }
            self.__apiUrl += '/v2/cmd/' + method
            res = requests.post(self.__apiUrl, params=Presig_Enc,
                                headers=apiheaders, data=Presig_Enc,
                                verify=isVerify)

        return res
