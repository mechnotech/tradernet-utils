# Tradernet API utils

Набор утилит для API TraderNet.ru

Для старта с нуля:
* Созадть окружение venv (`python3 -m venv venv && source venv/bin/activated`)
* Установить библиотеки pip из requirements.txt (`pip install -r requirements.txt`)
* создать .env файл с персональными настройками по шаблону .env.example



#### ТОП-10 самых торгуемых акций России
get_top() 

#### Получить один тикер

get_ticker('SBER')

#### Получить котировки по нескольким тикерам (через GET)
    
get_tickers(list)

#### Исторические данные: свечи, объемы, по тикерам

get_history(tickers, time_frame, data_from, data_to)

*присылает данные за неделю, даже если выбрать один день 

----
Использует PublicApiClient от Mr. TradeBot & Robotrader Jr

Подробное описание API - https://tradernet.ru/tradernet-api/public-api-client

