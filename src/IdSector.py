import pymysql
pymysql.install_as_MySQLdb()

import sqlalchemy as sa
import warnings
from sqlalchemy import exc as sa_exc

from util import *

warnings.simplefilter("ignore", category=sa_exc.SAWarning)

memsql_engine = create_memsql_engine()

results = memsql_engine.execute('''SELECT ticker, MAX(sub_sub_sector) sector
FROM 
(    
    SELECT ticker, sub_sub_sector, rank() over (PARTITION BY ticker ORDER BY cnt DESC) AS rank
    FROM 
        (
        SELECT ticker, sub_sub_sector, count(*) AS cnt
        FROM security_master
        WHERE ticker IS NOT NULL 
        	AND NOT ticker RLIKE '\\\\+|[0-9]|/|<'
        	AND NOT sub_sub_sector = "CURRENCY"
        GROUP BY ticker, sub_sub_sector
        ) s
) s
WHERE rank = 1
GROUP BY ticker
ORDER BY ticker''')

ticker_ind = {}
for row in results:
    ticker = row["ticker"]
    industry = row["sector"]
    ticker_ind[ticker] = industry

def getSector(ticker):
    industries = []
    if ',' in ticker:
        tickers = ticker.split(',')
    else:
        tickers = [ticker]
    for ticker in tickers:
        if ticker in ticker_ind.keys():
            tick = ticker_ind[ticker]
            if '_' in tick:
                tick = tick.split('_')
                tick = list(map(lambda x: x[0] + x[1:].lower(), tick))
                tick = ' '.join(tick)
            else:
                tick = tick[0] + tick[1:].lower()
            industries.append(tick)
        else:
            industries.append("Unknown")
    industries = list(set(industries))
    return ",".join(industries)