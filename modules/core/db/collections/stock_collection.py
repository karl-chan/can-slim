from typing import List, Dict, Iterable

from pymongo import ReplaceOne, IndexModel, ASCENDING

from modules.core.db.conn import get_collection
from modules.core.model.stock import Stock, HistoricDataPoint, EarningsEvent

# database stock collections
_collection = get_collection('stock')


def list_stocks(fields: List[str] = []) -> List[Stock]:
    args = {}
    if fields:
        args['projection'] = {field: True for field in fields}
    cursor = _collection.find(**args)
    return [_document_to_stock(doc) for doc in cursor]


def upsert_stocks(stocks: Iterable[Stock]) -> None:
    if not stocks:
        return
    requests = [ReplaceOne(filter={'ticker': s.ticker}, replacement=_stock_to_document(s), upsert=True) for s in stocks]
    return _collection.bulk_write(requests)


def delete_stocks(tickers: Iterable[str]) -> None:
    if not tickers:
        return
    return _collection.delete_many(filter={'ticker': {'$in': list(tickers)}})


def create_indexes() -> None:
    ticker_ts_index = IndexModel([('ticker', ASCENDING), ('time_series.time', ASCENDING)], unique=True)
    name_index = IndexModel([('name', ASCENDING)], unique=True)
    cusip_index = IndexModel([('cusip', ASCENDING)], unique=True)
    isin_index = IndexModel([('isin', ASCENDING)], unique=True)
    sedol_index = IndexModel([('sedol', ASCENDING)], unique=True)
    _collection.create_indexes([ticker_ts_index, name_index, cusip_index, isin_index, sedol_index])


def _document_to_stock(document: Dict) -> Stock:
    document.pop('_id', None)
    if 'time_series' in document:
        document['time_series'] = [HistoricDataPoint(**pt) for pt in document['time_series']]
    if 'quarterly_earnings' in document:
        document['quarterly_earnings'] = [EarningsEvent(**e) for e in document['quarterly_earnings']]
    stock = Stock(**document)
    return stock


def _stock_to_document(stock: Stock) -> Dict:
    document = stock._asdict()
    document['time_series'] = [pt._asdict() for pt in stock.time_series]
    document['quarterly_earnings'] = [e._asdict() for e in stock.quarterly_earnings]
    return document
