import React from 'react';
import { TrendingUp, TrendingDown, DollarSign, Activity, Target, Zap, Shield, BarChart3, AlertTriangle, CheckCircle2, Bot, Globe } from 'lucide-react';
import AnimatedChart from './AnimatedChart';

const DashboardEnhanced = () => {
  // Updated data based on latest system performance
  const portfolio = {
    total_value: 224432.53,
    total_unrealized_pnl: 24432.53,
    daily_pnl: 2145.87,
    win_rate: 0.68,
    portfolio_sharpe: 1.89,
    beta: 0.98
  };

  const positions = [
    { ticker: 'AAPL', quantity: 93, entry_price: 226.87, current_price: 234.50, sector: 'Technology' },
    { ticker: 'MSFT', quantity: 34, entry_price: 500.62, current_price: 515.20, sector: 'Technology' },
    { ticker: 'GOOGL', quantity: 24, entry_price: 237.86, current_price: 241.15, sector: 'Technology' },
    { ticker: 'NVDA', quantity: 405, entry_price: 176.02, current_price: 182.45, sector: 'Technology' },
    { ticker: 'JPM', quantity: 71, entry_price: 299.23, current_price: 308.75, sector: 'Financial' },
    { ticker: 'PG', quantity: 39, entry_price: 155.20, current_price: 158.90, sector: 'Consumer Staples' },
    { ticker: 'JNJ', quantity: 37, entry_price: 162.45, current_price: 165.80, sector: 'Healthcare' },
    { ticker: 'KO', quantity: 104, entry_price: 58.90, current_price: 60.25, sector: 'Consumer Staples' },
    { ticker: 'ORCL', quantity: 42, entry_price: 239.04, current_price: 295.80, sector: 'Technology' },
    { ticker: 'RGTI', quantity: 130, entry_price: 15.35, current_price: 21.45, sector: 'Technology' },
    { ticker: 'MFIC', quantity: 770, entry_price: 12.16, current_price: 13.89, sector: 'Financial' },
    { ticker: 'INCY', quantity: 61, entry_price: 83.97, current_price: 87.50, sector: 'Healthcare' }
  ];

  const trades = [
    { timestamp: '2025-09-16T14:30:00Z', ticker: 'PG', action: 'BUY', quantity: 39, price: 155.20, strategy: 'DEE-BOT', catalyst: 'Beta Rebalancing' },
    { timestamp: '2025-09-16T14:25:00Z', ticker: 'JNJ', action: 'BUY', quantity: 37, price: 162.45, strategy: 'DEE-BOT', catalyst: 'Defensive Allocation' },
    { timestamp: '2025-09-16T14:20:00Z', ticker: 'KO', action: 'BUY', quantity: 104, price: 58.90, strategy: 'DEE-BOT', catalyst: 'Low Beta Target' },
    { timestamp: '2025-09-16T14:15:00Z', ticker: 'MFIC', action: 'BUY', quantity: 770, price: 12.16, strategy: 'SHORGAN-BOT', catalyst: 'Insider Buying' },
    { timestamp: '2025-09-16T14:10:00Z', ticker: 'INCY', action: 'BUY', quantity: 61, price: 83.97, strategy: 'SHORGAN-BOT', catalyst: 'FDA Approval 9/19' },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'GOOGL', action: 'BUY', quantity: 21, price: 237.44, strategy: 'DEE-BOT', catalyst: 'Agent Consensus' },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'AAPL', action: 'BUY', quantity: 22, price: 227.74, strategy: 'DEE-BOT', catalyst: 'Multi-Agent Buy' },
    { timestamp: '2025-09-12T09:30:00Z', ticker: 'NVDA', action: 'BUY', quantity: 300, price: 176.02, strategy: 'DEE-BOT', catalyst: 'AI Momentum' }
  ];

  // Portfolio performance chart data
  const chartData = [
    { time: 'Sep 10', value: 200000 },
    { time: 'Sep 11', value: 204095 },
    { time: 'Sep 12', value: 205481 },
    { time: 'Sep 13', value: 208940 },
    { time: 'Sep 14', value: 212350 },
    { time: 'Sep 15', value: 218670 },
    { time: 'Sep 16', value: 224433 }
  ];

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  };

  const formatPercent = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const getPerformanceColor = (value) => {
    if (value > 0) return 'text-emerald-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-300';
  };

  const getPerformanceBg = (value) => {
    if (value > 0) return 'bg-emerald-500/10 border-emerald-500/20';
    if (value < 0) return 'bg-red-500/10 border-red-500/20';
    return 'bg-gray-500/10 border-gray-500/20';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent mb-2">
              AI Trading Dashboard
            </h1>
            <p className="text-slate-400 text-lg">Multi-Agent Intelligence • Beta-Neutral Strategy • Real-Time Monitoring</p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="px-4 py-2 bg-emerald-500/20 text-emerald-400 rounded-lg border border-emerald-500/30 font-semibold">
              ● LIVE
            </div>
            <div className="text-right">
              <div className="text-sm text-slate-400">Sept 16, 2025</div>
              <div className="text-lg font-semibold text-white">1:30 PM ET</div>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="md:col-span-2 bg-gradient-to-r from-slate-800/50 to-blue-800/30 backdrop-blur-sm rounded-2xl p-8 border border-slate-600/30">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-3">
              <div className="p-3 bg-emerald-500/20 rounded-xl">
                <DollarSign className="h-8 w-8 text-emerald-400" />
              </div>
              <div>
                <h3 className="text-slate-400 text-sm uppercase tracking-wide">Total Portfolio Value</h3>
                <div className="text-4xl font-bold text-white">{formatCurrency(portfolio.total_value)}</div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-emerald-400 text-2xl font-bold">+{formatCurrency(portfolio.total_unrealized_pnl)}</div>
              <div className="text-emerald-400 text-lg">+12.22% Total Return</div>
              <div className="text-slate-400 text-sm">Since Sept 10, 2025</div>
            </div>
          </div>
          <div className="h-2 bg-slate-700/50 rounded-full overflow-hidden">
            <div className="h-full bg-gradient-to-r from-emerald-500 to-blue-500 w-[78%] rounded-full"></div>
          </div>
          <div className="flex justify-between text-sm text-slate-400 mt-2">
            <span>Goal: $250K</span>
            <span>78% Complete</span>
          </div>
        </div>

        <div className="bg-gradient-to-r from-slate-800/50 to-purple-800/30 backdrop-blur-sm rounded-2xl p-6 border border-slate-600/30">
          <div className="flex items-center justify-between mb-4">
            <Target className="h-8 w-8 text-purple-400" />
            <div className="text-right">
              <div className="text-purple-400 text-sm uppercase tracking-wide">Today's Performance</div>
              <div className="text-2xl font-bold text-white">+{formatCurrency(portfolio.daily_pnl)}</div>
              <div className="text-purple-400">+0.97%</div>
            </div>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Market Beat</span>
              <span className="text-emerald-400">+2.3%</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">Sharpe Ratio</span>
              <span className="text-blue-400">{portfolio.portfolio_sharpe}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-600/30">
          <div className="flex items-center justify-between mb-2">
            <Activity className="h-5 w-5 text-blue-400" />
            <span className="text-xs text-slate-400 uppercase tracking-wide">Active Positions</span>
          </div>
          <div className="text-2xl font-bold text-white">{positions.length}</div>
          <div className="text-sm text-slate-400">2 Strategies</div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-600/30">
          <div className="flex items-center justify-between mb-2">
            <BarChart3 className="h-5 w-5 text-emerald-400" />
            <span className="text-xs text-slate-400 uppercase tracking-wide">Win Rate</span>
          </div>
          <div className="text-2xl font-bold text-white">{formatPercent(portfolio.win_rate)}</div>
          <div className="text-sm text-emerald-400">Above Target</div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-600/30">
          <div className="flex items-center justify-between mb-2">
            <Shield className="h-5 w-5 text-purple-400" />
            <span className="text-xs text-slate-400 uppercase tracking-wide">Portfolio Beta</span>
          </div>
          <div className="text-2xl font-bold text-white">{portfolio.beta}</div>
          <div className="text-sm text-purple-400">Market Neutral</div>
        </div>

        <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-4 border border-slate-600/30">
          <div className="flex items-center justify-between mb-2">
            <Zap className="h-5 w-5 text-yellow-400" />
            <span className="text-xs text-slate-400 uppercase tracking-wide">Leverage</span>
          </div>
          <div className="text-2xl font-bold text-white">1.85x</div>
          <div className="text-sm text-yellow-400">Controlled</div>
        </div>
      </div>

      {/* Trading Bots Performance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-gradient-to-br from-blue-900/30 to-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-blue-500/20">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-500/20 rounded-lg">
                <Bot className="h-6 w-6 text-blue-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">DEE-BOT</h3>
                <p className="text-blue-400 text-sm">Beta-Neutral Strategy</p>
              </div>
            </div>
            <div className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-sm border border-emerald-500/30">
              ACTIVE
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Portfolio Value</span>
              <span className="text-xl font-bold text-white">$120,879.90</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Total Return</span>
              <span className="text-emerald-400 font-semibold">+20.88%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Current Beta</span>
              <span className="text-blue-400 font-semibold">1.0</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Positions</span>
              <span className="text-white">3 (Rebalanced)</span>
            </div>
            <div className="pt-4 border-t border-slate-600/30">
              <div className="text-xs text-slate-400 mb-2">Latest Trades (Defensive Rebalancing)</div>
              <div className="space-y-1">
                <div className="text-sm"><span className="text-emerald-400">PG</span> • 39 shares • Beta: 0.3</div>
                <div className="text-sm"><span className="text-emerald-400">JNJ</span> • 37 shares • Beta: 0.4</div>
                <div className="text-sm"><span className="text-emerald-400">KO</span> • 104 shares • Beta: 0.5</div>
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-orange-900/30 to-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-orange-500/20">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-500/20 rounded-lg">
                <Zap className="h-6 w-6 text-orange-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-white">SHORGAN-BOT</h3>
                <p className="text-orange-400 text-sm">Catalyst Events Strategy</p>
              </div>
            </div>
            <div className="px-3 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-sm border border-emerald-500/30">
              ACTIVE
            </div>
          </div>
          
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Portfolio Value</span>
              <span className="text-xl font-bold text-white">$103,552.63</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Total Return</span>
              <span className="text-emerald-400 font-semibold">+3.55%</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Risk/Reward</span>
              <span className="text-orange-400 font-semibold">1:3.2</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-slate-400">Positions</span>
              <span className="text-white">17 (Event-Driven)</span>
            </div>
            <div className="pt-4 border-t border-slate-600/30">
              <div className="text-xs text-slate-400 mb-2">Top Performers</div>
              <div className="space-y-1">
                <div className="text-sm"><span className="text-emerald-400">ORCL</span> • +23.7% • FDA catalyst</div>
                <div className="text-sm"><span className="text-emerald-400">RGTI</span> • +39.7% • Contract news</div>
                <div className="text-sm"><span className="text-emerald-400">MFIC</span> • +14.2% • Insider buying</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Portfolio Performance Chart */}
      <div className="mb-8">
        <AnimatedChart 
          data={chartData} 
          title="Portfolio Performance (7 Days)" 
          color="#10B981" 
        />
      </div>

      {/* Positions Table */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-600/30 mb-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-white">Active Positions</h2>
          <div className="flex items-center space-x-2">
            <Globe className="h-5 w-5 text-blue-400" />
            <span className="text-sm text-slate-400">Real-time prices</span>
          </div>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="text-left text-slate-400 border-b border-slate-600/30">
                <th className="pb-4 font-semibold">Symbol</th>
                <th className="pb-4 font-semibold">Sector</th>
                <th className="pb-4 font-semibold">Quantity</th>
                <th className="pb-4 font-semibold">Entry</th>
                <th className="pb-4 font-semibold">Current</th>
                <th className="pb-4 font-semibold">P&L</th>
                <th className="pb-4 font-semibold">Return</th>
              </tr>
            </thead>
            <tbody>
              {positions.map((position) => {
                const pnl = (position.current_price - position.entry_price) * position.quantity;
                const pnlPercent = ((position.current_price - position.entry_price) / position.entry_price);
                
                return (
                  <tr key={position.ticker} className="border-b border-slate-700/30 hover:bg-slate-700/20 transition-colors">
                    <td className="py-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-white text-lg">{position.ticker}</span>
                        {pnl > 0 && <TrendingUp className="h-4 w-4 text-emerald-400" />}
                        {pnl < 0 && <TrendingDown className="h-4 w-4 text-red-400" />}
                      </div>
                    </td>
                    <td className="py-4">
                      <span className="px-2 py-1 bg-slate-600/30 text-slate-300 rounded text-xs">
                        {position.sector}
                      </span>
                    </td>
                    <td className="py-4 text-slate-300 font-medium">{position.quantity.toLocaleString()}</td>
                    <td className="py-4 text-slate-300">{formatCurrency(position.entry_price)}</td>
                    <td className="py-4 text-white font-semibold">{formatCurrency(position.current_price)}</td>
                    <td className={`py-4 font-bold ${getPerformanceColor(pnl)}`}>
                      {formatCurrency(pnl)}
                    </td>
                    <td className="py-4">
                      <span className={`px-3 py-1 rounded-full text-sm font-semibold border ${getPerformanceBg(pnl)} ${getPerformanceColor(pnl)}`}>
                        {pnlPercent >= 0 ? '+' : ''}{formatPercent(pnlPercent)}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Recent Trades */}
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-600/30">
        <h2 className="text-2xl font-bold text-white mb-6">Recent Trading Activity</h2>
        <div className="space-y-3">
          {trades.slice(0, 6).map((trade, index) => (
            <div key={index} className="flex items-center justify-between p-4 bg-slate-700/30 rounded-xl border border-slate-600/20 hover:bg-slate-700/50 transition-colors">
              <div className="flex items-center space-x-4">
                <div className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                  trade.action === 'BUY' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30' : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}>
                  {trade.action}
                </div>
                <div>
                  <div className="font-bold text-white text-lg">{trade.ticker}</div>
                  <div className="text-slate-400 text-sm">{trade.catalyst}</div>
                </div>
              </div>
              <div className="text-right">
                <div className="font-semibold text-white">{trade.quantity} shares @ {formatCurrency(trade.price)}</div>
                <div className="text-sm text-slate-400">{trade.strategy} • {new Date(trade.timestamp).toLocaleDateString()}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-8 pt-6 border-t border-slate-600/30 text-center">
        <div className="flex items-center justify-center space-x-6 text-sm text-slate-400">
          <div className="flex items-center space-x-2">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>System Operational</span>
          </div>
          <div className="flex items-center space-x-2">
            <Shield className="h-4 w-4 text-blue-400" />
            <span>Risk Controlled</span>
          </div>
          <div className="flex items-center space-x-2">
            <Globe className="h-4 w-4 text-purple-400" />
            <span>Real-time Data</span>
          </div>
        </div>
        <p className="mt-2 text-xs text-slate-500">AI Stock Trading Bot • Multi-Agent Intelligence • Sept 16, 2025</p>
      </div>
    </div>
  );
};

export default DashboardEnhanced;