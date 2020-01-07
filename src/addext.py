def get_ext(url):
    chonks = url.split('.')
    return chonks[-1].lower()

def recreateTicker(tickers):
    if ':' in tickers or '&' in tickers:
        tickers = tickers.replace(' ', '').replace(':', ',').replace('&', ',')
    i = 0
    while i < len(tickers):
        if not (tickers[i].isalpha() or tickers[i] == ',' or tickers[i] == ' '):
            tickers = tickers.replace(tickers[i], '')
            i = 0
        else:
            i += 1
    return tickers


def fixTicker(ticker, secondary_ticker):
    ticker = recreateTicker(ticker)
    secondary_ticker = recreateTicker(secondary_ticker)
    ticker = ticker.split(',')
    secondary_ticker = secondary_ticker.split(',')
    for tick in secondary_ticker:
        if not tick in ticker:
            ticker.append(tick)
    if len(ticker) > 1:
        ticker = ",".join(ticker)
    elif len(ticker) > 0:
        ticker = ticker[0]
    else:
        ticker = ""
    if len(ticker) > 0 and ticker[-1] == ',':
        ticker = ticker[:-1]
    if len(ticker) > 0 and ticker[0] == ',':
        ticker = ticker[1:]
    if ',' in ticker:
        ticker = ticker.replace(' ', '')
    return ticker