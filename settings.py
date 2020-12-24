import multiprocessing as mp

TOP_IDS = ['GAZP', 'SBER', 'AFKS', 'AFLT', 'MAIL', 'ALRS', 'LKOH',
           'TATN', 'MAGN']
# c     название тикера
# bap   лучшее предложение
# bas	Количество (сайз) лучшего предложения
# baf	Объем лучшего предложения
# bbp	Лучший бид
# bbs	Количество (сайз) лучшего бида
# bbf	Объем лучшего бида
# ----
# min_step	Минимальный шаг цены
# step_price	Шаг цены
V_INFO = ['c', 'bap', 'bas', 'baf', 'bbp', 'bbs', 'bbf', 'min_step',
          'step_price']

# Использовать все ядра, достуные для машины
CPU_UNITS = mp.cpu_count()

# Пауза между запросми тикеров в сек
SLEEP_TIME = 0.1
# Пауза для остановки запросов в нерабочее временя (5 мин)
WAIT_TIME = 300


# Рабочие часы и дни на бирже (с 10 - 18) с Пн по Пт (1 - 5)
TRADE_START_HOUR = 10
TRADE_STOP_HOUR = 18
TRADING_DAYS = range(1, 5)
# Тариф брокера - комиссия с одной сделки
TARIF = 0.02
# Каким процентом от депо по бумаге можно рискнуть
RISK_PCN = 15
# Сколько рублей выделено на одну акцию
STAKE_PER_PAPER = 100000
# Процент профита для расчетов лучшей позиции
MY_PCN_START = 0.1
MY_PCN_MAX = 3
MY_PCN_STEP = 0.01


# Часы для старта орбаботки данных, архивации и удаления сырых файлов за день
CALC_START = 19
CALC_STOP = 20
# Пауза после обработки данных (1 час)
CALC_HOLD_TIME = 300 * 2


# Размер блока данных для записи в файл по тикеру
CHUNK_SIZE = 60
