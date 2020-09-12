

import datahandler_factory
import utility as util
import talib_indicators
import constants


# UTIL
import pandas as pd
from sklearn import preprocessing
import numpy as np


import numpy as np
from keras.models import load_model


history_points = 50


def csv_to_dataset(csv_path):
    # data = pd.read_csv(csv_path)

    start_date = "2020/08/01"
    end_date = "2020/08/30"
    data_handler = datahandler_factory.data_handler_factory().get_data_handler()
    utility = util.utility()
    start_date = utility.parse_date(start_date)
    end_date = utility.parse_date(end_date)
    tickers = data_handler.fetch_backtest_tickers(start_date, end_date)
    data  = pd.DataFrame(tickers["FXPRO:1109"])
    cols = data.columns.tolist()
    cols = [cols[4], cols[3], cols[1], cols[2], cols[0], cols[5]]
    # cols = [cols[4], cols[3], cols[1], cols[2], cols[0]]
    data = data[cols]
    data.columns = ['date', '1. open', '2. high', '3. low', '4. close', '5. volume']
    # data.columns = ['date', '1. open', '2. high', '3. low', '4. close']

    # print(data)

    data = data.drop('date', axis=1)
    data = data.drop(0, axis=0)

    data = data.values

    data_normaliser = preprocessing.MinMaxScaler()
    data_normalised = data_normaliser.fit_transform(data)

    # using the last {history_points} open close high low volume data points, predict the next open value
    ohlcv_histories_normalised = np.array([data_normalised[i:i + history_points].copy() for i in range(len(data_normalised) - history_points)])
    next_day_open_values_normalised = np.array([data_normalised[:, 0][i + history_points].copy() for i in range(len(data_normalised) - history_points)])
    next_day_open_values_normalised = np.expand_dims(next_day_open_values_normalised, -1)

    next_day_open_values = np.array([data[:, 0][i + history_points].copy() for i in range(len(data) - history_points)])
    next_day_open_values = np.expand_dims(next_day_open_values, -1)

    y_normaliser = preprocessing.MinMaxScaler()
    y_normaliser.fit(next_day_open_values)

    def calc_ema(values, time_period):
        # https://www.investopedia.com/ask/answers/122314/what-exponential-moving-average-ema-formula-and-how-ema-calculated.asp
        sma = np.mean(values[:, 3])
        ema_values = [sma]
        k = 2 / (1 + time_period)
        for i in range(len(his) - time_period, len(his)):
            close = his[i][3]
            ema_values.append(close * k + ema_values[-1] * (1 - k))
        return ema_values[-1]

    technical_indicators = []
    for his in ohlcv_histories_normalised:
        # note since we are using his[3] we are taking the SMA of the closing price
        sma = np.mean(his[:, 3])
        macd = calc_ema(his, 12) - calc_ema(his, 26)
        # technical_indicators.append(np.array([sma]))
        technical_indicators.append(np.array([sma,macd,]))


    technical_indicators = np.array(technical_indicators)

    tech_ind_scaler = preprocessing.MinMaxScaler()
    technical_indicators_normalised = tech_ind_scaler.fit_transform(technical_indicators)

    assert ohlcv_histories_normalised.shape[0] == next_day_open_values_normalised.shape[0] == technical_indicators_normalised.shape[0]
    return (ohlcv_histories_normalised, technical_indicators_normalised, next_day_open_values_normalised, next_day_open_values, y_normaliser)




def train():

    # MODEL
    import keras
    import tensorflow as tf
    from keras.models import Model
    from keras.layers import Dense, Dropout, LSTM, Input, Activation, concatenate
    from keras import optimizers
    import numpy as np
    np.random.seed(4)
    #from tensorflow import set_random_seed
    tf.random.set_seed(4)



    # dataset

    ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset('MSFT_intraday.csv')



    test_split = 0.9
    n = int(ohlcv_histories.shape[0] * test_split)

    ohlcv_train = ohlcv_histories[:n]
    tech_ind_train = technical_indicators[:n]
    y_train = next_day_open_values[:n]

    # import matplotlib.pyplot as plt
    # plt.plot(y_train)
    # plt.show()

    ohlcv_test = ohlcv_histories[n:]
    tech_ind_test = technical_indicators[n:]
    y_test = next_day_open_values[n:]

    unscaled_y_test = unscaled_y[n:]

    print(ohlcv_train.shape)
    print(ohlcv_test.shape)


    # model architecture

    # define two sets of inputs
    lstm_input = Input(shape=(history_points, 5), name='lstm_input')
    dense_input = Input(shape=(technical_indicators.shape[1],), name='tech_input')

    # the first branch operates on the first input
    x = LSTM(50, name='lstm_0')(lstm_input)
    x = Dropout(0.2, name='lstm_dropout_0')(x)
    lstm_branch = Model(inputs=lstm_input, outputs=x)

    # the second branch opreates on the second input
    y = Dense(20, name='tech_dense_0')(dense_input)
    y = Activation("relu", name='tech_relu_0')(y)
    y = Dropout(0.2, name='tech_dropout_0')(y)
    technical_indicators_branch = Model(inputs=dense_input, outputs=y)

    # combine the output of the two branches
    combined = concatenate([lstm_branch.output, technical_indicators_branch.output], name='concatenate')

    z = Dense(64, activation="sigmoid", name='dense_pooling')(combined)
    z = Dense(1, activation="linear", name='dense_out')(z)

    # our model will accept the inputs of the two branches and
    # then output a single value
    model = Model(inputs=[lstm_branch.input, technical_indicators_branch.input], outputs=z)
    adam = optimizers.Adam(lr=0.0005)
    model.compile(optimizer=adam, loss='mse')
    model.fit(x=[ohlcv_train, tech_ind_train], y=y_train, batch_size=32, epochs=1, shuffle=True, validation_split=0.1)


    # evaluation

    y_test_predicted = model.predict([ohlcv_test, tech_ind_test])
    y_test_predicted = y_normaliser.inverse_transform(y_test_predicted)
    y_predicted = model.predict([ohlcv_histories, technical_indicators])
    y_predicted = y_normaliser.inverse_transform(y_predicted)
    assert unscaled_y_test.shape == y_test_predicted.shape
    real_mse = np.mean(np.square(unscaled_y_test - y_test_predicted))
    scaled_mse = real_mse / (np.max(unscaled_y_test) - np.min(unscaled_y_test)) * 100
    print(scaled_mse)

    import matplotlib.pyplot as plt

    plt.gcf().set_size_inches(22, 15, forward=True)

    start = 0
    end = -1

    real = plt.plot(unscaled_y_test[start:end], label='real')
    pred = plt.plot(y_test_predicted[start:end], label='predicted')

    # real = plt.plot(unscaled_y[start:end], label='real')
    # pred = plt.plot(y_predicted[start:end], label='predicted')

    plt.legend(['Real', 'Predicted'])

    plt.show()

    from datetime import datetime
    model.save(constants.AI_MODEL+f'technical_model.h5')




def predict_test():

    # TRADING ALGORITHM
    import numpy as np
    from keras.models import load_model


    model = load_model(constants.AI_MODEL+'technical_model.h5')

    ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset('MSFT_intraday.csv')

    test_split = 0.9
    n = int(ohlcv_histories.shape[0] * test_split)

    ohlcv_train = ohlcv_histories[:n]
    tech_ind_train = technical_indicators[:n]
    y_train = next_day_open_values[:n]

    ohlcv_test = ohlcv_histories[n:]
    tech_ind_test = technical_indicators[n:]
    y_test = next_day_open_values[n:]

    unscaled_y_test = unscaled_y[n:]

    # print([ohlcv_test, tech_ind_test])
    # print(ohlcv_test.shape)
    # print(tech_ind_test.shape)
    y_test_predicted = model.predict([ohlcv_test, tech_ind_test])
    y_test_predicted = y_normaliser.inverse_transform(y_test_predicted)

    buys = []
    sells = []
    thresh = 0.1

    start = 0
    end = -1

    x = -1
    # print(ohlcv_test[0])
    # print(tech_ind_test[0])
    count = 0
    for ohlcv, ind in zip(ohlcv_test[start: end], tech_ind_test[start: end]):
        count += 1
        # if count == 0:
        #     count += 1
        #     continue
        # print(ohlcv)
        # print(ind)
        # ohlcv = ohlcv.reshape(1, ohlcv.shape[0], ohlcv.shape[1])
        # ind = ind.reshape(1, ind.shape[0])
        normalised_price_today = ohlcv[-1][0]
        normalised_price_today = np.array([[normalised_price_today]])
        price_today = y_normaliser.inverse_transform(normalised_price_today)
        # print(ohlcv.reshape(1, ohlcv.shape[0], ohlcv.shape[1]).shape)
        # print(ind.reshape(1, ind.shape[0]).shape)
        # result = model.predict(ohlcv.reshape(1, ohlcv.shape[0], ohlcv.shape[1]), ind.reshape(1, ind.shape[0]))
        # print([np.array([ohlcv,]), np.array([ind,])])
        print(len(ohlcv))
        result = model.predict([np.array([ohlcv,]), np.array([ind,])])
        predicted_price_tomorrow = np.squeeze(y_normaliser.inverse_transform(result))
        # predicted_price_tomorrow = np.squeeze(y_test_predicted[count-1])
        delta = predicted_price_tomorrow - price_today
        if delta > thresh:
            buys.append((x, price_today[0][0]))
        elif delta < -thresh:
            sells.append((x, price_today[0][0]))
        x += 1
    print(f"buys: {len(buys)}")
    print(f"sells: {len(sells)}")


    def compute_earnings(buys_, sells_):
        purchase_amt = 10
        stock = 0
        balance = 0
        while len(buys_) > 0 and len(sells_) > 0:
            if buys_[0][0] < sells_[0][0]:
                # time to buy $10 worth of stock
                balance -= purchase_amt
                stock += purchase_amt / buys_[0][1]
                buys_.pop(0)
            else:
                # time to sell all of our stock
                balance += stock * sells_[0][1]
                stock = 0
                sells_.pop(0)
        print(f"earnings: ${balance}")


    # we create new lists so we dont modify the original
    compute_earnings([b for b in buys], [s for s in sells])

    import matplotlib.pyplot as plt

    plt.gcf().set_size_inches(22, 15, forward=True)

    real = plt.plot(unscaled_y_test[start:end], label='real')
    pred = plt.plot(y_test_predicted[start:end], label='predicted')

    if len(buys) > 0:
        plt.scatter(list(list(zip(*buys))[0]), list(list(zip(*buys))[1]), c='#00ff00', s=50)
    if len(sells) > 0:
        plt.scatter(list(list(zip(*sells))[0]), list(list(zip(*sells))[1]), c='#ff0000', s=50)

    # real = plt.plot(unscaled_y[start:end], label='real')
    # pred = plt.plot(y_predicted[start:end], label='predicted')

    plt.legend(['Real', 'Predicted', 'Buy', 'Sell'])

    plt.show()


def predict_buy(ticker):

    model = load_model(constants.AI_MODEL+'technical_model.h5')
    ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset('MSFT_intraday.csv')

    ohlcv_test = ohlcv_histories[-50:]
    tech_ind_test = technical_indicators[-50:]
    y_test = next_day_open_values[-50:]

    unscaled_y_test = unscaled_y[-50:]
    print(len(ohlcv_test))

    normalised_price_today = ohlcv_test[-1][0]
    normalised_price_today = [normalised_price_today]
    # print(normalised_price_today)
    price_today = y_normaliser.inverse_transform(normalised_price_today)

    # print([ohlcv_test, tech_ind_test])
    result = model.predict([np.array(ohlcv_test), np.array(tech_ind_test)])
    predicted_price_tomorrow = np.squeeze(y_normaliser.inverse_transform(result))

    thresh = 0.1
    
    delta = predicted_price_tomorrow[-1] - price_today
    if delta > thresh:
        return True


def predict_sell(ticker):
    
    model = load_model(constants.AI_MODEL+'technical_model.h5')
    ohlcv_histories, technical_indicators, next_day_open_values, unscaled_y, y_normaliser = csv_to_dataset('MSFT_intraday.csv')

    ohlcv_test = ohlcv_histories[:]
    tech_ind_test = technical_indicators[:]
    y_test = next_day_open_values[:]

    unscaled_y_test = unscaled_y[:]

    normalised_price_today = ohlcv[-1][0]
    normalised_price_today = np.array([[normalised_price_today]])
    price_today = y_normaliser.inverse_transform(normalised_price_today)

    result = model.predict([np.array([ohlcv_test,]), np.array([tech_ind_test,])])
    predicted_price_tomorrow = np.squeeze(y_normaliser.inverse_transform(result))

    thresh = 0.1
    
    delta = predicted_price_tomorrow - price_today
    if delta < thresh:
        return True


def indicators_dataframe(ticker):
    return csv_to_dataset("csv_path")



if __name__ == "__main__":
    # train()
    predict_test()