import requests
import time

API_KEY = {'X-API-key': 'FELIPE_IS_THE_BEST'}
link = 'http://localhost:20029/v1'


def arbitrage(book_A, book_M, s):

    # Get the best bid and ask prices for A and M
    A_bid = [[book_A['bids'][i][j] for i in range(10)] for j in ['price', 'quantity']]
    A_ask = [[book_A['asks'][i][j] for i in range(10)] for j in ['price', 'quantity']]

    M_bid = [[book_M['bids'][i][j] for i in range(10)] for j in ['price', 'quantity']]
    M_ask = [[book_M['asks'][i][j] for i in range(10)] for j in ['price', 'quantity']]

    def arbitrage_opportunity(ask, bid, ticker_buy, ticker_sell, scaling_factor, i=0):
        if (len(ask) == 0) or (len(bid) == 0):
            return

        if ask[0][0] < bid[0][0]:
            print("TRANSACTION ARBITRAGE")

            # POST market buy order
            mkt_buy_params = {'ticker': ticker_buy, 'type': 'MARKET',
                              'quantity': (2**i) * scaling_factor * min(ask[1][0], bid[1][0]), 'action': 'BUY'}
            s.post(f'{link}/orders', params=mkt_buy_params)

            # POST sell market order
            mkt_sell_params = {'ticker': ticker_sell, 'type': 'MARKET',
                               'quantity': (2**i) * scaling_factor * min(ask[1][0], bid[1][0]), 'action': 'SELL'}
            s.post(f'{link}/orders', params=mkt_sell_params)

            i += 1

            if min(ask[1][0], bid[1][0]) == bid[1][0]:
                ask[1][0] -= bid[1][0]
                bid = [bid[col][1:] for col in range(len(bid))]
                return arbitrage_opportunity(ask, bid, s, ticker_buy, ticker_sell, i)

            else:
                bid[1][0] -= ask[1][0]
                ask = [ask[col][1:] for col in range(len(ask))]
                return arbitrage_opportunity(ask, bid, s, ticker_buy, ticker_sell, i)

        else:
            return

    arbitrage_opportunity(A_ask, M_bid, s, ticker_buy="CRZY_A", ticker_sell="CRZY_M")
    arbitrage_opportunity(M_ask, A_bid, s, ticker_buy="CRZY_M", ticker_sell="CRZY_A")


def main():
    # execute strategy while market is activated
    while True:
        # get book information
        with requests.Session() as s:
            s.headers.update(API_KEY)
            book_A = s.get(f'{link}/securities/book', params={'ticker': 'CRZY_A'})
            book_M = s.get(f'{link}/securities/book', params={'ticker': 'CRZY_M'})

        if book_A.ok and book_M.ok:
            # Execute Algo Arbitrage Strategy
            arbitrage(book_A.json(), book_M.json(), s)

        else:
            print("Failed: No info available")
            break
        time.sleep(1)


if __name__ == '__main__':
    main()
