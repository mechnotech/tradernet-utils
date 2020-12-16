import os
import time

import PublicApiClient as NtApi
from dotenv import load_dotenv

load_dotenv()

pub_ = os.getenv('TN_PUB_KEY')
sec_ = os.getenv('TN_PRIVATE_KEY')

res = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V2)


def get_ticker(ticker, sup=False):
    cmd_ = 'getSecurityInfo'
    param_ = {
        'ticker': ticker,
        'sup': sup
    }
    res = NtApi.PublicApiClient(pub_, sec_, NtApi.PublicApiClient().V1)
    return res.sendRequest(cmd_, param_).content.decode("utf-8")


if __name__ == '__main__':
        print(get_ticker('SBER'))
        time.sleep(0.5)
