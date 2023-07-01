from typing import Union

from fastapi import FastAPI, HTTPException
from bsedata.bse import BSE

from datetime import datetime

app = FastAPI()

bse = BSE(update_codes = True)


def getRightFormat(time_series):
    """
    Highcharts.js requires the timeseries data to be in a certain format. A 2x2 array
    with each array containing timestamp in milliseconds and respective value.

    time_series = [{'date': 'Fri Dec 30 2022 00:00:00', 'value': 6574.16, 'vol': 20394}]
    """
    data = []
    for s in time_series:
        time = s['date']
        time_obj = datetime.strptime(time, "%a %b %d %Y %H:%M:%S")
        timestamp = int(time_obj.timestamp()) * 1000
        data.append([timestamp, s['value']])
    return data


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/bse/{id}")
async def read_stock(id: int):
    q = str(id)
    if bse.verifyScripCode(q):
        quote = bse.getQuote(q)
        return quote
    else:
        raise HTTPException(status_code=404, detail="Please check your BSE scrip code")
    
    
@app.get("/bse/{id}/time/{period}")
async def read_stock_price_history(id: int, period: str):
    q = str(id)
    p = str(period)
    if bse.verifyScripCode(q) and p in ['1M', '3M', '6M', '12M']:
        price_history = bse.getPeriodTrend(q, p)
        price_history_milliseconds_format = getRightFormat(price_history)
        return price_history_milliseconds_format
    elif p not in ['1M', '3M', '6M', '12M']:
        raise HTTPException(status_code=404, detail="The permitted time periods are 1M, 3M, 6M & 12M")
    else:
        raise HTTPException(status_code=404, detail="Kindly check your BSE scrip code")

@app.get("/bse/list/{performers}")
async def read_bse_performers(performers: str):
    if performers == "topGainers":
        return bse.topGainers()
    elif performers == "topLosers":
        return bse.topLosers()
    else:
        raise HTTPException(status_code=404, detail="Oops, try topGainers or topLosers")
    
    


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}