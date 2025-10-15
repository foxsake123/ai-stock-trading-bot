"""Tests for insider transaction monitoring"""

import pytest
from datetime import datetime, timedelta
from data_sources.insider_monitor import InsiderMonitor, InsiderTransaction, get_insider_signals
from unittest.mock import Mock, MagicMock

@pytest.fixture
def mock_api_client():
    """Mock Financial Datasets API client"""
    client = Mock()
    return client

@pytest.fixture
def insider_monitor(mock_api_client):
    """Create InsiderMonitor instance with mock API"""
    return InsiderMonitor(mock_api_client)

@pytest.fixture
def sample_filing():
    """Sample Form 4 filing data"""
    return {
        'filing_date': datetime.now().isoformat(),
        'transaction_date': datetime.now().isoformat(),
        'reporting_owner': 'John Doe',
        'title': 'CEO',
        'transaction_type': 'PURCHASE',
        'shares_traded': 10000,
        'price_per_share': 50.0
    }

@pytest.fixture
def sample_old_filing():
    """Sample old filing beyond cutoff date"""
    old_date = datetime.now() - timedelta(days=45)
    return {
        'filing_date': old_date.isoformat(),
        'transaction_date': old_date.isoformat(),
        'reporting_owner': 'Jane Smith',
        'title': 'CFO',
        'transaction_type': 'PURCHASE',
        'shares_traded': 5000,
        'price_per_share': 50.0
    }

class TestInsiderMonitorInitialization:
    """Test InsiderMonitor initialization"""

    def test_initialization(self, insider_monitor):
        """Test InsiderMonitor initialization"""
        assert insider_monitor.significance_threshold == 500_000
        assert 'CEO' in insider_monitor.c_suite_titles
        assert 'CFO' in insider_monitor.c_suite_titles
        assert 'President' in insider_monitor.c_suite_titles

    def test_initialization_with_api_client(self, mock_api_client):
        """Test initialization with API client"""
        monitor = InsiderMonitor(mock_api_client)
        assert monitor.api == mock_api_client

class TestParseFilings:
    """Test filing parsing logic"""

    def test_parse_filing_buy(self, insider_monitor, sample_filing):
        """Test parsing a buy transaction"""
        transaction = insider_monitor._parse_filing('AAPL', sample_filing)

        assert transaction is not None
        assert transaction.ticker == 'AAPL'
        assert transaction.insider_name == 'John Doe'
        assert transaction.title == 'CEO'
        assert transaction.transaction_type == 'BUY'
        assert transaction.shares == 10000
        assert transaction.price == 50.0
        assert transaction.value == 500_000
        assert transaction.signal == 'BULLISH'

    def test_parse_filing_sell(self, insider_monitor, sample_filing):
        """Test parsing a sell transaction"""
        sample_filing['transaction_type'] = 'SALE'
        sample_filing['shares_traded'] = 20000

        transaction = insider_monitor._parse_filing('AAPL', sample_filing)

        assert transaction.transaction_type == 'SELL'
        assert transaction.value == 1_000_000
        assert transaction.signal == 'BEARISH'

    def test_parse_filing_purchase_normalization(self, insider_monitor, sample_filing):
        """Test that PURCHASE is normalized to BUY"""
        sample_filing['transaction_type'] = 'PURCHASE'
        transaction = insider_monitor._parse_filing('AAPL', sample_filing)
        assert transaction.transaction_type == 'BUY'

    def test_parse_filing_sale_normalization(self, insider_monitor, sample_filing):
        """Test that SALE is normalized to SELL"""
        sample_filing['transaction_type'] = 'SALE'
        transaction = insider_monitor._parse_filing('AAPL', sample_filing)
        assert transaction.transaction_type == 'SELL'

    def test_parse_filing_invalid_transaction_type(self, insider_monitor, sample_filing):
        """Test that invalid transaction types return None"""
        sample_filing['transaction_type'] = 'GRANT'  # Not a buy or sell
        transaction = insider_monitor._parse_filing('AAPL', sample_filing)
        assert transaction is None

    def test_parse_filing_missing_data(self, insider_monitor):
        """Test parsing filing with missing data"""
        incomplete_filing = {
            'filing_date': datetime.now().isoformat()
        }
        transaction = insider_monitor._parse_filing('AAPL', incomplete_filing)
        # Should handle gracefully - returns None or transaction with defaults
        assert transaction is None or isinstance(transaction, InsiderTransaction)

    def test_parse_filing_default_values(self, insider_monitor):
        """Test that missing fields use default values"""
        minimal_filing = {
            'filing_date': datetime.now().isoformat(),
            'transaction_type': 'BUY',
            'shares_traded': 1000,
            'price_per_share': 100.0
        }
        transaction = insider_monitor._parse_filing('AAPL', minimal_filing)

        if transaction:
            assert transaction.insider_name == 'Unknown'
            assert transaction.title == 'Unknown'

class TestSignalDetermination:
    """Test signal determination logic"""

    def test_determine_signal_bullish_c_suite(self, insider_monitor):
        """Test bullish signal for C-suite buy"""
        signal = insider_monitor._determine_signal('BUY', 600_000, 'CEO')
        assert signal == 'BULLISH'

    def test_determine_signal_bullish_large_non_c_suite(self, insider_monitor):
        """Test bullish signal for large non-C-suite buy"""
        signal = insider_monitor._determine_signal('BUY', 600_000, 'Director')
        assert signal == 'BULLISH'

    def test_determine_signal_neutral_small_buy(self, insider_monitor):
        """Test neutral signal for small buy"""
        signal = insider_monitor._determine_signal('BUY', 100_000, 'Employee')
        assert signal == 'NEUTRAL'

    def test_determine_signal_bearish_large_sell(self, insider_monitor):
        """Test bearish signal for large sell"""
        signal = insider_monitor._determine_signal('SELL', 1_500_000, 'CFO')
        assert signal == 'BEARISH'

    def test_determine_signal_neutral_small_sell(self, insider_monitor):
        """Test neutral signal for small routine sell"""
        signal = insider_monitor._determine_signal('SELL', 100_000, 'Director')
        assert signal == 'NEUTRAL'

    def test_determine_signal_neutral_medium_sell(self, insider_monitor):
        """Test neutral signal for medium sell below threshold"""
        signal = insider_monitor._determine_signal('SELL', 800_000, 'Director')
        assert signal == 'NEUTRAL'

    def test_determine_signal_c_suite_detection(self, insider_monitor):
        """Test C-suite title detection (case insensitive)"""
        for title in ['ceo', 'CEO', 'Chief Executive Officer']:
            signal = insider_monitor._determine_signal('BUY', 600_000, title)
            assert signal == 'BULLISH', f"Failed for title: {title}"

    def test_determine_signal_edge_cases(self, insider_monitor):
        """Test edge cases for signal determination"""
        # Exactly at threshold - C-suite buy
        signal = insider_monitor._determine_signal('BUY', 500_000, 'CEO')
        assert signal == 'BULLISH'

        # Exactly at 2x threshold - C-suite sell
        signal = insider_monitor._determine_signal('SELL', 1_000_000, 'CFO')
        assert signal == 'BEARISH'

        # Just below threshold
        signal = insider_monitor._determine_signal('BUY', 499_999, 'CEO')
        assert signal == 'NEUTRAL'

class TestFetchTransactions:
    """Test transaction fetching"""

    def test_fetch_recent_transactions(self, insider_monitor, mock_api_client, sample_filing):
        """Test fetching recent transactions"""
        mock_api_client.get_filings.return_value = [sample_filing]

        transactions = insider_monitor.fetch_recent_transactions('AAPL', days=30)

        assert len(transactions) == 1
        assert transactions[0].ticker == 'AAPL'
        mock_api_client.get_filings.assert_called_once()

    def test_fetch_transactions_filters_old(self, insider_monitor, mock_api_client, sample_filing, sample_old_filing):
        """Test that old transactions are filtered out"""
        mock_api_client.get_filings.return_value = [sample_filing, sample_old_filing]

        transactions = insider_monitor.fetch_recent_transactions('AAPL', days=30)

        # Only recent filing should be returned
        assert len(transactions) == 1
        assert transactions[0].insider_name == 'John Doe'

    def test_fetch_transactions_api_error(self, insider_monitor, mock_api_client):
        """Test handling of API errors"""
        mock_api_client.get_filings.side_effect = Exception("API Error")

        transactions = insider_monitor.fetch_recent_transactions('AAPL', days=30)

        assert transactions == []

    def test_fetch_transactions_empty_response(self, insider_monitor, mock_api_client):
        """Test handling of empty API response"""
        mock_api_client.get_filings.return_value = []

        transactions = insider_monitor.fetch_recent_transactions('AAPL', days=30)

        assert transactions == []

    def test_fetch_transactions_custom_days(self, insider_monitor, mock_api_client, sample_filing):
        """Test custom days parameter"""
        mock_api_client.get_filings.return_value = [sample_filing]

        transactions = insider_monitor.fetch_recent_transactions('AAPL', days=60)

        assert len(transactions) == 1
        mock_api_client.get_filings.assert_called_with(ticker='AAPL', filing_type='4', limit=50)

class TestSignificantTransactions:
    """Test filtering for significant transactions"""

    def test_get_significant_transactions(self, insider_monitor, mock_api_client, sample_filing):
        """Test filtering for significant transactions only"""
        # Create mix of significant and insignificant
        significant_filing = sample_filing.copy()
        insignificant_filing = sample_filing.copy()
        insignificant_filing['shares_traded'] = 100  # Only $5K
        insignificant_filing['title'] = 'Employee'
        insignificant_filing['reporting_owner'] = 'Small Trader'

        mock_api_client.get_filings.return_value = [significant_filing, insignificant_filing]

        results = insider_monitor.get_significant_transactions(['AAPL'], days=30)

        assert 'AAPL' in results
        assert len(results['AAPL']) == 1  # Only significant transaction
        assert results['AAPL'][0].signal == 'BULLISH'

    def test_get_significant_transactions_multiple_tickers(self, insider_monitor, mock_api_client, sample_filing):
        """Test fetching significant transactions for multiple tickers"""
        mock_api_client.get_filings.return_value = [sample_filing]

        results = insider_monitor.get_significant_transactions(['AAPL', 'MSFT'], days=30)

        assert len(results) == 2
        assert 'AAPL' in results
        assert 'MSFT' in results
        assert mock_api_client.get_filings.call_count == 2

    def test_get_significant_transactions_no_significant(self, insider_monitor, mock_api_client):
        """Test when no significant transactions found"""
        insignificant_filing = {
            'filing_date': datetime.now().isoformat(),
            'transaction_date': datetime.now().isoformat(),
            'reporting_owner': 'Employee',
            'title': 'Engineer',
            'transaction_type': 'BUY',
            'shares_traded': 100,
            'price_per_share': 50.0
        }
        mock_api_client.get_filings.return_value = [insignificant_filing]

        results = insider_monitor.get_significant_transactions(['AAPL'], days=30)

        assert results == {}

class TestReportGeneration:
    """Test report generation"""

    def test_generate_summary_report(self, insider_monitor):
        """Test markdown report generation"""
        transactions = {
            'AAPL': [
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='John Doe',
                    title='CEO',
                    transaction_type='BUY',
                    shares=10000,
                    price=50.0,
                    value=500_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BULLISH'
                )
            ]
        }

        report = insider_monitor.generate_summary_report(transactions)

        assert '## Insider Transaction Signals' in report
        assert 'AAPL' in report
        assert 'John Doe' in report
        assert 'CEO' in report
        assert 'BULLISH' in report
        assert '$500,000' in report

    def test_generate_summary_report_empty(self, insider_monitor):
        """Test report generation with no transactions"""
        report = insider_monitor.generate_summary_report({})
        assert 'No significant insider transactions detected' in report

    def test_generate_summary_report_multiple_tickers(self, insider_monitor):
        """Test report with multiple tickers"""
        transactions = {
            'AAPL': [
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='John Doe',
                    title='CEO',
                    transaction_type='BUY',
                    shares=10000,
                    price=50.0,
                    value=500_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BULLISH'
                )
            ],
            'MSFT': [
                InsiderTransaction(
                    ticker='MSFT',
                    insider_name='Jane Smith',
                    title='CFO',
                    transaction_type='SELL',
                    shares=20000,
                    price=100.0,
                    value=2_000_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BEARISH'
                )
            ]
        }

        report = insider_monitor.generate_summary_report(transactions)

        assert 'AAPL' in report
        assert 'MSFT' in report
        assert 'John Doe' in report
        assert 'Jane Smith' in report

    def test_generate_summary_report_net_bullish(self, insider_monitor):
        """Test report net signal for bullish ticker"""
        transactions = {
            'AAPL': [
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='Buyer 1',
                    title='CEO',
                    transaction_type='BUY',
                    shares=10000,
                    price=50.0,
                    value=500_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BULLISH'
                ),
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='Buyer 2',
                    title='CFO',
                    transaction_type='BUY',
                    shares=5000,
                    price=50.0,
                    value=250_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BULLISH'
                )
            ]
        }

        report = insider_monitor.generate_summary_report(transactions)

        assert '[BUY] **BULLISH**' in report
        assert '2 buys vs 0 sells' in report

    def test_generate_summary_report_net_bearish(self, insider_monitor):
        """Test report net signal for bearish ticker"""
        transactions = {
            'AAPL': [
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='Seller 1',
                    title='CEO',
                    transaction_type='SELL',
                    shares=20000,
                    price=50.0,
                    value=1_000_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BEARISH'
                ),
                InsiderTransaction(
                    ticker='AAPL',
                    insider_name='Seller 2',
                    title='CFO',
                    transaction_type='SELL',
                    shares=30000,
                    price=50.0,
                    value=1_500_000,
                    filing_date=datetime.now(),
                    transaction_date=datetime.now(),
                    signal='BEARISH'
                )
            ]
        }

        report = insider_monitor.generate_summary_report(transactions)

        assert '[SELL] **BEARISH**' in report
        assert '2 sells vs 0 buys' in report

class TestConvenienceFunction:
    """Test get_insider_signals convenience function"""

    def test_get_insider_signals_integration(self, mock_api_client, sample_filing):
        """Test the convenience function"""
        mock_api_client.get_filings.return_value = [sample_filing]

        result = get_insider_signals(['AAPL'], mock_api_client, days=30)

        assert 'transactions' in result
        assert 'report' in result
        assert 'summary' in result
        assert result['summary']['total_tickers'] == 1
        assert result['summary']['bullish_signals'] == 1
        assert result['summary']['bearish_signals'] == 0

    def test_get_insider_signals_summary_counts(self, mock_api_client, sample_filing):
        """Test summary statistics calculation"""
        # Create multiple significant transactions
        buy_filing = sample_filing.copy()
        sell_filing = sample_filing.copy()
        sell_filing['transaction_type'] = 'SELL'
        sell_filing['shares_traded'] = 20000

        mock_api_client.get_filings.return_value = [buy_filing, sell_filing]

        result = get_insider_signals(['AAPL'], mock_api_client, days=30)

        assert result['summary']['total_transactions'] == 2
        assert result['summary']['bullish_signals'] == 1
        assert result['summary']['bearish_signals'] == 1

    def test_get_insider_signals_empty(self, mock_api_client):
        """Test convenience function with no transactions"""
        mock_api_client.get_filings.return_value = []

        result = get_insider_signals(['AAPL'], mock_api_client, days=30)

        assert result['summary']['total_tickers'] == 0
        assert result['summary']['total_transactions'] == 0
        assert 'No significant insider transactions' in result['report']
