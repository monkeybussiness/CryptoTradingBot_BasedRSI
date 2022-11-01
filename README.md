# CryptoTradingBot_BasedRSI
 
 Данный бот основан на RSI индикаторе. 
 
 Суть проста. С помощью API ключа Binance бот получает данные в виде словаря. Из этих данных он создает локальный CSV файл, с которым в дальнейшем работает. 
 Добавляет RSI индикатор и сравнивает этот показатель с торговой системой. Если условия подходят, то открывает сделку. Проверка сделки происходит через флаг.
 
 Так же  есть файл который проверяет на исторических данных прибыльность стратегии. 
 
 TODO:
 1.Добавить больше индикаторов. 
 2.Зоздать базу данных с обработанными данными по стратегии, для более быстрого сравнения торговых систем.
 3.Добавить получение данных через вебсокет.
 4.Обработать ошибку при отсоединения интернета. Чтобы бот запоминал, что он открыл сделку и перезапускался. (Сейчас если бот упадет, он не знает что он открыавал сделку и открывает новую)
