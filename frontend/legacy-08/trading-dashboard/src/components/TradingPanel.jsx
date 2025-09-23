import React, { useState } from 'react';
import { TrendingUp, TrendingDown, AlertCircle, DollarSign } from 'lucide-react';

const TradingPanel = ({ onTrade }) => {
  const [symbol, setSymbol] = useState('');
  const [quantity, setQuantity] = useState('');
  const [orderType, setOrderType] = useState('MARKET');
  const [action, setAction] = useState('BUY');
  const [limitPrice, setLimitPrice] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!symbol || !quantity) {
      setMessage({ type: 'error', text: 'Please enter symbol and quantity' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const orderData = {
        symbol: symbol.toUpperCase(),
        action,
        quantity: parseInt(quantity),
        order_type: orderType,
        ...(orderType === 'LIMIT' && { limit_price: parseFloat(limitPrice) })
      };

      const response = await fetch('http://localhost:8000/api/trade/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(orderData),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({ 
          type: 'success', 
          text: `Order executed: ${action} ${quantity} ${symbol} @ $${data.price || 'MARKET'}` 
        });
        
        // Clear form
        setSymbol('');
        setQuantity('');
        setLimitPrice('');
        
        // Notify parent component
        if (onTrade) {
          onTrade(data);
        }
      } else {
        setMessage({ 
          type: 'error', 
          text: data.error || 'Failed to execute order' 
        });
      }
    } catch (error) {
      setMessage({ 
        type: 'error', 
        text: 'Failed to connect to trading server' 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4 flex items-center">
        <DollarSign className="mr-2" />
        Trade Execution
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Symbol Input */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Symbol
          </label>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            placeholder="AAPL"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>

        {/* Action Buttons */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Action
          </label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setAction('BUY')}
              className={`py-2 px-4 rounded-md font-medium transition-colors ${
                action === 'BUY'
                  ? 'bg-green-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={loading}
            >
              <TrendingUp className="inline mr-1" size={16} />
              Buy
            </button>
            <button
              type="button"
              onClick={() => setAction('SELL')}
              className={`py-2 px-4 rounded-md font-medium transition-colors ${
                action === 'SELL'
                  ? 'bg-red-500 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
              disabled={loading}
            >
              <TrendingDown className="inline mr-1" size={16} />
              Sell
            </button>
          </div>
        </div>

        {/* Quantity */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Quantity
          </label>
          <input
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(e.target.value)}
            placeholder="100"
            min="1"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          />
        </div>

        {/* Order Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Order Type
          </label>
          <select
            value={orderType}
            onChange={(e) => setOrderType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={loading}
          >
            <option value="MARKET">Market</option>
            <option value="LIMIT">Limit</option>
          </select>
        </div>

        {/* Limit Price (conditional) */}
        {orderType === 'LIMIT' && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Limit Price
            </label>
            <input
              type="number"
              value={limitPrice}
              onChange={(e) => setLimitPrice(e.target.value)}
              placeholder="150.00"
              step="0.01"
              min="0.01"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={loading}
              required
            />
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-2 px-4 rounded-md font-medium text-white transition-colors ${
            loading
              ? 'bg-gray-400 cursor-not-allowed'
              : action === 'BUY'
              ? 'bg-green-500 hover:bg-green-600'
              : 'bg-red-500 hover:bg-red-600'
          }`}
        >
          {loading ? 'Processing...' : `${action} ${symbol || 'Stock'}`}
        </button>
      </form>

      {/* Message Display */}
      {message && (
        <div
          className={`mt-4 p-3 rounded-md flex items-start ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800'
              : 'bg-red-50 text-red-800'
          }`}
        >
          <AlertCircle className="mr-2 mt-0.5" size={16} />
          <span className="text-sm">{message.text}</span>
        </div>
      )}

      {/* Demo Mode Notice */}
      <div className="mt-4 p-3 bg-blue-50 rounded-md">
        <p className="text-sm text-blue-800">
          <strong>Demo Mode:</strong> Using mock broker for demonstration. 
          Configure Alpaca API keys for real paper trading.
        </p>
      </div>
    </div>
  );
};

export default TradingPanel;