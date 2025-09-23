import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, ArrowUp, ArrowDown, MoreHorizontal, Bell, Settings, Search, Filter, RefreshCw } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Candlestick } from 'recharts';

const BloombergDashboard = () => {
  const [currentTime, setCurrentTime] = useState(new Date());
  const [selectedTimeframe, setSelectedTimeframe] = useState('1D');
  const [selectedBot, setSelectedBot] = useState('ALL');

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Bloomberg-style market data
  const marketData = {
    indices: [
      { symbol: 'SPX', name: 'S&P 500', price: 4456.75, change: 12.34, changePercent: 0.28, volume: '1.2B' },
      { symbol: 'IXIC', name: 'NASDAQ', price: 13845.12, change: -23.45, changePercent: -0.17, volume: '2.1B' },
      { symbol: 'DJI', name: 'DOW JONES', price: 34567.89, change: 45.67, changePercent: 0.13, volume: '890M' },
      { symbol: 'VIX', name: 'VOLATILITY', price: 18.45, change: -1.23, changePercent: -6.25, volume: '456M' }
    ],
    portfolio: {
      totalValue: 224432.53,
      dailyPnL: 2145.87,
      totalPnL: 24432.53,
      totalReturn: 12.22,
      sharpe: 1.89,
      beta: 0.98,
      var: -8942.12,
      maxDrawdown: -2.34
    }
  };

  // Trading positions data with Bloomberg-style formatting
  const positions = [
    { symbol: 'AAPL', side: 'LONG', qty: 93, avgPrice: 226.87, lastPrice: 234.50, mktValue: 21808.50, unrealizedPnL: 709.59, unrealizedPct: 3.13, dayPnL: 186.00, beta: 1.25, duration: '4D', sector: 'TECH' },
    { symbol: 'MSFT', side: 'LONG', qty: 34, avgPrice: 500.62, lastPrice: 515.20, mktValue: 17516.80, unrealizedPnL: 495.72, unrealizedPct: 2.91, dayPnL: 136.00, beta: 0.89, duration: '4D', sector: 'TECH' },
    { symbol: 'GOOGL', side: 'LONG', qty: 24, avgPrice: 237.86, lastPrice: 241.15, mktValue: 5787.60, unrealizedPnL: 78.96, unrealizedPct: 1.38, dayPnL: 24.00, beta: 1.05, duration: '4D', sector: 'TECH' },
    { symbol: 'NVDA', side: 'LONG', qty: 405, avgPrice: 176.02, lastPrice: 182.45, mktValue: 73892.25, unrealizedPnL: 2604.15, unrealizedPct: 3.65, dayPnL: 810.00, beta: 1.65, duration: '4D', sector: 'TECH' },
    { symbol: 'JPM', side: 'LONG', qty: 71, avgPrice: 299.23, lastPrice: 308.75, mktValue: 21921.25, unrealizedPnL: 676.92, unrealizedPct: 3.18, dayPnL: 142.00, beta: 1.18, duration: '4D', sector: 'FIN' },
    { symbol: 'PG', side: 'LONG', qty: 39, avgPrice: 155.20, lastPrice: 158.90, mktValue: 6197.10, unrealizedPnL: 144.30, unrealizedPct: 2.38, dayPnL: 39.00, beta: 0.31, duration: '1D', sector: 'STAPLES' },
    { symbol: 'JNJ', side: 'LONG', qty: 37, avgPrice: 162.45, lastPrice: 165.80, mktValue: 6134.60, unrealizedPnL: 123.95, unrealizedPct: 2.06, dayPnL: 37.00, beta: 0.42, duration: '1D', sector: 'HEALTH' },
    { symbol: 'KO', side: 'LONG', qty: 104, avgPrice: 58.90, lastPrice: 60.25, mktValue: 6266.00, unrealizedPnL: 140.40, unrealizedPct: 2.29, dayPnL: 52.00, beta: 0.53, duration: '1D', sector: 'STAPLES' },
    { symbol: 'ORCL', side: 'LONG', qty: 42, avgPrice: 239.04, lastPrice: 295.80, mktValue: 12423.60, unrealizedPnL: 2383.92, unrealizedPct: 23.74, dayPnL: 168.00, beta: 0.78, duration: '6D', sector: 'TECH' },
    { symbol: 'RGTI', side: 'LONG', qty: 130, avgPrice: 15.35, lastPrice: 21.45, mktValue: 2788.50, unrealizedPnL: 793.00, unrealizedPct: 39.74, dayPnL: 130.00, beta: 1.89, duration: '6D', sector: 'TECH' },
    { symbol: 'MFIC', side: 'LONG', qty: 770, avgPrice: 12.16, lastPrice: 13.89, mktValue: 10695.30, unrealizedPnL: 1332.10, unrealizedPct: 14.22, dayPnL: 231.00, beta: 1.45, duration: '1D', sector: 'FIN' },
    { symbol: 'INCY', side: 'LONG', qty: 61, avgPrice: 83.97, lastPrice: 87.50, mktValue: 5337.50, unrealizedPnL: 215.33, unrealizedPct: 4.20, dayPnL: 61.00, beta: 0.89, duration: '1D', sector: 'BIOTECH' }
  ];

  // Chart data for different timeframes
  const chartData = {
    '1D': [
      { time: '09:30', value: 222456, volume: 1200 },
      { time: '10:00', value: 223123, volume: 1350 },
      { time: '10:30', value: 222987, volume: 1100 },
      { time: '11:00', value: 223456, volume: 1450 },
      { time: '11:30', value: 223789, volume: 1300 },
      { time: '12:00', value: 224123, volume: 1200 },
      { time: '12:30', value: 224234, volume: 1100 },
      { time: '13:00', value: 224432, volume: 1250 }
    ],
    '5D': [
      { time: 'Mon', value: 218456, volume: 12000 },
      { time: 'Tue', value: 220123, volume: 13500 },
      { time: 'Wed', value: 221789, volume: 11000 },
      { time: 'Thu', value: 223456, volume: 14500 },
      { time: 'Fri', value: 224432, volume: 13000 }
    ],
    '1M': [
      { time: 'W1', value: 206000, volume: 52000 },
      { time: 'W2', value: 212000, volume: 48000 },
      { time: 'W3', value: 218000, volume: 55000 },
      { time: 'W4', value: 224432, volume: 51000 }
    ]
  };

  const formatCurrency = (value, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  const formatNumber = (value, decimals = 2) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals
    }).format(value);
  };

  const getChangeColor = (value) => {
    if (value > 0) return 'text-green-400';
    if (value < 0) return 'text-red-400';
    return 'text-gray-300';
  };

  const getChangeBg = (value) => {
    if (value > 0) return 'bg-green-900/30';
    if (value < 0) return 'bg-red-900/30';
    return 'bg-gray-900/30';
  };

  return (
    <div className="min-h-screen bg-black text-white font-mono text-sm">
      {/* Bloomberg-style Header */}
      <div className="bg-orange-500 text-black px-4 py-2 flex items-center justify-between">
        <div className="flex items-center space-x-6">
          <div className="text-lg font-bold">BLOOMBERG TERMINAL</div>
          <div className="text-sm">AI TRADING SYSTEM</div>
          <div className="text-sm">{currentTime.toLocaleString()}</div>
        </div>
        <div className="flex items-center space-x-4">
          <Search className="h-4 w-4" />
          <Bell className="h-4 w-4" />
          <Settings className="h-4 w-4" />
        </div>
      </div>

      {/* Market Data Bar */}
      <div className="bg-gray-900 px-4 py-2 border-b border-gray-700">
        <div className="flex items-center justify-between text-xs">
          {marketData.indices.map((index) => (
            <div key={index.symbol} className="flex items-center space-x-2">
              <span className="text-orange-400 font-bold">{index.symbol}</span>
              <span className="text-white">{formatNumber(index.price)}</span>
              <span className={`${getChangeColor(index.change)} flex items-center`}>
                {index.change > 0 ? <ArrowUp className="h-3 w-3 mr-1" /> : <ArrowDown className="h-3 w-3 mr-1" />}
                {formatNumber(Math.abs(index.change))} ({formatNumber(Math.abs(index.changePercent))}%)
              </span>
              <span className="text-gray-400">VOL {index.volume}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="flex h-screen">
        {/* Left Panel - Portfolio Overview */}
        <div className="w-80 bg-gray-900 border-r border-gray-700 p-4">
          <div className="mb-4">
            <h2 className="text-orange-400 font-bold mb-2">PORTFOLIO SUMMARY</h2>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">TOTAL NAV</span>
                <span className="text-white font-bold">{formatCurrency(marketData.portfolio.totalValue, 0)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">DAY P&L</span>
                <span className={getChangeColor(marketData.portfolio.dailyPnL)}>
                  {marketData.portfolio.dailyPnL > 0 ? '+' : ''}{formatCurrency(marketData.portfolio.dailyPnL)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">TOTAL P&L</span>
                <span className={getChangeColor(marketData.portfolio.totalPnL)}>
                  {marketData.portfolio.totalPnL > 0 ? '+' : ''}{formatCurrency(marketData.portfolio.totalPnL)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">TOTAL RTN</span>
                <span className="text-green-400">+{formatNumber(marketData.portfolio.totalReturn)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">SHARPE</span>
                <span className="text-white">{formatNumber(marketData.portfolio.sharpe)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">BETA</span>
                <span className="text-white">{formatNumber(marketData.portfolio.beta)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">VAR (95%)</span>
                <span className="text-red-400">{formatCurrency(marketData.portfolio.var)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">MAX DD</span>
                <span className="text-red-400">{formatNumber(marketData.portfolio.maxDrawdown)}%</span>
              </div>
            </div>
          </div>

          {/* Bot Status */}
          <div className="mb-4">
            <h3 className="text-orange-400 font-bold mb-2">TRADING BOTS</h3>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between items-center">
                <span className="text-gray-400">DEE-BOT</span>
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">ACTIVE</span>
                  <span className="text-white">$120.9K</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-400">SHORGAN-BOT</span>
                <div className="flex items-center space-x-2">
                  <span className="text-green-400">ACTIVE</span>
                  <span className="text-white">$103.6K</span>
                </div>
              </div>
            </div>
          </div>

          {/* Risk Monitors */}
          <div>
            <h3 className="text-orange-400 font-bold mb-2">RISK MONITORS</h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">EXPOSURE</span>
                <span className="text-yellow-400">185%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">LEVERAGE</span>
                <span className="text-yellow-400">1.85X</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">MARGIN</span>
                <span className="text-green-400">45%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">CONCENTRATION</span>
                <span className="text-yellow-400">WARN</span>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="flex-1 flex flex-col">
          {/* Chart Section */}
          <div className="h-80 bg-black border-b border-gray-700 p-4">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-4">
                <h3 className="text-orange-400 font-bold">PORTFOLIO PERFORMANCE</h3>
                <div className="flex space-x-1">
                  {['1D', '5D', '1M', '3M', '1Y'].map((timeframe) => (
                    <button
                      key={timeframe}
                      onClick={() => setSelectedTimeframe(timeframe)}
                      className={`px-2 py-1 text-xs ${
                        selectedTimeframe === timeframe
                          ? 'bg-orange-500 text-black'
                          : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                      }`}
                    >
                      {timeframe}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex items-center space-x-4 text-xs">
                <span className="text-gray-400">LAST: <span className="text-white">{formatCurrency(224432.53, 0)}</span></span>
                <span className={`${getChangeColor(2145.87)}`}>
                  {2145.87 > 0 ? '+' : ''}{formatCurrency(2145.87)} (+0.97%)
                </span>
                <RefreshCw className="h-4 w-4 text-gray-400" />
              </div>
            </div>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData[selectedTimeframe] || chartData['1D']}>
                <CartesianGrid strokeDasharray="1 1" stroke="#374151" opacity={0.3} />
                <XAxis 
                  dataKey="time" 
                  stroke="#9CA3AF" 
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis 
                  stroke="#9CA3AF" 
                  fontSize={10}
                  tickLine={false}
                  axisLine={false}
                  domain={['dataMin - 1000', 'dataMax + 1000']}
                />
                <Tooltip 
                  contentStyle={{
                    backgroundColor: '#1F2937',
                    border: '1px solid #374151',
                    borderRadius: 0,
                    fontSize: '10px'
                  }}
                />
                <Line 
                  type="monotone" 
                  dataKey="value" 
                  stroke="#F59E0B" 
                  strokeWidth={1}
                  dot={false}
                  activeDot={{ r: 2, stroke: '#F59E0B', strokeWidth: 1, fill: '#000' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>

          {/* Positions Table */}
          <div className="flex-1 bg-black p-4 overflow-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-orange-400 font-bold">POSITIONS</h3>
              <div className="flex items-center space-x-2">
                <Filter className="h-4 w-4 text-gray-400" />
                <select 
                  className="bg-gray-900 text-white text-xs border border-gray-700 px-2 py-1"
                  value={selectedBot}
                  onChange={(e) => setSelectedBot(e.target.value)}
                >
                  <option value="ALL">ALL BOTS</option>
                  <option value="DEE">DEE-BOT</option>
                  <option value="SHORGAN">SHORGAN-BOT</option>
                </select>
              </div>
            </div>

            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-gray-700 text-orange-400">
                  <th className="text-left py-2">SYMBOL</th>
                  <th className="text-left py-2">SIDE</th>
                  <th className="text-right py-2">QTY</th>
                  <th className="text-right py-2">AVG PX</th>
                  <th className="text-right py-2">LAST PX</th>
                  <th className="text-right py-2">MKT VAL</th>
                  <th className="text-right py-2">UNREAL P&L</th>
                  <th className="text-right py-2">UNREAL %</th>
                  <th className="text-right py-2">DAY P&L</th>
                  <th className="text-right py-2">BETA</th>
                  <th className="text-right py-2">DUR</th>
                  <th className="text-left py-2">SECTOR</th>
                </tr>
              </thead>
              <tbody>
                {positions.map((position) => (
                  <tr key={position.symbol} className="border-b border-gray-800 hover:bg-gray-900/50">
                    <td className="py-2 text-white font-bold">{position.symbol}</td>
                    <td className="py-2">
                      <span className={`px-1 py-0.5 text-xs ${
                        position.side === 'LONG' ? 'bg-blue-900/30 text-blue-400' : 'bg-red-900/30 text-red-400'
                      }`}>
                        {position.side}
                      </span>
                    </td>
                    <td className="py-2 text-right text-white">{position.qty.toLocaleString()}</td>
                    <td className="py-2 text-right text-gray-300">{formatNumber(position.avgPrice)}</td>
                    <td className="py-2 text-right text-white font-bold">{formatNumber(position.lastPrice)}</td>
                    <td className="py-2 text-right text-white">{formatCurrency(position.mktValue, 0)}</td>
                    <td className={`py-2 text-right ${getChangeColor(position.unrealizedPnL)}`}>
                      {position.unrealizedPnL > 0 ? '+' : ''}{formatCurrency(position.unrealizedPnL, 0)}
                    </td>
                    <td className={`py-2 text-right ${getChangeColor(position.unrealizedPnL)}`}>
                      {position.unrealizedPnL > 0 ? '+' : ''}{formatNumber(position.unrealizedPct)}%
                    </td>
                    <td className={`py-2 text-right ${getChangeColor(position.dayPnL)}`}>
                      {position.dayPnL > 0 ? '+' : ''}{formatCurrency(position.dayPnL, 0)}
                    </td>
                    <td className="py-2 text-right text-gray-300">{formatNumber(position.beta)}</td>
                    <td className="py-2 text-right text-gray-400">{position.duration}</td>
                    <td className="py-2 text-left">
                      <span className="px-1 py-0.5 bg-gray-800 text-gray-400 text-xs">
                        {position.sector}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Right Panel - News & Alerts */}
        <div className="w-80 bg-gray-900 border-l border-gray-700 p-4">
          <div className="mb-4">
            <h3 className="text-orange-400 font-bold mb-2">MARKET NEWS</h3>
            <div className="space-y-2 text-xs">
              <div className="border-b border-gray-800 pb-2">
                <div className="text-white font-bold">NVDA +2.1%</div>
                <div className="text-gray-400">Strong AI chip demand drives gains</div>
                <div className="text-gray-500">2m ago</div>
              </div>
              <div className="border-b border-gray-800 pb-2">
                <div className="text-white font-bold">Fed Minutes</div>
                <div className="text-gray-400">Dovish tone supports equity markets</div>
                <div className="text-gray-500">15m ago</div>
              </div>
              <div className="border-b border-gray-800 pb-2">
                <div className="text-white font-bold">AAPL Earnings</div>
                <div className="text-gray-400">iPhone 15 sales exceed expectations</div>
                <div className="text-gray-500">1h ago</div>
              </div>
            </div>
          </div>

          <div className="mb-4">
            <h3 className="text-orange-400 font-bold mb-2">SYSTEM ALERTS</h3>
            <div className="space-y-2 text-xs">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                <span className="text-yellow-400">High concentration risk in TECH</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <span className="text-green-400">DEE-BOT beta rebalanced to 1.0</span>
              </div>
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <span className="text-blue-400">SHORGAN-BOT 4 new catalysts identified</span>
              </div>
            </div>
          </div>

          <div>
            <h3 className="text-orange-400 font-bold mb-2">AGENT STATUS</h3>
            <div className="space-y-1 text-xs">
              <div className="flex justify-between">
                <span className="text-gray-400">Fundamental</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Technical</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">News</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Sentiment</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-400">Risk Manager</span>
                <span className="text-green-400">ACTIVE</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BloombergDashboard;