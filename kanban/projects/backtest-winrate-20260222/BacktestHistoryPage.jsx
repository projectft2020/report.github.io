import React, { useState, useEffect } from 'react';
import './BacktestHistoryPage.css';

function BacktestHistoryPage() {
  const [histories, setHistories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedHistories, setSelectedHistories] = useState([]);
  const [showComparison, setShowComparison] = useState(false);

  useEffect(() => {
    async function fetchHistories() {
      try {
        setLoading(true);
        const response = await fetch('/api/backtest/history?user_id=1');
        if (!response.ok) {
          throw new Error('Failed to fetch backtest history');
        }
        const data = await response.json();
        setHistories(data.histories);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchHistories();
  }, []);

  const formatWinRate = (winRate) => {
    if (winRate === null || winRate === undefined || isNaN(winRate)) {
      return 'N/A';
    }
    return `${winRate.toFixed(2)}%`;
  };

  const formatProfitFactor = (profitFactor) => {
    if (profitFactor === null || profitFactor === undefined || isNaN(profitFactor)) {
      return 'N/A';
    }
    if (profitFactor === Infinity || profitFactor === 'Infinity') {
      return '∞';
    }
    return profitFactor.toFixed(2);
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('zh-TW', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'status-completed';
      case 'running':
        return 'status-running';
      case 'failed':
        return 'status-failed';
      case 'pending':
        return 'status-pending';
      default:
        return 'status-unknown';
    }
  };

  const getStatusText = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return '已完成';
      case 'running':
        return '運行中';
      case 'failed':
        return '失敗';
      case 'pending':
        return '等待中';
      default:
        return status || '未知';
    }
  };

  const handleCompare = (historyId) => {
    if (selectedHistories.includes(historyId)) {
      setSelectedHistories(selectedHistories.filter(id => id !== historyId));
    } else {
      setSelectedHistories([...selectedHistories, historyId]);
    }
  };

  const handleViewDetails = async (historyId) => {
    try {
      const response = await fetch(`/api/backtest/history/${historyId}?user_id=1`);
      if (!response.ok) throw new Error('Failed to fetch details');
      const data = await response.json();
      alert(`回測詳情：\n勝率: ${formatWinRate(data.history.win_rate)}\n賺賠比: ${formatProfitFactor(data.history.profit_factor)}`);
    } catch (error) {
      console.error('Error fetching backtest details:', error);
      alert('獲取詳情失敗');
    }
  };

  const handleCompareSelected = async () => {
    if (selectedHistories.length < 2) {
      alert('請選擇至少 2 個回測記錄進行比較');
      return;
    }

    try {
      const response = await fetch('/api/backtest/compare?user_id=1', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ history_ids: selectedHistories }),
      });

      if (!response.ok) throw new Error('Failed to fetch comparisons');
      const data = await response.json();
      setShowComparison(true);
      setComparisonData(data.comparisons);
    } catch (error) {
      console.error('Error fetching comparisons:', error);
      alert('比較失敗');
    }
  };

  const [comparisonData, setComparisonData] = useState([]);

  const getAverageWinRate = () => {
    if (comparisonData.length === 0) return 'N/A';
    const validRates = comparisonData.map(c => c.win_rate).filter(r => r !== null && !isNaN(r));
    if (validRates.length === 0) return 'N/A';
    const avg = validRates.reduce((sum, rate) => sum + rate, 0) / validRates.length;
    return formatWinRate(avg);
  };

  const getAverageProfitFactor = () => {
    if (comparisonData.length === 0) return 'N/A';
    const validFactors = comparisonData.map(c => c.profit_factor).filter(f => f !== null && !isNaN(f) && f !== Infinity);
    if (validFactors.length === 0) return 'N/A';
    const avg = validFactors.reduce((sum, factor) => sum + factor, 0) / validFactors.length;
    return formatProfitFactor(avg);
  };

  if (loading) {
    return (
      <div className="backtest-history-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>載入回測歷史記錄中...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="backtest-history-page">
        <div className="error-container">
          <h2>錯誤</h2>
          <p>{error}</p>
          <button onClick={() => window.location.reload()} className="retry-button">
            重試
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="backtest-history-page">
      <div className="page-header">
        <h1>回測歷史記錄</h1>
        <div className="page-actions">
          <span className="record-count">共 {histories.length} 筆記錄</span>
          {selectedHistories.length > 0 && (
            <button 
              onClick={handleCompareSelected} 
              className="compare-button"
            >
              比較選擇項 ({selectedHistories.length})
            </button>
          )}
        </div>
      </div>

      {showComparison && comparisonData.length > 0 && (
        <div className="comparison-panel">
          <div className="comparison-header">
            <h3>比較結果</h3>
            <button 
              onClick={() => setShowComparison(false)} 
              className="close-button"
            >
              ×
            </button>
          </div>
          
          <div className="comparison-summary">
            <div className="summary-item">
              <label>平均勝率</label>
              <span className="metric-value">{getAverageWinRate()}</span>
            </div>
            <div className="summary-item">
              <label>平均賺賠比</label>
              <span className="metric-value">{getAverageProfitFactor()}</span>
            </div>
            <div className="summary-item">
              <label>比較項目</label>
              <span>{comparisonData.length}</span>
            </div>
          </div>

          <table className="comparison-table">
            <thead>
              <tr>
                <th>策略</th>
                <th>日期</th>
                <th>勝率</th>
                <th>賺賠比</th>
                <th>總交易數</th>
                <th>狀態</th>
              </tr>
            </thead>
            <tbody>
              {comparisonData.map(comp => (
                <tr key={comp.id}>
                  <td className="strategy-name">{comp.strategy_id}</td>
                  <td>{formatDate(comp.created_at)}</td>
                  <td className="metric win-rate">
                    {formatWinRate(comp.win_rate)}
                  </td>
                  <td className="metric profit-factor">
                    {formatProfitFactor(comp.profit_factor)}
                  </td>
                  <td>{comp.total_trades || 'N/A'}</td>
                  <td>
                    <span className={`status ${getStatusColor(comp.status)}`}>
                      {getStatusText(comp.status)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="history-table-container">
        <table className="history-table">
          <thead>
            <tr>
              <th>
                <input
                  type="checkbox"
                  onChange={(e) => {
                    if (e.target.checked) {
                      setSelectedHistories(histories.map(h => h.id));
                    } else {
                      setSelectedHistories([]);
                    }
                  }}
                  checked={selectedHistories.length === histories.length && histories.length > 0}
                />
              </th>
              <th>日期時間</th>
              <th>策略 ID</th>
              <th>狀態</th>
              <th>勝率</th>
              <th>賺賠比</th>
              <th>總交易數</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {histories.map(history => (
              <tr key={history.id}>
                <td>
                  <input
                    type="checkbox"
                    checked={selectedHistories.includes(history.id)}
                    onChange={() => handleCompare(history.id)}
                  />
                </td>
                <td className="date-time">
                  {formatDate(history.created_at)}
                </td>
                <td className="strategy-id">
                  <code>{history.strategy_id}</code>
                </td>
                <td>
                  <span className={`status ${getStatusColor(history.status)}`}>
                    {getStatusText(history.status)}
                  </span>
                </td>
                <td className="metric win-rate">
                  {formatWinRate(history.win_rate)}
                </td>
                <td className="metric profit-factor">
                  {formatProfitFactor(history.profit_factor)}
                </td>
                <td className="total-trades">
                  {history.total_trades || 'N/A'}
                </td>
                <td className="actions">
                  <button
                    onClick={() => handleViewDetails(history.id)}
                    className="btn btn-view"
                    title="查看詳情"
                  >
                    詳情
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {histories.length === 0 && (
        <div className="no-data-container">
          <div className="no-data-icon">📊</div>
          <h3>尚無回測記錄</h3>
          <p>請先運行回測，結果將顯示在這裡</p>
          <button className="btn btn-primary">
            開始回測
          </button>
        </div>
      )}

      <div className="legend">
        <h4>指標說明</h4>
        <div className="legend-item">
          <span className="legend-label">勝率 (Win Rate):</span>
          <span className="legend-desc">盈利交易佔總交易的比例，越高越好</span>
        </div>
        <div className="legend-item">
          <span className="legend-label">賺賠比 (Profit Factor):</span>
          <span className="legend-desc">總盈利金額除以總虧損金額，大於1表示盈利</span>
        </div>
      </div>
    </div>
  );
}

export default BacktestHistoryPage;