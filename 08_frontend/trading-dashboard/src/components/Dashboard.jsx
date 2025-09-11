import React, { useState, useEffect } from 'react';
import axios from 'axios';
import io from 'socket.io-client';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, DollarSign, Activity, AlertCircle, CheckCircle, XCircle, RefreshCw } from 'lucide-react';
import TradingPanel from './TradingPanel';

const API_BASE_URL = 'http://localhost:8000';

const Dashboard = () => {
  const [portfolio, setPortfolio] = useState(null);
  const [positions, setPositions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [agents, setAgents] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [socket, setSocket] = useState(null);
  const [realtimeData, setRealtimeData] = useState({});

  // Fetch portfolio data
  const fetchPortfolio = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/portfolio/summary`);
      setPortfolio(response.data.stats);
      setPositions(response.data.positions || []);
    } catch (err) {
      console.error('Error fetching portfolio:', err);
      setError('Failed to fetch portfolio data');
    }
  };

  // Fetch recent trades
  const fetchTrades = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/trades?limit=10`);
      setTrades(response.data);
    } catch (err) {
      console.error('Error fetching trades:', err);
    }
  };

  // Fetch agent status
  const fetchAgentStatus = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/status`);
      setAgents(response.data);
    } catch (err) {
      console.error('Error fetching agent status:', err);
    }
  };

  // Initialize WebSocket connection
  useEffect(() => {
    const ws = io(`${API_BASE_URL}/ws`, {
      transports: ['websocket']
    });

    ws.on('connect', () => {
      console.log('WebSocket connected');
    });

    ws.on('portfolio_update', (data) => {
      setPortfolio(data);
    });

    ws.on('trade_executed', (trade) => {
      setTrades(prev => [trade, ...prev.slice(0, 9)]);
    });

    ws.on('price_update', (data) => {
      setRealtimeData(prev => ({ ...prev, ...data }));
    });

    setSocket(ws);

    return () => {
      ws.close();
    };
  }, []);

  // Initial data fetch
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      await Promise.all([
        fetchPortfolio(),
        fetchTrades(),
        fetchAgentStatus()
      ]);
      setIsLoading(false);
    };

    fetchData();
    const interval = setInterval(fetchData, 30000); // Refresh every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <RefreshCw className="animate-spin h-8 w-8 text-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-red-500 flex items-center">
          <AlertCircle className="mr-2" />
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">AI Trading Dashboard</h1>
        <p className="text-gray-400">Real-time portfolio monitoring and trading insights</p>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Total Value</span>
            <DollarSign className="h-5 w-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">
            {portfolio ? formatCurrency(portfolio.total_value) : '$0'}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Total P&L</span>
            {portfolio?.total_unrealized_pnl >= 0 ? (
              <TrendingUp className="h-5 w-5 text-green-500" />
            ) : (
              <TrendingDown className="h-5 w-5 text-red-500" />
            )}
          </div>
          <div className={`text-2xl font-bold ${portfolio?.total_unrealized_pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            {portfolio ? formatCurrency(portfolio.total_unrealized_pnl) : '$0'}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Win Rate</span>
            <Activity className="h-5 w-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">
            {portfolio ? formatPercent(portfolio.win_rate) : '0%'}
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Sharpe Ratio</span>
            <Activity className="h-5 w-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">
            {portfolio ? portfolio.portfolio_sharpe.toFixed(2) : '0.00'}
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Positions Table */}
        <div className="lg:col-span-2 bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">Current Positions</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="text-left text-gray-400 border-b border-gray-700">
                  <th className="pb-2">Symbol</th>
                  <th className="pb-2">Quantity</th>
                  <th className="pb-2">Entry Price</th>
                  <th className="pb-2">Current Price</th>
                  <th className="pb-2">P&L</th>
                  <th className="pb-2">P&L %</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((position) => {
                  const currentPrice = realtimeData[position.ticker]?.price || position.current_price;
                  const pnl = (currentPrice - position.entry_price) * position.quantity;
                  const pnlPercent = ((currentPrice - position.entry_price) / position.entry_price);
                  
                  return (
                    <tr key={position.ticker} className="border-b border-gray-700">
                      <td className="py-3 font-semibold">{position.ticker}</td>
                      <td className="py-3">{position.quantity}</td>
                      <td className="py-3">{formatCurrency(position.entry_price)}</td>
                      <td className="py-3">{formatCurrency(currentPrice)}</td>
                      <td className={`py-3 ${pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {formatCurrency(pnl)}
                      </td>
                      <td className={`py-3 ${pnl >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {formatPercent(pnlPercent)}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {positions.length === 0 && (
              <div className="text-center py-8 text-gray-500">No open positions</div>
            )}
          </div>
        </div>

        {/* Trading Panel */}
        <TradingPanel 
          onTrade={(tradeData) => {
            // Refresh portfolio and trades data after a trade
            fetchPortfolio();
            fetchTrades();
          }}
        />
      </div>

      {/* Recent Trades */}
      <div className="mt-6 bg-gray-800 rounded-lg p-6">
        <h2 className="text-xl font-bold mb-4">Recent Trades</h2>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-gray-400 border-b border-gray-700">
                <th className="pb-2">Time</th>
                <th className="pb-2">Symbol</th>
                <th className="pb-2">Action</th>
                <th className="pb-2">Quantity</th>
                <th className="pb-2">Price</th>
                <th className="pb-2">Total</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, index) => (
                <tr key={index} className="border-b border-gray-700">
                  <td className="py-3 text-sm text-gray-400">
                    {new Date(trade.timestamp).toLocaleString()}
                  </td>
                  <td className="py-3 font-semibold">{trade.ticker}</td>
                  <td className="py-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      trade.action === 'BUY' ? 'bg-green-500/20 text-green-500' : 'bg-red-500/20 text-red-500'
                    }`}>
                      {trade.action}
                    </span>
                  </td>
                  <td className="py-3">{trade.quantity}</td>
                  <td className="py-3">{formatCurrency(trade.price)}</td>
                  <td className="py-3">{formatCurrency(trade.quantity * trade.price)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {trades.length === 0 && (
            <div className="text-center py-8 text-gray-500">No recent trades</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;