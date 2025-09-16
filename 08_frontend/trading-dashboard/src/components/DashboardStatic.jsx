import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity } from 'lucide-react';

const DashboardStatic = () => {
  // Static data based on current system performance
  const portfolio = {
    total_value: 206243.48,
    total_unrealized_pnl: 6243.48,
    win_rate: 0.62,
    portfolio_sharpe: 1.34
  };

  const positions = [
    { ticker: 'AAPL', quantity: 93, entry_price: 226.87, current_price: 234.00 },
    { ticker: 'MSFT', quantity: 34, entry_price: 500.62, current_price: 510.99 },
    { ticker: 'GOOGL', quantity: 24, entry_price: 237.86, current_price: 238.03 },
    { ticker: 'NVDA', quantity: 405, entry_price: 176.02, current_price: 178.18 },
    { ticker: 'JPM', quantity: 71, entry_price: 299.23, current_price: 305.39 },
    { ticker: 'ORCL', quantity: 42, entry_price: 239.04, current_price: 292.54 },
    { ticker: 'RGTI', quantity: 130, entry_price: 15.35, current_price: 19.03 },
    { ticker: 'MFIC', quantity: 770, entry_price: 12.16, current_price: 12.50 },
    { ticker: 'INCY', quantity: 61, entry_price: 83.97, current_price: 85.20 },
    { ticker: 'CBRL', quantity: 81, entry_price: 51.00, current_price: 52.10 }
  ];

  const trades = [
    { timestamp: '2025-09-16T14:30:00Z', ticker: 'MFIC', action: 'BUY', quantity: 770, price: 12.16 },
    { timestamp: '2025-09-16T14:25:00Z', ticker: 'INCY', action: 'BUY', quantity: 61, price: 83.97 },
    { timestamp: '2025-09-16T14:20:00Z', ticker: 'CBRL', action: 'BUY', quantity: 81, price: 51.00 },
    { timestamp: '2025-09-16T14:15:00Z', ticker: 'RIVN', action: 'BUY', quantity: 357, price: 14.50 },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'GOOGL', action: 'BUY', quantity: 21, price: 237.44 },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'AAPL', action: 'BUY', quantity: 22, price: 227.74 },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'HD', action: 'BUY', quantity: 12, price: 416.39 },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'CVX', action: 'BUY', quantity: 31, price: 157.87 }
  ];

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold mb-2">AI Trading Dashboard</h1>
        <p className="text-gray-400">Real-time portfolio monitoring and trading insights</p>
        <div className="mt-2 px-3 py-1 bg-green-500/20 text-green-500 rounded-full text-sm inline-block">
          ● Live - Sept 16, 2025
        </div>
      </div>

      {/* Portfolio Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Total Value</span>
            <DollarSign className="h-5 w-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold">
            {formatCurrency(portfolio.total_value)}
          </div>
          <div className="text-sm text-green-500 mt-1">+3.12% (+$6,243.48)</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Total P&L</span>
            <TrendingUp className="h-5 w-5 text-green-500" />
          </div>
          <div className="text-2xl font-bold text-green-500">
            {formatCurrency(portfolio.total_unrealized_pnl)}
          </div>
          <div className="text-sm text-gray-400 mt-1">Unrealized gains</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Active Positions</span>
            <Activity className="h-5 w-5 text-blue-500" />
          </div>
          <div className="text-2xl font-bold">
            {positions.length}
          </div>
          <div className="text-sm text-gray-400 mt-1">2 bots trading</div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-gray-400">Win Rate</span>
            <Activity className="h-5 w-5 text-purple-500" />
          </div>
          <div className="text-2xl font-bold">
            {formatPercent(portfolio.win_rate)}
          </div>
          <div className="text-sm text-gray-400 mt-1">Beta: 0.98</div>
        </div>
      </div>

      {/* Bot Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 text-blue-400">DEE-BOT (Conservative)</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Value:</span>
              <span className="font-semibold">$102,690.85</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Return:</span>
              <span className="text-green-500">+2.69%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Strategy:</span>
              <span className="text-sm">Beta-Neutral 2X</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Positions:</span>
              <span>8</span>
            </div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-bold mb-4 text-orange-400">SHORGAN-BOT (Aggressive)</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span className="text-gray-400">Value:</span>
              <span className="font-semibold">$103,552.63</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Return:</span>
              <span className="text-green-500">+3.55%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Strategy:</span>
              <span className="text-sm">Catalyst Events</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Positions:</span>
              <span>17</span>
            </div>
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
                  const pnl = (position.current_price - position.entry_price) * position.quantity;
                  const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price);
                  
                  return (
                    <tr key={position.ticker} className="border-b border-gray-700">
                      <td className="py-3 font-semibold">{position.ticker}</td>
                      <td className="py-3">{position.quantity}</td>
                      <td className="py-3">{formatCurrency(position.entry_price)}</td>
                      <td className="py-3">{formatCurrency(position.current_price)}</td>
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
          </div>
        </div>

        {/* System Status */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h2 className="text-xl font-bold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Market Status</span>
              <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-sm">OPEN</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">DEE-BOT</span>
              <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-sm">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">SHORGAN-BOT</span>
              <span className="px-2 py-1 bg-green-500/20 text-green-500 rounded text-sm">ACTIVE</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Risk Level</span>
              <span className="px-2 py-1 bg-yellow-500/20 text-yellow-500 rounded text-sm">CONTROLLED</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Leverage</span>
              <span className="text-sm">2.0x</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-400">Portfolio Beta</span>
              <span className="text-sm">0.98</span>
            </div>
          </div>
        </div>
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
        </div>
      </div>
    </div>
  );
};

export default DashboardStatic;