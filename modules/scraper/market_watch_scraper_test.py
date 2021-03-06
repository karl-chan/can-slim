import pytest

from modules.scraper.market_watch_scraper import MarketWatchScraper
from datetime import datetime


@pytest.fixture
def scraper():
    return MarketWatchScraper()

def test_get_basic_stock_info(scraper):
    basic_info = scraper.get_basic_stock_info(ticker='HSBA', country_code='UK')
    assert basic_info.ticker == 'HSBA'
    assert basic_info.name == 'HSBC Holdings PLC (UK Reg)'
    assert basic_info.cusip == 'G4634U169'
    assert basic_info.sedol == '0540528'
    assert basic_info.isin == 'GB0005405286'
    assert basic_info.country_code == 'UK'
    assert basic_info.iso_code == 'XLON'

def test_get_time_series(scraper):
    time_series = scraper.get_time_series(ticker='HSBA', country_code='UK', iso_code='XLON', step='P1D', timeframe='P5D')
    assert 3 <= len(time_series) <= 5
    for point in time_series:
        assert type(point.time) == datetime
        assert point.open > 0
        assert point.high > 0
        assert point.low > 0
        assert point.close > 0
        assert point.volume > 0
        assert point.low <= point.open <= point.high
        assert point.low <= point.close <= point.high

def test_get_quarterly_earnings(scraper):
    quarterly_earnings = scraper.get_quarterly_earnings(ticker='HSBA', country_code='UK', iso_code='XLON', timeframe='P5Y')
    assert len(quarterly_earnings) >= 20
    for point in quarterly_earnings:
        assert type(point.time) == datetime
        assert point.value