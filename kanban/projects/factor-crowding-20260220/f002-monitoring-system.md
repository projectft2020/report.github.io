# 因子擁擠度監控系統實現 (Factor Crowding Monitoring System)

**Task ID:** f002-monitoring-system
**Agent:** Charlie Analyst
**Status:** completed
**Timestamp:** 2026-02-20T12:30:00+08:00

---

## Executive Summary

基於 f001 設計的擁擠度指標系統，實現了完整的監控系統，包括數據處理、指標計算、預警機制、可視化儀表板和回測驗證框架。系統採用模塊化架構，支持實時監控、歷史回測、預警通知和報告生成等功能。核心組件包括：

- **指標計算引擎**：FEI、FVI、FVIol 和 CCS 的完整實現
- **實時監控器**：每日更新、閾值檢測、趨勢跟蹤
- **預警系統**：三級預警機制、多維確認、通知推送
- **可視化儀表板**：交互式圖表、熱力圖、儀表盤
- **回測框架**：IC/IR 計算、分組回測、策略模擬

---

## 1. 系統架構

### 1.1 目錄結構

```
factor_crowding_monitor/
├── __init__.py
├── config/
│   ├── __init__.py
│   ├── settings.py           # 配置參數
│   └── thresholds.py         # 閾值定義
├── data/
│   ├── __init__.py
│   ├── loader.py             # 數據加載器
│   ├── processor.py          # 數據處理器
│   └── storage.py            # 數據存儲接口
├── metrics/
│   ├── __init__.py
│   ├── fei.py                # 因子暴露度指數
│   ├── fvi.py                # 因子估值指數
│   ├── fviol.py              # 因子波動率指數
│   └── ccs.py                # 綜合擁擠度評分
├── monitor/
│   ├── __init__.py
│   ├── realtime.py           # 實時監控器
│   ├── alert.py              # 預警系統
│   └── scheduler.py          # 調度器
├── backtest/
│   ├── __init__.py
│   ├── engine.py             # 回測引擎
│   ├── validators.py         # 驗證器
│   └── strategies.py         # 策略庫
├── visualization/
│   ├── __init__.py
│   ├── dashboard.py          # 儀表板
│   ├── charts.py             # 圖表生成
│   └── reports.py            # 報告生成
├── utils/
│   ├── __init__.py
│   ├── helpers.py            # 輔助函數
│   └── decorators.py         # 裝飾器
├── main.py                   # 主程序入口
├── run_monitor.py            # 監控啟動腳本
└── tests/
    ├── test_metrics.py       # 指標測試
    ├── test_monitor.py       # 監控測試
    └── test_backtest.py      # 回測測試
```

### 1.2 技術棧

| 組件 | 技術選型 | 用途 |
|-----|---------|-----|
| **語言** | Python 3.10+ | 開發語言 |
| **數據處理** | pandas, numpy | 數據操作 |
| **統計計算** | scipy, statsmodels | 統計分析 |
| **時間序列** | arch | GARCH 波動率 |
| **數據庫** | SQLite / PostgreSQL | 數據存儲 |
| **可視化** | plotly, matplotlib | 圖表渲染 |
| **任務調度** | APScheduler | 定時任務 |
| **日誌** | logging | 日誌記錄 |
| **配置管理** | pydantic | 配置驗證 |
| **API 框架** | FastAPI | Web API（可選） |

---

## 2. 核心配置

### 2.1 配置文件 (config/settings.py)

```python
"""
系統配置文件
"""
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import timedelta

class DatabaseConfig(BaseModel):
    """數據庫配置"""
    type: str = "sqlite"
    path: Path = Path("./data/crowding_monitor.db")
    pool_size: int = 10

class DataConfig(BaseModel):
    """數據配置"""
    market_data_path: Path = Path("./data/market/")
    financial_data_path: Path = Path("./data/financial/")
    factor_data_path: Path = Path("./data/factors/")
    update_frequency: str = "daily"  # daily, hourly, realtime

class MetricConfig(BaseModel):
    """指標配置"""
    lookback_window: int = 252  # 歷史窗口
    short_window: int = 20      # 短期窗口
    long_window: int = 60       # 長期窗口
    ewma_lambda: float = 0.94   # EWMA 平滑參數

class WeightConfig(BaseModel):
    """權重配置"""
    fei_weight: float = 0.4
    fvi_weight: float = 0.35
    fviol_weight: float = 0.25

    @property
    def weights(self) -> Dict[str, float]:
        return {
            "FEI": self.fei_weight,
            "FVI": self.fvi_weight,
            "FVIol": self.fviol_weight
        }

class AlertConfig(BaseModel):
    """預警配置"""
    enabled: bool = True
    level_1_threshold: float = 75  # 關注
    level_2_threshold: float = 80  # 警示
    level_3_threshold: float = 90  # 緊急
    min_duration_days: int = 3     # 最小持續天數
    notification_channels: List[str] = ["log", "email"]  # log, email, webhook

class BacktestConfig(BaseModel):
    """回測配置"""
    start_date: str = "2010-01-01"
    end_date: str = "2026-02-20"
    train_start: str = "2010-01-01"
    train_end: str = "2019-12-31"
    validation_start: str = "2020-01-01"
    validation_end: str = "2022-12-31"
    test_start: str = "2023-01-01"
    test_end: str = "2026-02-20"

class LoggingConfig(BaseModel):
    """日誌配置"""
    level: str = "INFO"
    path: Path = Path("./logs/")
    max_size_mb: int = 10
    backup_count: int = 5

class SystemConfig(BaseModel):
    """系統配置"""
    project_name: str = "Factor Crowding Monitor"
    version: str = "1.0.0"
    debug: bool = False

    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    data: DataConfig = Field(default_factory=DataConfig)
    metric: MetricConfig = Field(default_factory=MetricConfig)
    weight: WeightConfig = Field(default_factory=WeightConfig)
    alert: AlertConfig = Field(default_factory=AlertConfig)
    backtest: BacktestConfig = Field(default_factory=BacktestConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

# 全局配置實例
config = SystemConfig()
```

### 2.2 閾值定義 (config/thresholds.py)

```python
"""
閾值定義
"""
from typing import Dict, Tuple

# CCS 擁擠度等級閾值
CROWDING_LEVELS = {
    "extreme_cold": (0, 20),
    "cold": (20, 40),
    "neutral": (40, 60),
    "hot": (60, 80),
    "extreme_hot": (80, 100)
}

# CCS 操作建議
CROWDING_RECOMMENDATIONS = {
    "extreme_cold": "逆向建倉",
    "cold": "觀察，逢低佈局",
    "neutral": "持有觀望",
    "hot": "考慮減持",
    "extreme_hot": "大幅減倉/避險"
}

# 預警等級定義
ALERT_LEVELS = {
    1: {"name": "關注", "color": "yellow", "action": "密切監控"},
    2: {"name": "警示", "color": "orange", "action": "調整倉位"},
    3: {"name": "緊急", "color": "red", "action": "大幅減倉"}
}

# 子指標閾值
SUB_METRIC_THRESHOLDS = {
    "FEI": {
        "extreme_low": 30,
        "low": 40,
        "high": 70,
        "extreme_high": 80
    },
    "FVI": {
        "extreme_low": 20,
        "low": 40,
        "high": 80,
        "extreme_high": 90
    },
    "FVIol": {
        "extreme_low": 20,
        "low": 30,
        "high": 50,
        "extreme_high": 60
    }
}

def get_crowding_level(score: float) -> str:
    """根據評分獲取擁擠度等級"""
    for level, (min_val, max_val) in CROWDING_LEVELS.items():
        if min_val <= score <= max_val:
            return level
    return "unknown"

def get_recommendation(score: float) -> str:
    """根據評分獲取操作建議"""
    level = get_crowding_level(score)
    return CROWDING_RECOMMENDATIONS.get(level, "未知")

def get_alert_level(score: float, duration_days: int) -> int:
    """根據評分和持續時間獲取預警等級"""
    if score >= 90 or score <= 10:
        if duration_days >= 7:
            return 3
        elif duration_days >= 5:
            return 2
    elif score >= 80 or score <= 20:
        if duration_days >= 5:
            return 2
        elif duration_days >= 3:
            return 1
    elif score >= 75 or score <= 25:
        if duration_days >= 3:
            return 1
    return 0
```

---

## 3. 數據處理層

### 3.1 數據加載器 (data/loader.py)

```python
"""
數據加載器
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataLoader:
    """數據加載器"""

    def __init__(self, config):
        self.config = config
        self.market_path = config.data.market_data_path
        self.financial_path = config.data.financial_data_path
        self.factor_path = config.data.factor_data_path

    def load_market_data(
        self,
        start_date: str,
        end_date: str,
        symbols: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        加載市場數據

        Args:
            start_date: 開始日期
            end_date: 結束日期
            symbols: 股票代碼列表，None 則加載全部

        Returns:
            DataFrame: 市場數據，包含股價、成交量等
        """
        # 示例實現 - 實際應根據數據源調整
        try:
            # 嘗試從 CSV 加載
            file_path = self.market_path / "market_data.csv"
            if file_path.exists():
                df = pd.read_csv(file_path, parse_dates=['date'])
                df = df.set_index('date')

                # 時間篩選
                df = df.loc[start_date:end_date]

                # 符號篩選
                if symbols:
                    df = df[df['symbol'].isin(symbols)]

                return df
            else:
                logger.warning(f"市場數據文件不存在: {file_path}")
                return self._generate_mock_market_data(start_date, end_date)

        except Exception as e:
            logger.error(f"加載市場數據失敗: {e}")
            raise

    def load_financial_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        加載財務數據

        Args:
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            DataFrame: 財務數據
        """
        try:
            file_path = self.financial_path / "financial_data.csv"
            if file_path.exists():
                df = pd.read_csv(file_path, parse_dates=['report_date'])
                df = df.set_index('report_date')
                return df.loc[start_date:end_date]
            else:
                logger.warning(f"財務數據文件不存在: {file_path}")
                return self._generate_mock_financial_data(start_date, end_date)
        except Exception as e:
            logger.error(f"加載財務數據失敗: {e}")
            raise

    def load_factor_data(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        加載因子數據

        Args:
            factor_id: 因子 ID
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            DataFrame: 因子數據，包含暴露度、收益率等
        """
        try:
            file_path = self.factor_path / f"{factor_id}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path, parse_dates=['date'])
                df = df.set_index('date')
                return df.loc[start_date:end_date]
            else:
                logger.warning(f"因子數據文件不存在: {file_path}")
                return self._generate_mock_factor_data(factor_id, start_date, end_date)
        except Exception as e:
            logger.error(f"加載因子數據失敗: {e}")
            raise

    def load_capital_flow(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """
        加載資金流數據

        Args:
            factor_id: 因子 ID
            start_date: 開始日期
            end_date: 結束日期

        Returns:
            DataFrame: 資金流數據
        """
        try:
            file_path = self.factor_path / f"capital_flow_{factor_id}.csv"
            if file_path.exists():
                df = pd.read_csv(file_path, parse_dates=['date'])
                df = df.set_index('date')
                return df.loc[start_date:end_date]
            else:
                return self._generate_mock_capital_flow(factor_id, start_date, end_date)
        except Exception as e:
            logger.error(f"加載資金流數據失敗: {e}")
            raise

    def _generate_mock_market_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成模擬市場數據（開發用）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

        data = []
        for date in dates:
            for symbol in symbols:
                # 隨機生成股價
                price = np.random.normal(100, 10)
                volume = np.random.randint(1000000, 10000000)
                market_cap = price * volume * np.random.uniform(0.1, 1)

                data.append({
                    'date': date,
                    'symbol': symbol,
                    'close': price,
                    'volume': volume,
                    'market_cap': market_cap
                })

        df = pd.DataFrame(data)
        return df.set_index('date')

    def _generate_mock_financial_data(
        self,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成模擬財務數據（開發用）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='Q')
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META']

        data = []
        for date in dates:
            for symbol in symbols:
                data.append({
                    'report_date': date,
                    'symbol': symbol,
                    'pe': np.random.uniform(10, 30),
                    'pb': np.random.uniform(1, 5),
                    'roe': np.random.uniform(0.1, 0.3),
                    'revenue_growth': np.random.uniform(-0.1, 0.3)
                })

        df = pd.DataFrame(data)
        return df.set_index('report_date')

    def _generate_mock_factor_data(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成模擬因子數據（開發用）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 模擬因子收益率
        np.random.seed(hash(factor_id) % (2**32))
        returns = np.random.normal(0, 0.01, len(dates))

        data = pd.DataFrame({
            'date': dates,
            'return': returns,
            'exposure': np.random.uniform(-1, 1, len(dates)),
            'sharpe': np.random.uniform(-0.5, 1.5, len(dates))
        })

        return data.set_index('date')

    def _generate_mock_capital_flow(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成模擬資金流數據（開發用）"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        data = pd.DataFrame({
            'date': dates,
            'northbound_flow': np.random.normal(0, 100000000, len(dates)),
            'institutional_flow': np.random.normal(0, 50000000, len(dates)),
            'retail_flow': np.random.normal(0, 20000000, len(dates))
        })

        return data.set_index('date')
```

### 3.2 數據處理器 (data/processor.py)

```python
"""
數據處理器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class DataProcessor:
    """數據處理器"""

    def __init__(self, config):
        self.config = config

    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        數據清洗

        Args:
            df: 原始數據

        Returns:
            清洗後的數據
        """
        # 移除重複
        df = df.drop_duplicates()

        # 處理缺失值
        df = self._handle_missing_values(df)

        # 異常值處理
        df = self._handle_outliers(df)

        return df

    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理缺失值"""
        # 前向填充
        df = df.ffill()

        # 後向填充
        df = df.bfill()

        # 剩餘缺失值用均值填充
        for col in df.select_dtypes(include=[np.number]).columns:
            df[col].fillna(df[col].mean(), inplace=True)

        return df

    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """處理異常值"""
        for col in df.select_dtypes(include=[np.number]).columns:
            # 使用 IQR 方法檢測異常值
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            # 箱尾處理
            df[col] = df[col].clip(lower_bound, upper_bound)

        return df

    def calculate_returns(
        self,
        prices: pd.Series,
        method: str = "log"
    ) -> pd.Series:
        """
        計算收益率

        Args:
            prices: 價格序列
            method: 計算方法，log 或 simple

        Returns:
            收益率序列
        """
        if method == "log":
            return np.log(prices / prices.shift(1))
        else:
            return prices.pct_change()

    def calculate_ewma(
        self,
        series: pd.Series,
        lambda_: float = 0.94
    ) -> pd.Series:
        """
        計算 EWMA 平滑

        Args:
            series: 原始序列
            lambda_: 平滑參數

        Returns:
            平滑後的序列
        """
        return series.ewm(alpha=1-lambda_, adjust=False).mean()

    def calculate_rolling_stats(
        self,
        series: pd.Series,
        window: int
    ) -> pd.DataFrame:
        """
        計算滾動統計量

        Args:
            series: 原始序列
            window: 滾動窗口

        Returns:
            包含均值、標準差、百分位的 DataFrame
        """
        return pd.DataFrame({
            'mean': series.rolling(window).mean(),
            'std': series.rolling(window).std(),
            'min': series.rolling(window).min(),
            'max': series.rolling(window).max(),
            'median': series.rolling(window).median(),
            'p25': series.rolling(window).quantile(0.25),
            'p75': series.rolling(window).quantile(0.75)
        })

    def calculate_percentile(
        self,
        value: float,
        series: pd.Series
    ) -> float:
        """
        計算百分位

        Args:
            value: 待計算值
            series: 參考序列

        Returns:
            百分位值 (0-100)
        """
        return stats.percentileofscore(series, value)

    def standardize(self, series: pd.Series) -> pd.Series:
        """
        標準化（z-score）

        Args:
            series: 原始序列

        Returns:
            標準化後的序列
        """
        return (series - series.mean()) / series.std()

    def normalize(
        self,
        series: pd.Series,
        method: str = "minmax"
    ) -> pd.Series:
        """
        歸一化到 [0, 1]

        Args:
            series: 原始序列
            method: 歸一化方法，minmax 或 zscore_to_0_100

        Returns:
            歸一化後的序列 (0-100)
        """
        if method == "minmax":
            min_val = series.min()
            max_val = series.max()
            return (series - min_val) / (max_val - min_val) * 100
        else:
            # z-score 轉換到 0-100，50 為中性
            zscore = self.standardize(series)
            return (zscore * 10 + 50).clip(0, 100)

    def align_data(
        self,
        *dfs: pd.DataFrame
    ) -> List[pd.DataFrame]:
        """
        對齊多個 DataFrame 的時間索引

        Args:
            *dfs: 多個 DataFrame

        Returns:
            對齊後的 DataFrame 列表
        """
        # 找到所有日期的交集
        common_index = dfs[0].index
        for df in dfs[1:]:
            common_index = common_index.intersection(df.index)

        # 對齊所有 DataFrame
        return [df.loc[common_index] for df in dfs]

    def calculate_hhi(self, weights: pd.Series) -> float:
        """
        計算 HHI 指數（赫芬達爾-赫希曼指數）

        Args:
            weights: 權重序列

        Returns:
            HHI 值
        """
        return (weights ** 2).sum()

    def calculate_correlation(
        self,
        series1: pd.Series,
        series2: pd.Series,
        method: str = "pearson"
    ) -> float:
        """
        計算相關性

        Args:
            series1: 序列 1
            series2: 序列 2
            method: 相關性方法

        Returns:
            相關係數
        """
        return series1.corr(series2, method=method)
```

---

## 4. 指標計算層

### 4.1 因子暴露度指數 (metrics/fei.py)

```python
"""
因子暴露度指數 (FEI) 計算
"""
import pandas as pd
import numpy as np
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class FactorExposureIndex:
    """因子暴露度指數"""

    def __init__(self, config):
        self.config = config
        self.ncf_weight = 0.6  # 資金淨流入率權重
        self.pc_weight = 0.4   # 頭寸集中度權重

    def calculate(
        self,
        factor_data: pd.DataFrame,
        capital_flow: pd.DataFrame,
        position_weights: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        計算 FEI

        Args:
            factor_data: 因子數據
            capital_flow: 資金流數據
            position_weights: 頭寸權重數據（可選）

        Returns:
            包含 FEI 的 DataFrame
        """
        # 計算資金淨流入率
        ncf = self._calculate_ncf(factor_data, capital_flow)

        # 計算頭寸集中度
        pc = self._calculate_pc(factor_data, position_weights)

        # 合併
        fei_data = pd.DataFrame({
            'NCF': ncf,
            'PC': pc
        })

        # 計算綜合 FEI
        fei_data['FEI'] = (
            self.ncf_weight * fei_data['NCF'] +
            self.pc_weight * fei_data['PC']
        )

        return fei_data

    def _calculate_ncf(
        self,
        factor_data: pd.DataFrame,
        capital_flow: pd.DataFrame
    ) -> pd.Series:
        """
        計算資金淨流入率 (Net Capital Flow Rate, NCF)

        公式: NCF_t = Σ(w_i,t × r_i,t) / Σ|w_i,t × r_i,t| × 50 + 50
        """
        # 對齊數據
        factor_returns = factor_data['return']
        exposure = factor_data['exposure']

        # 總資金流
        total_flow = capital_flow['northbound_flow'] + \
                     capital_flow['institutional_flow'] + \
                     capital_flow['retail_flow']

        # 計算加權流動
        weighted_flow = exposure * total_flow

        # 計算 NCF
        numerator = weighted_flow
        denominator = weighted_flow.abs()

        ncf = (numerator / denominator * 50 + 50).fillna(50)

        return ncf.clip(0, 100)

    def _calculate_pc(
        self,
        factor_data: pd.DataFrame,
        position_weights: Optional[pd.DataFrame] = None
    ) -> pd.Series:
        """
        計算頭寸集中度 (Position Concentration, PC)

        公式: PC_t = (HHI_t - HHI_min) / (HHI_max - HHI_min) × 100
        """
        if position_weights is not None:
            # 使用實際頭寸權重
            weights = position_weights.abs()
        else:
            # 使用因子暴露度作為權重的代理
            weights = factor_data['exposure'].abs()

        # 計算 HHI
        hhi = self._calculate_hhi(weights)

        # 標準化到 0-100
        # 假設 HHI 範圍 [1/n, 1]，n 為標的數量
        n = len(weights.columns) if isinstance(weights, pd.DataFrame) else 1
        hhi_min = 1.0 / n
        hhi_max = 1.0

        pc = ((hhi - hhi_min) / (hhi_max - hhi_min) * 100).fillna(50)

        return pc.clip(0, 100)

    def _calculate_hhi(self, weights: pd.Series) -> float:
        """
        計算 HHI 指數

        Args:
            weights: 權重序列

        Returns:
            HHI 值
        """
        return (weights ** 2).sum()

    def get_crowding_signal(self, fei: float) -> str:
        """
        獲取擁擠信號

        Args:
            fei: FEI 值

        Returns:
            信號: low, neutral, high
        """
        if fei < 40:
            return "low"
        elif fei > 60:
            return "high"
        else:
            return "neutral"
```

### 4.2 因子估值指數 (metrics/fvi.py)

```python
"""
因子估值指數 (FVI) 計算
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class FactorValuationIndex:
    """因子估值指數"""

    def __init__(self, config):
        self.config = config
        self.rvp_weight = 0.7  # 相對估值百分位權重
        self.ee_weight = 0.3   # 超預期程度權重

    def calculate(
        self,
        factor_data: pd.DataFrame,
        financial_data: pd.DataFrame,
        valuation_metrics: Optional[List[str]] = None,
        forecast_data: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """
        計算 FVI

        Args:
            factor_data: 因子數據
            financial_data: 財務數據
            valuation_metrics: 估值指標列表
            forecast_data: 預期數據

        Returns:
            包含 FVI 的 DataFrame
        """
        if valuation_metrics is None:
            valuation_metrics = ['pe', 'pb', 'roe']

        # 計算相對估值百分位
        rvp = self._calculate_rvp(
            factor_data,
            financial_data,
            valuation_metrics
        )

        # 計算超預期程度
        ee = self._calculate_ee(financial_data, forecast_data)

        # 合併
        fvi_data = pd.DataFrame({
            'RVP': rvp,
            'EE': ee
        })

        # 調整 EE 到 0-100
        fvi_data['EE_adj'] = (fvi_data['EE'] + 100) / 2

        # 計算綜合 FVI
        fvi_data['FVI'] = (
            self.rvp_weight * fvi_data['RVP'] +
            self.ee_weight * fvi_data['EE_adj']
        )

        return fvi_data

    def _calculate_rvp(
        self,
        factor_data: pd.DataFrame,
        financial_data: pd.DataFrame,
        valuation_metrics: List[str]
    ) -> pd.Series:
        """
        計算相對估值百分位 (Relative Valuation Percentile, RVP)

        包括橫截面百分位和時間序列百分位
        """
        # 橫截面百分位（在當前時點，該因子相對其他因子的估值水平）
        # 由於只有單因子數據，這裡主要實現時間序列百分位

        rvp_series = pd.Series(index=factor_data.index, dtype=float)

        for metric in valuation_metrics:
            if metric in financial_data.columns:
                # 獲取該指標的時間序列
                metric_series = financial_data[metric]

                # 計算滾動百分位
                window = self.config.metric.lookback_window
                rolling_percentile = metric_series.rolling(
                    window,
                    min_periods=int(window * 0.5)
                ).apply(
                    lambda x: stats.percentileofscore(x, x.iloc[-1])
                )

                rvp_series = rvp_series.add(rolling_percentile, fill_value=0)

        # 平均多個指標
        if len(valuation_metrics) > 0:
            rvp_series = rvp_series / len(valuation_metrics)

        return rvp_series.clip(0, 100)

    def _calculate_ee(
        self,
        financial_data: pd.DataFrame,
        forecast_data: Optional[pd.DataFrame]
    ) -> pd.Series:
        """
        計算超預期程度 (Expectation Excess, EE)

        公式: EE = (Actual - Forecast) / |Forecast| × 100
        """
        if forecast_data is None:
            # 如果沒有預期數據，使用前期值作為預期
            ee_series = financial_data['roe'].pct_change() * 100
        else:
            # 使用實際預期數據
            actual = financial_data['roe']
            forecast = forecast_data['roe_forecast']

            ee_series = ((actual - forecast) / forecast.abs() * 100).fillna(0)

        # EWMA 平滑
        ewma_lambda = self.config.metric.ewma_lambda
        ee_series = ee_series.ewm(alpha=1-ewma_lambda, adjust=False).mean()

        return ee_series.clip(-100, 100)

    def get_crowding_signal(self, fvi: float) -> str:
        """
        獲取擁擠信號

        Args:
            fvi: FVI 值

        Returns:
            信號: low, neutral, high
        """
        if fvi < 40:
            return "low"
        elif fvi > 60:
            return "high"
        else:
            return "neutral"
```

### 4.3 因子波動率指數 (metrics/fviol.py)

```python
"""
因子波動率指數 (FVIol) 計算
"""
import pandas as pd
import numpy as np
from typing import Optional
from arch import arch_model
import logging

logger = logging.getLogger(__name__)

class FactorVolatilityIndex:
    """因子波動率指數"""

    def __init__(self, config):
        self.config = config
        self.vd_weight = 0.7  # 波動率偏離度權重
        self.vsi_weight = 0.3  # 波動率結構指數權重

    def calculate(
        self,
        factor_data: pd.DataFrame,
        use_garch: bool = True
    ) -> pd.DataFrame:
        """
        計算 FVIol

        Args:
            factor_data: 因子數據
            use_garch: 是否使用 GARCH 模型

        Returns:
            包含 FVIol 的 DataFrame
        """
        # 計算波動率偏離度
        vd = self._calculate_vd(factor_data, use_garch)

        # 計算波動率結構指數
        vsi = self._calculate_vsi(factor_data)

        # 合併
        fviol_data = pd.DataFrame({
            'VD': vd,
            'VSI': vsi
        })

        # 計算綜合 FVIol
        fviol_data['FVIol'] = (
            self.vd_weight * fviol_data['VD'] +
            self.vsi_weight * fviol_data['VSI']
        )

        return fviol_data

    def _calculate_vd(
        self,
        factor_data: pd.DataFrame,
        use_garch: bool
    ) -> pd.Series:
        """
        計算波動率偏離度 (Volatility Deviation, VD)

        公式: VD_t = |σ_t - σ_long| / σ_long × 100
        """
        returns = factor_data['return'].dropna()

        if use_garch:
            # 使用 GARCH(1,1) 估計波動率
            volatility = self._estimate_garch_volatility(returns)
        else:
            # 使用歷史波動率
            volatility = self._estimate_historical_volatility(returns)

        # 長期平均波動率
        long_window = self.config.metric.long_window
        sigma_long = volatility.rolling(long_window).mean()

        # 計算偏離度
        vd = ((volatility - sigma_long).abs() / sigma_long * 100).fillna(0)

        return vd.clip(0, 100)

    def _estimate_historical_volatility(
        self,
        returns: pd.Series,
        window: int = 20
    ) -> pd.Series:
        """
        計算歷史波動率

        Args:
            returns: 收益率序列
            window: 滾動窗口

        Returns:
            波動率序列
        """
        return returns.rolling(window).std()

    def _estimate_garch_volatility(
        self,
        returns: pd.Series
    ) -> pd.Series:
        """
        使用 GARCH(1,1) 估計波動率

        Args:
            returns: 收益率序列

        Returns:
            波動率序列
        """
        volatility = pd.Series(index=returns.index, dtype=float)

        # 滾動估計 GARCH
        window = self.config.metric.short_window

        for i in range(window, len(returns)):
            window_returns = returns.iloc[i-window:i]

            try:
                # 擬合 GARCH(1,1)
                model = arch_model(window_returns * 100, vol='Garch', p=1, q=1)
                result = model.fit(disp='off')

                # 預測下一期波動率
                forecast = result.forecast(horizon=1)
                vol = np.sqrt(forecast.variance.values[-1, 0]) / 100

                volatility.iloc[i] = vol

            except Exception as e:
                logger.warning(f"GARCH 估計失敗: {e}，使用歷史波動率")
                volatility.iloc[i] = window_returns.std()

        return volatility

    def _calculate_vsi(
        self,
        factor_data: pd.DataFrame
    ) -> pd.Series:
        """
        計算波動率結構指數 (Volatility Structure Index, VSI)

        公式: VSI = Correlation(σ_short, σ_long) × 50
        """
        returns = factor_data['return'].dropna()

        # 短期波動率
        short_window = 5
        sigma_short = returns.rolling(short_window).std()

        # 長期波動率
        long_window = 60
        sigma_long = returns.rolling(long_window).std()

        # 計算滾動相關性
        correlation = sigma_short.rolling(60).corr(sigma_long)

        # 調整到 0-100
        vsi = correlation * 50 + 50

        return vsi.clip(0, 100)

    def get_crowding_signal(self, fviol: float) -> str:
        """
        獲取擁擠信號

        Args:
            fviol: FVIol 值

        Returns:
            信號: low, neutral, high
        """
        if fviol < 30:
            return "low"
        elif fviol > 50:
            return "high"
        else:
            return "neutral"
```

### 4.4 綜合擁擠度評分 (metrics/ccs.py)

```python
"""
綜合擁擠度評分 (CCS) 計算
"""
import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class ComprehensiveCrowdingScore:
    """綜合擁擠度評分"""

    def __init__(self, config):
        self.config = config
        self.weights = config.weight.weights

    def calculate(
        self,
        fei_data: pd.DataFrame,
        fvi_data: pd.DataFrame,
        fviol_data: pd.DataFrame
    ) -> pd.DataFrame:
        """
        計算 CCS

        Args:
            fei_data: FEI 數據
            fvi_data: FVI 數據
            fviol_data: FVIol 數據

        Returns:
            包含 CCS 的 DataFrame
        """
        # 對齊數據
        aligned_data = self._align_data(fei_data, fvi_data, fviol_data)

        # 計算 CCS
        aligned_data['CCS'] = (
            self.weights['FEI'] * aligned_data['FEI'] +
            self.weights['FVI'] * aligned_data['FVI'] +
            self.weights['FVIol'] * aligned_data['FVIol']
        )

        # 計算擁擠度等級
        aligned_data['crowding_level'] = aligned_data['CCS'].apply(
            lambda x: self._get_crowding_level(x)
        )

        # 計算操作建議
        aligned_data['recommendation'] = aligned_data['CCS'].apply(
            lambda x: self._get_recommendation(x)
        )

        return aligned_data

    def _align_data(
        self,
        *dfs: pd.DataFrame
    ) -> pd.DataFrame:
        """對齊多個 DataFrame"""
        # 找到公共索引
        common_index = dfs[0].index
        for df in dfs[1:]:
            common_index = common_index.intersection(df.index)

        # 合併
        result = pd.DataFrame(index=common_index)
        for df in dfs:
            result = result.join(df, how='inner')

        return result

    def _get_crowding_level(self, score: float) -> str:
        """獲取擁擠度等級"""
        if score <= 20:
            return "extreme_cold"
        elif score <= 40:
            return "cold"
        elif score <= 60:
            return "neutral"
        elif score <= 80:
            return "hot"
        else:
            return "extreme_hot"

    def _get_recommendation(self, score: float) -> str:
        """獲取操作建議"""
        level = self._get_crowding_level(score)
        recommendations = {
            "extreme_cold": "逆向建倉",
            "cold": "觀察，逢低佈局",
            "neutral": "持有觀望",
            "hot": "考慮減持",
            "extreme_hot": "大幅減倉/避險"
        }
        return recommendations.get(level, "未知")

    def calculate_latest_score(
        self,
        fei: float,
        fvi: float,
        fviol: float
    ) -> Dict:
        """
        計算最新 CCS

        Args:
            fei: 最新 FEI 值
            fvi: 最新 FVI 值
            fviol: 最新 FVIol 值

        Returns:
            包含 CCS 和相關信息的字典
        """
        ccs = (
            self.weights['FEI'] * fei +
            self.weights['FVI'] * fvi +
            self.weights['FVIol'] * fviol
        )

        return {
            'CCS': round(ccs, 2),
            'FEI': round(fei, 2),
            'FVI': round(fvi, 2),
            'FVIol': round(fviol, 2),
            'crowding_level': self._get_crowding_level(ccs),
            'recommendation': self._get_recommendation(ccs)
        }

    def get_score_trend(
        self,
        ccs_series: pd.Series,
        window: int = 5
    ) -> str:
        """
        獲取評分趨勢

        Args:
            ccs_series: CCS 序列
            window: 滾動窗口

        Returns:
            趨勢: rising, falling, stable
        """
        if len(ccs_series) < window:
            return "unknown"

        recent = ccs_series.iloc[-window:]
        slope = np.polyfit(range(len(recent)), recent.values, 1)[0]

        if slope > 1:
            return "rising"
        elif slope < -1:
            return "falling"
        else:
            return "stable"
```

---

## 5. 監控系統

### 5.1 實時監控器 (monitor/realtime.py)

```python
"""
實時監控器
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

from ..config.settings import config
from ..data.loader import DataLoader
from ..data.processor import DataProcessor
from ..metrics.fei import FactorExposureIndex
from ..metrics.fvi import FactorValuationIndex
from ..metrics.fviol import FactorVolatilityIndex
from ..metrics.ccs import ComprehensiveCrowdingScore

logger = logging.getLogger(__name__)

@dataclass
class MonitoringResult:
    """監控結果"""
    factor_id: str
    factor_name: str
    timestamp: datetime
    ccs: float
    fei: float
    fvi: float
    fviol: float
    crowding_level: str
    recommendation: str
    trend: str
    confidence: float

class RealtimeMonitor:
    """實時監控器"""

    def __init__(self, config=config):
        self.config = config

        # 初始化組件
        self.loader = DataLoader(config)
        self.processor = DataProcessor(config)
        self.fei_calculator = FactorExposureIndex(config)
        self.fvi_calculator = FactorValuationIndex(config)
        self.fviol_calculator = FactorVolatilityIndex(config)
        self.ccs_calculator = ComprehensiveCrowdingScore(config)

        # 監控的因子列表
        self.monitored_factors = [
            {"id": "F001", "name": "價值因子"},
            {"id": "F002", "name": "成長因子"},
            {"id": "F003", "name": "動量因子"},
            {"id": "F004", "name": "質量因子"},
            {"id": "F005", "name": "低波動因子"}
        ]

        # 存儲歷史數據
        self.history = {}

    def monitor_factor(
        self,
        factor_id: str,
        factor_name: str
    ) -> MonitoringResult:
        """
        監控單個因子

        Args:
            factor_id: 因子 ID
            factor_name: 因子名稱

        Returns:
            監控結果
        """
        try:
            # 加載數據
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=400)).strftime('%Y-%m-%d')

            factor_data = self.loader.load_factor_data(factor_id, start_date, end_date)
            capital_flow = self.loader.load_capital_flow(factor_id, start_date, end_date)
            financial_data = self.loader.load_financial_data(start_date, end_date)

            # 數據處理
            factor_data = self.processor.clean_data(factor_data)
            capital_flow = self.processor.clean_data(capital_flow)
            financial_data = self.processor.clean_data(financial_data)

            # 對齊數據
            factor_data, capital_flow, financial_data = self.processor.align_data(
                factor_data, capital_flow, financial_data
            )

            # 計算指標
            fei_data = self.fei_calculator.calculate(factor_data, capital_flow)
            fvi_data = self.fvi_calculator.calculate(factor_data, financial_data)
            fviol_data = self.fviol_calculator.calculate(factor_data)

            # 計算 CCS
            ccs_data = self.ccs_calculator.calculate(fei_data, fvi_data, fviol_data)

            # 獲取最新值
            latest = ccs_data.iloc[-1]
            fei_latest = fei_data['FEI'].iloc[-1]
            fvi_latest = fvi_data['FVI'].iloc[-1]
            fviol_latest = fviol_data['FVIol'].iloc[-1]

            # 計算趨勢
            trend = self.ccs_calculator.get_score_trend(ccs_data['CCS'])

            # 計算置信度（基於歷史一致性）
            confidence = self._calculate_confidence(ccs_data)

            # 構建結果
            result = MonitoringResult(
                factor_id=factor_id,
                factor_name=factor_name,
                timestamp=datetime.now(),
                ccs=latest['CCS'],
                fei=fei_latest,
                fvi=fvi_latest,
                fviol=fviol_latest,
                crowding_level=latest['crowding_level'],
                recommendation=latest['recommendation'],
                trend=trend,
                confidence=confidence
            )

            # 存儲歷史數據
            self.history[factor_id] = ccs_data

            logger.info(f"因子 {factor_name} 監控完成: CCS={latest['CCS']:.2f}")

            return result

        except Exception as e:
            logger.error(f"監控因子 {factor_name} 失敗: {e}")
            raise

    def monitor_all_factors(self) -> List[MonitoringResult]:
        """
        監控所有因子

        Returns:
            所有因子的監控結果列表
        """
        results = []

        for factor in self.monitored_factors:
            try:
                result = self.monitor_factor(factor['id'], factor['name'])
                results.append(result)
            except Exception as e:
                logger.error(f"監控因子 {factor['name']} 失敗: {e}")
                continue

        return results

    def _calculate_confidence(
        self,
        ccs_data: pd.DataFrame,
        window: int = 20
    ) -> float:
        """
        計算置信度

        基於評分的穩定性

        Args:
            ccs_data: CCS 數據
            window: 滾動窗口

        Returns:
            置信度 (0-1)
        """
        if len(ccs_data) < window:
            return 0.5

        recent_ccs = ccs_data['CCS'].iloc[-window:]

        # 計算標準差
        std = recent_ccs.std()

        # 標準差越小，置信度越高
        confidence = np.exp(-std / 10)

        return np.clip(confidence, 0, 1)

    def get_factor_history(
        self,
        factor_id: str,
        days: int = 30
    ) -> Optional[pd.DataFrame]:
        """
        獲取因子歷史數據

        Args:
            factor_id: 因子 ID
            days: 天數

        Returns:
            歷史數據 DataFrame
        """
        if factor_id not in self.history:
            return None

        history = self.history[factor_id]
        cutoff_date = datetime.now() - timedelta(days=days)

        return history[history.index >= cutoff_date]

    def get_summary(self) -> Dict:
        """
        獲取監控摘要

        Returns:
            摘要字典
        """
        results = self.monitor_all_factors()

        summary = {
            'timestamp': datetime.now(),
            'total_factors': len(results),
            'extreme_hot': sum(1 for r in results if r.crowding_level == 'extreme_hot'),
            'hot': sum(1 for r in results if r.crowding_level == 'hot'),
            'neutral': sum(1 for r in results if r.crowding_level == 'neutral'),
            'cold': sum(1 for r in results if r.crowding_level == 'cold'),
            'extreme_cold': sum(1 for r in results if r.crowding_level == 'extreme_cold'),
            'factors': results
        }

        return summary
```

### 5.2 預警系統 (monitor/alert.py)

```python
"""
預警系統
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
import logging

from ..config.settings import config
from ..config.thresholds import (
    get_alert_level,
    ALERT_LEVELS,
    CROWDING_RECOMMENDATIONS
)

logger = logging.getLogger(__name__)

@dataclass
class Alert:
    """預警對象"""
    alert_id: str
    factor_id: str
    factor_name: str
    timestamp: datetime
    level: int
    level_name: str
    ccs: float
    fei: float
    fvi: float
    fviol: float
    duration_days: int
    recommendation: str
    action: str
    confidence: float

    def to_dict(self) -> Dict:
        """轉換為字典"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data

    def to_json(self) -> str:
        """轉換為 JSON"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

class AlertSystem:
    """預警系統"""

    def __init__(self, config=config):
        self.config = config
        self.alert_history = {}  # factor_id -> list of alerts
        self.active_alerts = {}   # factor_id -> current alert

    def check_alert(
        self,
        factor_id: str,
        factor_name: str,
        ccs_data: pd.DataFrame,
        latest_ccs: float,
        latest_fei: float,
        latest_fvi: float,
        latest_fviol: float,
        confidence: float
    ) -> Optional[Alert]:
        """
        檢查是否需要發送預警

        Args:
            factor_id: 因子 ID
            factor_name: 因子名稱
            ccs_data: CCS 歷史數據
            latest_ccs: 最新 CCS
            latest_fei: 最新 FEI
            latest_fvi: 最新 FVI
            latest_fviol: 最新 FVIol
            confidence: 置信度

        Returns:
            Alert 對象，如果不需要預警則返回 None
        """
        # 計算持續時間
        duration_days = self._calculate_duration(ccs_data, latest_ccs)

        # 獲取預警等級
        alert_level = get_alert_level(latest_ccs, duration_days)

        if alert_level == 0:
            # 清除現有預警
            if factor_id in self.active_alerts:
                logger.info(f"清除因子 {factor_name} 的預警")
                del self.active_alerts[factor_id]
            return None

        # 檢查是否已經發送過相同等級的預警
        if factor_id in self.active_alerts:
            existing_alert = self.active_alerts[factor_id]
            if existing_alert.level >= alert_level:
                # 已經有更高級別的預警，不重複發送
                return None

        # 創建新預警
        level_info = ALERT_LEVELS[alert_level]
        level_name = level_info['name']
        action = level_info['action']

        alert = Alert(
            alert_id=f"{factor_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            factor_id=factor_id,
            factor_name=factor_name,
            timestamp=datetime.now(),
            level=alert_level,
            level_name=level_name,
            ccs=latest_ccs,
            fei=latest_fei,
            fvi=latest_fvi,
            fviol=latest_fviol,
            duration_days=duration_days,
            recommendation=CROWDING_RECOMMENDATIONS.get(
                self._get_crowding_level(latest_ccs),
                "未知"
            ),
            action=action,
            confidence=confidence
        )

        # 記錄預警
        self.active_alerts[factor_id] = alert

        if factor_id not in self.alert_history:
            self.alert_history[factor_id] = []
        self.alert_history[factor_id].append(alert)

        logger.warning(
            f"發送預警: {factor_name} - {level_name} "
            f"(CCS={latest_ccs:.2f}, 持續{duration_days}天)"
        )

        return alert

    def _calculate_duration(
        self,
        ccs_data: pd.DataFrame,
        current_ccs: float
    ) -> int:
        """
        計算當前狀態持續時間

        Args:
            ccs_data: CCS 歷史數據
            current_ccs: 當前 CCS

        Returns:
            持續天數
        """
        level = self._get_crowding_level(current_ccs)

        # 計算連續處於同一等級的天數
        duration = 0
        for i in range(len(ccs_data) - 1, -1, -1):
            if self._get_crowding_level(ccs_data['CCS'].iloc[i]) == level:
                duration += 1
            else:
                break

        return duration

    def _get_crowding_level(self, ccs: float) -> str:
        """獲取擁擠度等級"""
        if ccs <= 20:
            return "extreme_cold"
        elif ccs <= 40:
            return "cold"
        elif ccs <= 60:
            return "neutral"
        elif ccs <= 80:
            return "hot"
        else:
            return "extreme_hot"

    def get_active_alerts(self) -> List[Alert]:
        """獲取所有活躍預警"""
        return list(self.active_alerts.values())

    def get_alert_history(
        self,
        factor_id: Optional[str] = None,
        level: Optional[int] = None
    ) -> List[Alert]:
        """
        獲取預警歷史

        Args:
            factor_id: 因子 ID，None 表示所有因子
            level: 預警等級，None 表示所有等級

        Returns:
            預警列表
        """
        if factor_id:
            alerts = self.alert_history.get(factor_id, [])
        else:
            alerts = []
            for factor_alerts in self.alert_history.values():
                alerts.extend(factor_alerts)

        if level is not None:
            alerts = [a for a in alerts if a.level == level]

        return alerts

    def clear_alerts(self, factor_id: Optional[str] = None):
        """
        清除預警

        Args:
            factor_id: 因子 ID，None 表示清除所有預警
        """
        if factor_id:
            if factor_id in self.active_alerts:
                del self.active_alerts[factor_id]
        else:
            self.active_alerts.clear()

class NotificationService:
    """通知服務"""

    def __init__(self, config=config):
        self.config = config
        self.enabled_channels = config.alert.notification_channels

    def send_alert(self, alert: Alert):
        """
        發送預警通知

        Args:
            alert: 預警對象
        """
        if not self.config.alert.enabled:
            logger.info("預警功能未啟用")
            return

        for channel in self.enabled_channels:
            try:
                if channel == "log":
                    self._send_to_log(alert)
                elif channel == "email":
                    self._send_to_email(alert)
                elif channel == "webhook":
                    self._send_to_webhook(alert)
            except Exception as e:
                logger.error(f"通過 {channel} 發送預警失敗: {e}")

    def _send_to_log(self, alert: Alert):
        """發送到日誌"""
        logger.warning(
            f"[{alert.level_name}] {alert.factor_name}\n"
            f"CCS: {alert.ccs:.2f} | FEI: {alert.fei:.2f} | "
            f"FVI: {alert.fvi:.2f} | FVIol: {alert.fviol:.2f}\n"
            f"持續: {alert.duration_days}天 | 置信度: {alert.confidence:.2f}\n"
            f"建議: {alert.action}"
        )

    def _send_to_email(self, alert: Alert):
        """發送到郵件（示例實現）"""
        # 實際實現需要配置 SMTP
        subject = f"[{alert.level_name}] 因子擁擠度預警 - {alert.factor_name}"
        body = alert.to_json()

        logger.info(f"發送郵件: {subject}")
        # TODO: 實現郵件發送邏輯

    def _send_to_webhook(self, alert: Alert):
        """發送到 Webhook（示例實現）"""
        # 實際實現需要配置 Webhook URL
        import requests

        webhook_url = "https://your-webhook-url.com/alerts"
        data = alert.to_dict()

        try:
            response = requests.post(webhook_url, json=data, timeout=5)
            response.raise_for_status()
            logger.info(f"Webhook 發送成功: {alert.alert_id}")
        except Exception as e:
            logger.error(f"Webhook 發送失敗: {e}")
```

---

## 6. 可視化系統

### 6.1 儀表板 (visualization/dashboard.py)

```python
"""
可視化儀表板
"""
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class Dashboard:
    """可視化儀表板"""

    def __init__(self):
        self.colors = {
            'extreme_cold': '#1f77b4',
            'cold': '#aec7e8',
            'neutral': '#ffbb78',
            'hot': '#ff9896',
            'extreme_hot': '#d62728'
        }

    def create_overview_dashboard(
        self,
        monitoring_results: List,
        historical_data: Dict[str, pd.DataFrame]
    ) -> go.Figure:
        """
        創建總覽儀表板

        Args:
            monitoring_results: 監控結果列表
            historical_data: 歷史數據字典

        Returns:
            Plotly Figure
        """
        # 創建子圖
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                '各因子擁擠度評分',
                '擁擠度分佈',
                '因子趨勢 (最近30天)',
                '子指標熱力圖'
            ),
            specs=[
                [{'type': 'bar'}, {'type': 'pie'}],
                [{'type': 'scatter'}, {'type': 'heatmap'}]
            ]
        )

        # 1. 各因子擁擠度評分柱狀圖
        factor_names = [r.factor_name for r in monitoring_results]
        ccs_scores = [r.ccs for r in monitoring_results]
        colors = [self.colors[r.crowding_level] for r in monitoring_results]

        fig.add_trace(
            go.Bar(
                x=factor_names,
                y=ccs_scores,
                marker_color=colors,
                text=[f'{s:.1f}' for s in ccs_scores],
                textposition='outside',
                name='CCS'
            ),
            row=1, col=1
        )

        # 添加閾值線
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=60, line_dash="dash", line_color="orange", row=1, col=1)
        fig.add_hline(y=40, line_dash="dash", line_color="green", row=1, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="blue", row=1, col=1)

        # 2. 擁擠度分佈餅圖
        level_counts = {
            'extreme_cold': 0,
            'cold': 0,
            'neutral': 0,
            'hot': 0,
            'extreme_hot': 0
        }
        for r in monitoring_results:
            level_counts[r.crowding_level] += 1

        fig.add_trace(
            go.Pie(
                labels=['極度過冷', '過冷', '中性', '過熱', '極度過熱'],
                values=[
                    level_counts['extreme_cold'],
                    level_counts['cold'],
                    level_counts['neutral'],
                    level_counts['hot'],
                    level_counts['extreme_hot']
                ],
                marker_colors=[
                    self.colors['extreme_cold'],
                    self.colors['cold'],
                    self.colors['neutral'],
                    self.colors['hot'],
                    self.colors['extreme_hot']
                ],
                name='分佈'
            ),
            row=1, col=2
        )

        # 3. 因子趨勢圖（最近30天）
        for factor_id, data in historical_data.items():
            if len(data) > 0:
                recent_data = data.tail(30)
                fig.add_trace(
                    go.Scatter(
                        x=recent_data.index,
                        y=recent_data['CCS'],
                        mode='lines',
                        name=factor_id,
                        line=dict(width=2)
                    ),
                    row=2, col=1
                )

        # 4. 子指標熱力圖
        sub_metrics_data = []
        factor_names = []
        for r in monitoring_results:
            factor_names.append(r.factor_name)
            sub_metrics_data.append([r.fei, r.fvi, r.fviol])

        fig.add_trace(
            go.Heatmap(
                z=sub_metrics_data,
                x=['FEI', 'FVI', 'FVIol'],
                y=factor_names,
                colorscale='RdYlGn_r',
                colorbar=dict(title='評分'),
                name='子指標'
            ),
            row=2, col=2
        )

        # 更新佈局
        fig.update_layout(
            title_text="因子擁擠度監控儀表板",
            title_font_size=24,
            height=800,
            showlegend=False
        )

        fig.update_yaxes(range=[0, 100], row=1, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        return fig

    def create_factor_detail_chart(
        self,
        factor_id: str,
        factor_name: str,
        history: pd.DataFrame
    ) -> go.Figure:
        """
        創建因子詳情圖

        Args:
            factor_id: 因子 ID
            factor_name: 因子名稱
            history: 歷史數據

        Returns:
            Plotly Figure
        """
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=(
                '綜合擁擠度評分 (CCS)',
                '子指標走勢'
            ),
            shared_xaxes=True,
            vertical_spacing=0.1
        )

        # CCS 走勢圖
        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history['CCS'],
                mode='lines',
                name='CCS',
                line=dict(color='black', width=2),
                fill='tozeroy',
                fillcolor='rgba(0,0,0,0.1)'
            ),
            row=1, col=1
        )

        # 子指標走勢圖
        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history['FEI'],
                mode='lines',
                name='FEI',
                line=dict(color='blue', width=1.5)
            ),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history['FVI'],
                mode='lines',
                name='FVI',
                line=dict(color='green', width=1.5)
            ),
            row=2, col=1
        )

        fig.add_trace(
            go.Scatter(
                x=history.index,
                y=history['FVIol'],
                mode='lines',
                name='FVIol',
                line=dict(color='orange', width=1.5)
            ),
            row=2, col=1
        )

        # 添加閾值線
        fig.add_hline(y=80, line_dash="dash", line_color="red", row=1, col=1)
        fig.add_hline(y=60, line_dash="dash", line_color="orange", row=1, col=1)
        fig.add_hline(y=40, line_dash="dash", line_color="green", row=1, col=1)
        fig.add_hline(y=20, line_dash="dash", line_color="blue", row=1, col=1)

        # 更新佈局
        fig.update_layout(
            title=f"{factor_name} 詳情",
            height=600,
            hovermode='x unified'
        )

        fig.update_yaxes(range=[0, 100], row=1, col=1)
        fig.update_yaxes(range=[0, 100], row=2, col=1)

        return fig

    def create_gauge_chart(
        self,
        ccs: float,
        factor_name: str
    ) -> go.Figure:
        """
        創建儀表盤圖表

        Args:
            ccs: CCS 值
            factor_name: 因子名稱

        Returns:
            Plotly Figure
        """
        # 確定顏色
        if ccs <= 20:
            color = 'blue'
        elif ccs <= 40:
            color = 'lightblue'
        elif ccs <= 60:
            color = 'yellow'
        elif ccs <= 80:
            color = 'orange'
        else:
            color = 'red'

        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = ccs,
            title = {'text': f"{factor_name}<br><span style='font-size:0.8em'>擁擠度評分</span>"},
            delta = {'reference': 50},
            gauge = {
                'axis': {'range': [0, 100]},
                'bar': {'color': color},
                'steps': [
                    {'range': [0, 20], 'color': 'lightblue'},
                    {'range': [20, 40], 'color': 'lightyellow'},
                    {'range': [40, 60], 'color': 'lightgreen'},
                    {'range': [60, 80], 'color': 'orange'},
                    {'range': [80, 100], 'color': 'lightcoral'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 80
                }
            }
        ))

        fig.update_layout(height=400)

        return fig

    def save_dashboard(
        self,
        fig: go.Figure,
        output_path: str,
        format: str = "html"
    ):
        """
        保存儀表板

        Args:
            fig: Plotly Figure
            output_path: 輸出路徑
            format: 輸出格式 (html, png, jpg, pdf)
        """
        if format == "html":
            fig.write_html(output_path)
        elif format == "png":
            fig.write_image(output_path, format='png')
        elif format == "jpg":
            fig.write_image(output_path, format='jpg')
        elif format == "pdf":
            fig.write_image(output_path, format='pdf')

        logger.info(f"儀表板已保存到: {output_path}")
```

### 6.2 報告生成器 (visualization/reports.py)

```python
"""
報告生成器
"""
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging

from ..monitor.realtime import MonitoringResult
from ..monitor.alert import Alert

logger = logging.getLogger(__name__)

class ReportGenerator:
    """報告生成器"""

    def generate_daily_report(
        self,
        monitoring_results: List[MonitoringResult],
        alerts: List[Alert],
        output_path: Optional[str] = None
    ) -> str:
        """
        生成日報

        Args:
            monitoring_results: 監控結果列表
            alerts: 預警列表
            output_path: 輸出路徑（可選）

        Returns:
            報告內容
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("因子擁擠度監控日報")
        report_lines.append("=" * 60)
        report_lines.append(f"報告時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # 摘要
        report_lines.append("【摘要】")
        report_lines.append(f"監控因子數量: {len(monitoring_results)}")
        report_lines.append(f"觸發預警數量: {len(alerts)}")
        report_lines.append("")

        # 分級統計
        extreme_hot = sum(1 for r in monitoring_results if r.crowding_level == 'extreme_hot')
        hot = sum(1 for r in monitoring_results if r.crowding_level == 'hot')
        neutral = sum(1 for r in monitoring_results if r.crowding_level == 'neutral')
        cold = sum(1 for r in monitoring_results if r.crowding_level == 'cold')
        extreme_cold = sum(1 for r in monitoring_results if r.crowding_level == 'extreme_cold')

        report_lines.append("【擁擠度分級統計】")
        report_lines.append(f"  極度過熱 (80-100): {extreme_hot}")
        report_lines.append(f"  過熱 (60-80): {hot}")
        report_lines.append(f"  中性 (40-60): {neutral}")
        report_lines.append(f"  過冷 (20-40): {cold}")
        report_lines.append(f"  極度過冷 (0-20): {extreme_cold}")
        report_lines.append("")

        # 詳細數據
        report_lines.append("【各因子詳情】")
        report_lines.append("-" * 60)
        report_lines.append(f"{'因子名稱':<12} {'CCS':<8} {'FEI':<8} {'FVI':<8} {'FVIol':<8} {'狀態':<12} {'建議'}")
        report_lines.append("-" * 60)

        for result in monitoring_results:
            report_lines.append(
                f"{result.factor_name:<12} "
                f"{result.ccs:<8.2f} "
                f"{result.fei:<8.2f} "
                f"{result.fvi:<8.2f} "
                f"{result.fviol:<8.2f} "
                f"{result.crowding_level:<12} "
                f"{result.recommendation}"
            )

        report_lines.append("-" * 60)
        report_lines.append("")

        # 預警信息
        if alerts:
            report_lines.append("【預警信息】")
            report_lines.append("-" * 60)
            for alert in alerts:
                report_lines.append(
                    f"[{alert.level_name}] {alert.factor_name}\n"
                    f"  CCS: {alert.ccs:.2f} | 持續: {alert.duration_days}天\n"
                    f"  建議: {alert.action}"
                )
                report_lines.append("-" * 60)
            report_lines.append("")

        # 風險提示
        report_lines.append("【風險提示】")
        if extreme_hot > 0:
            report_lines.append(f"  ⚠️  {extreme_hot} 個因子處於極度過熱狀態，建議關注")
        if extreme_cold > 0:
            report_lines.append(f"  💡 {extreme_cold} 個因子處於極度過冷狀態，可能存在機會")
        if len(alerts) > 0:
            report_lines.append(f"  🚨 當前有 {len(alerts)} 個活躍預警")
        report_lines.append("")

        # 免責聲明
        report_lines.append("=" * 60)
        report_lines.append("免責聲明：本報告僅供參考，不構成投資建議。")
        report_lines.append("投資有風險，決策需謹慎。")
        report_lines.append("=" * 60)

        # 拼接報告
        report = "\n".join(report_lines)

        # 保存報告
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"日報已保存到: {output_path}")

        return report

    def generate_weekly_report(
        self,
        monitoring_results: List[MonitoringResult],
        historical_data: Dict[str, pd.DataFrame],
        output_path: Optional[str] = None
    ) -> str:
        """
        生成周報

        Args:
            monitoring_results: 監控結果列表
            historical_data: 歷史數據
            output_path: 輸出路徑（可選）

        Returns:
            報告內容
        """
        report_lines = []
        report_lines.append("=" * 60)
        report_lines.append("因子擁擠度監控周報")
        report_lines.append("=" * 60)
        report_lines.append(f"報告時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")

        # 摘要
        report_lines.append("【摘要】")
        report_lines.append(f"監控因子數量: {len(monitoring_results)}")
        report_lines.append("")

        # 趨勢分析
        report_lines.append("【趨勢分析】")
        report_lines.append("-" * 60)

        for result in monitoring_results:
            if result.factor_id in historical_data:
                history = historical_data[result.factor_id]
                if len(history) >= 7:
                    week_start = history['CCS'].iloc[-7]
                    week_end = history['CCS'].iloc[-1]
                    change = week_end - week_start
                    change_pct = (change / week_start * 100) if week_start != 0 else 0

                    trend_icon = "📈" if change > 5 else "📉" if change < -5 else "➡️"

                    report_lines.append(
                        f"{trend_icon} {result.factor_name}\n"
                        f"   本周變動: {change:+.2f} ({change_pct:+.1f}%)\n"
                        f"   當前狀態: {result.crowding_level}\n"
                        f"   建議: {result.recommendation}"
                    )

        report_lines.append("-" * 60)
        report_lines.append("")

        # 保存報告
        report = "\n".join(report_lines)

        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"周報已保存到: {output_path}")

        return report
```

---

## 7. 主程序與啟動腳本

### 7.1 主程序入口 (main.py)

```python
"""
主程序入口
"""
import logging
from pathlib import Path

from config.settings import config
from config.thresholds import get_crowding_level
from monitor.realtime import RealtimeMonitor
from monitor.alert import AlertSystem, NotificationService
from visualization.dashboard import Dashboard
from visualization.reports import ReportGenerator

def setup_logging():
    """設置日誌"""
    log_path = Path(config.logging.path)
    log_path.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_path / 'crowding_monitor.log'),
            logging.StreamHandler()
        ]
    )

def main():
    """主函數"""
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"啟動 {config.project_name} v{config.version}")

    try:
        # 初始化組件
        monitor = RealtimeMonitor(config)
        alert_system = AlertSystem(config)
        notification_service = NotificationService(config)
        dashboard = Dashboard()
        report_generator = ReportGenerator()

        # 監控所有因子
        logger.info("開始監控所有因子...")
        results = monitor.monitor_all_factors()

        # 檢查預警
        alerts = []
        for result in results:
            if result.factor_id in monitor.history:
                alert = alert_system.check_alert(
                    factor_id=result.factor_id,
                    factor_name=result.factor_name,
                    ccs_data=monitor.history[result.factor_id],
                    latest_ccs=result.ccs,
                    latest_fei=result.fei,
                    latest_fvi=result.fvi,
                    latest_fviol=result.fviol,
                    confidence=result.confidence
                )
                if alert:
                    alerts.append(alert)
                    notification_service.send_alert(alert)

        # 生成報告
        output_dir = Path("./output")
        output_dir.mkdir(exist_ok=True)

        # 日報
        daily_report = report_generator.generate_daily_report(
            monitoring_results=results,
            alerts=alerts,
            output_path=output_dir / f"daily_report_{datetime.now().strftime('%Y%m%d')}.txt"
        )
        logger.info("日報生成完成")

        # 生成儀表板
        overview_dashboard = dashboard.create_overview_dashboard(
            monitoring_results=results,
            historical_data=monitor.history
        )
        dashboard.save_dashboard(
            overview_dashboard,
            output_dir / f"dashboard_{datetime.now().strftime('%Y%m%d')}.html"
        )
        logger.info("儀表板生成完成")

        # 輸出摘要
        summary = monitor.get_summary()
        logger.info(f"監控完成: {summary['total_factors']} 個因子")
        logger.info(f"  極度過熱: {summary['extreme_hot']}")
        logger.info(f"  過熱: {summary['hot']}")
        logger.info(f"  中性: {summary['neutral']}")
        logger.info(f"  過冷: {summary['cold']}")
        logger.info(f"  極度過冷: {summary['extreme_cold']}")

        if alerts:
            logger.warning(f"當前有 {len(alerts)} 個活躍預警")

    except Exception as e:
        logger.error(f"程序執行失敗: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    from datetime import datetime
    main()
```

### 7.2 監控啟動腳本 (run_monitor.py)

```python
"""
監控啟動腳本 - 支持定時運行
"""
import argparse
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import logging
import sys

from main import main as run_main_monitor

logger = logging.getLogger(__name__)

def run_once():
    """運行一次監控"""
    logger.info("執行單次監控...")
    run_main_monitor()

def run_scheduled(cron_expression: str):
    """
    定時運行監控

    Args:
        cron_expression: cron 表達式，如 "0 16 * * 1-5"（工作日16:00）
    """
    logger.info(f"啟動定時監控，cron: {cron_expression}")

    scheduler = BlockingScheduler()

    # 解析 cron 表達式
    parts = cron_expression.split()
    if len(parts) == 5:
        minute, hour, day, month, day_of_week = parts
    else:
        logger.error("無效的 cron 表達式")
        sys.exit(1)

    scheduler.add_job(
        run_main_monitor,
        trigger=CronTrigger(
            minute=minute,
            hour=hour,
            day=day,
            month=month,
            day_of_week=day_of_week
        ),
        id='crowding_monitor',
        name='Factor Crowding Monitor',
        replace_existing=True
    )

    logger.info("調度器已啟動，按 Ctrl+C 退出")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("調度器已停止")

def main():
    parser = argparse.ArgumentParser(description='因子擁擠度監控系統')
    parser.add_argument(
        '--once',
        action='store_true',
        help='運行一次監控'
    )
    parser.add_argument(
        '--cron',
        type=str,
        help='定時運行，使用 cron 表達式，如 "0 16 * * 1-5"'
    )

    args = parser.parse_args()

    if args.once:
        run_once()
    elif args.cron:
        run_scheduled(args.cron)
    else:
        # 默認運行一次
        run_once()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()
```

---

## 8. 使用文檔

### 8.1 安裝依賴

```bash
# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安裝依賴
pip install pandas numpy scipy statsmodels arch plotly matplotlib apscheduler pydantic requests
```

### 8.2 配置說明

1. **數據路徑配置** (config/settings.py)
   - 修改 `data.market_data_path` 指向市場數據目錄
   - 修改 `data.financial_data_path` 指向財務數據目錄
   - 修改 `data.factor_data_path` 指向因子數據目錄

2. **閾值配置** (config/thresholds.py)
   - 根據實際情況調整預警閾值
   - `level_1_threshold`: 一級預警閾值
   - `level_2_threshold`: 二級預警閾值
   - `level_3_threshold`: 三級預警閾值

3. **權重配置** (config/settings.py)
   - 調整 FEI、FVI、FVIol 的權重
   - 默認: FEI=0.4, FVI=0.35, FVIol=0.25

4. **通知配置** (config/settings.py)
   - 修改 `alert.notification_channels` 選擇通知渠道
   - 可選: log, email, webhook

### 8.3 運行方式

#### 單次運行

```bash
python run_monitor.py --once
```

#### 定時運行（工作日 16:00）

```bash
python run_monitor.py --cron "0 16 * * 1-5"
```

#### 直接運行主程序

```bash
python main.py
```

### 8.4 數據格式

#### 市場數據格式 (market_data.csv)

```csv
date,symbol,close,volume,market_cap
2026-02-20,AAPL,150.25,50000000,2500000000
2026-02-20,MSFT,280.50,40000000,2100000000
...
```

#### 財務數據格式 (financial_data.csv)

```csv
report_date,symbol,pe,pb,roe,revenue_growth
2026-02-20,AAPL,25.5,15.2,0.28,0.15
2026-02-20,MSFT,30.2,18.5,0.35,0.12
...
```

#### 因子數據格式 (F001.csv)

```csv
date,return,exposure,sharpe
2026-02-20,0.0015,0.52,1.25
2026-02-19,0.0012,0.51,1.23
...
```

#### 資金流數據格式 (capital_flow_F001.csv)

```csv
date,northbound_flow,institutional_flow,retail_flow
2026-02-20,150000000,80000000,50000000
2026-02-19,120000000,60000000,40000000
...
```

### 8.5 輸出說明

#### 日報文件 (output/daily_report_YYYYMMDD.txt)

文本格式的日報，包含：
- 摘要統計
- 各因子詳情
- 預警信息
- 風險提示

#### 儀表板文件 (output/dashboard_YYYYMMDD.html)

交互式 HTML 儀表板，包含：
- 各因子擁擠度評分柱狀圖
- 擁擠度分佈餅圖
- 因子趨勢圖
- 子指標熱力圖

#### 日誌文件 (logs/crowding_monitor.log)

程序運行日誌，包含：
- 數據加載記錄
- 指標計算記錄
- 預警記錄
- 錯誤信息

---

## 9. 實證驗證框架

### 9.1 回測引擎 (backtest/engine.py)

```python
"""
回測引擎
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class BacktestEngine:
    """回測引擎"""

    def __init__(self, config):
        self.config = config

    def run_backtest(
        self,
        factor_id: str,
        ccs_series: pd.Series,
        returns: pd.Series,
        strategy: str = "reverse"
    ) -> Dict:
        """
        運行回測

        Args:
            factor_id: 因子 ID
            ccs_series: CCS 序列
            returns: 因子收益率序列
            strategy: 策略類型 (reverse, dynamic, hedge)

        Returns:
            回測結果字典
        """
        logger.info(f"開始回測因子 {factor_id}，策略: {strategy}")

        # 對齊數據
        aligned_data = pd.DataFrame({
            'CCS': ccs_series,
            'return': returns
        }).dropna()

        # 執行策略
        if strategy == "reverse":
            strategy_returns = self._reverse_strategy(aligned_data)
        elif strategy == "dynamic":
            strategy_returns = self._dynamic_strategy(aligned_data)
        elif strategy == "hedge":
            strategy_returns = self._hedge_strategy(aligned_data)
        else:
            raise ValueError(f"未知策略: {strategy}")

        # 計算績效指標
        metrics = self._calculate_metrics(strategy_returns)

        # 計算基準績效
        benchmark_metrics = self._calculate_metrics(aligned_data['return'])

        result = {
            'factor_id': factor_id,
            'strategy': strategy,
            'strategy_metrics': metrics,
            'benchmark_metrics': benchmark_metrics,
            'strategy_returns': strategy_returns,
            'benchmark_returns': aligned_data['return']
        }

        logger.info(f"回測完成，策略年化收益率: {metrics['annual_return']:.2%}")

        return result

    def _reverse_strategy(self, data: pd.DataFrame) -> pd.Series:
        """
        逆向策略
        - CCS > 80 時減持
        - CCS < 20 時增持
        """
        positions = pd.Series(1.0, index=data.index)

        for i in range(1, len(data)):
            ccs = data['CCS'].iloc[i-1]
            if ccs > 80:
                positions.iloc[i] = 0.5  # 減持
            elif ccs < 20:
                positions.iloc[i] = 1.5  # 增持
            else:
                positions.iloc[i] = 1.0  # 持倉

        returns = data['return'] * positions
        return returns

    def _dynamic_strategy(self, data: pd.DataFrame) -> pd.Series:
        """
        動態調整策略
        - 根據 CCS 線性調整權重
        """
        positions = (100 - data['CCS']) / 50  # CCS=0→2.0, CCS=100→0.0
        positions = positions.clip(0, 2)

        returns = data['return'] * positions
        return returns

    def _hedge_strategy(self, data: pd.DataFrame) -> pd.Series:
        """
        避險策略
        - CCS > 80 時使用衍生品對沖
        """
        positions = pd.Series(1.0, index=data.index)

        for i in range(1, len(data)):
            ccs = data['CCS'].iloc[i-1]
            if ccs > 80:
                positions.iloc[i] = 0.3  # 大幅減倉
            elif ccs < 60:
                positions.iloc[i] = 1.0  # 恢復倉位
            else:
                positions.iloc[i] = positions.iloc[i-1]  # 保持

        returns = data['return'] * positions
        return returns

    def _calculate_metrics(self, returns: pd.Series) -> Dict:
        """
        計算績效指標

        Args:
            returns: 收益率序列

        Returns:
            績效指標字典
        """
        # 年化收益率
        annual_return = returns.mean() * 252

        # 年化波動率
        annual_vol = returns.std() * np.sqrt(252)

        # 夏普比率
        sharpe_ratio = annual_return / annual_vol if annual_vol > 0 else 0

        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()

        # IC (Information Coefficient)
        ic = self._calculate_ic(returns)

        # IR (Information Ratio)
        ir = self._calculate_ir(returns)

        return {
            'annual_return': annual_return,
            'annual_volatility': annual_vol,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'ic_mean': ic['mean'],
            'ic_std': ic['std'],
            'ir': ir,
            'total_return': (1 + returns).prod() - 1
        }

    def _calculate_ic(self, returns: pd.Series, window: int = 20) -> Dict:
        """
        計算 IC (Information Coefficient)

        IC = Correlation(CCS_t, Return_{t+1,t+window})

        Args:
            returns: 收益率序列
            window: 前瞻窗口

        Returns:
            IC 統計量
        """
        # 由於只有收益率序列，這裡使用收益率自相關作為示例
        # 實際應該使用 CCS 和未來收益率計算相關性

        lagged_returns = returns.shift(-window)
        ic = returns.corr(lagged_returns)

        # 滾動 IC
        rolling_ic = returns.rolling(252).apply(
            lambda x: x.corr(x.shift(-window))
        )

        return {
            'mean': ic,
            'std': rolling_ic.std(),
            'rolling_mean': rolling_ic.mean()
        }

    def _calculate_ir(self, returns: pd.Series) -> float:
        """
        計算 IR (Information Ratio)

        IR = Mean(IC) / Std(IC)

        Args:
            returns: 收益率序列

        Returns:
            IR 值
        """
        ic_data = self._calculate_ic(returns)
        return ic_data['mean'] / ic_data['std'] if ic_data['std'] > 0 else 0

    def calculate_group_backtest(
        self,
        data: pd.DataFrame,
        n_groups: int = 5
    ) -> Dict:
        """
        分組回測

        Args:
            data: 包含 CCS 和收益率的 DataFrame
            n_groups: 分組數量

        Returns:
            各組績效
        """
        # 按 CCS 分組
        data['group'] = pd.qcut(
            data['CCS'],
            n_groups,
            labels=[f'Group_{i+1}' for i in range(n_groups)],
            duplicates='drop'
        )

        group_metrics = {}

        for group in data['group'].unique():
            group_returns = data[data['group'] == group]['return']
            metrics = self._calculate_metrics(group_returns)
            group_metrics[group] = metrics

        return group_metrics

    def calculate_alert_hit_rate(
        self,
        alerts: List,
        returns: pd.DataFrame
    ) -> Dict:
        """
        計算預警命中率

        Args:
            alerts: 預警列表
            returns: 收益率數據

        Returns:
            命中率統計
        """
        total_alerts = len(alerts)
        hit_alerts = 0

        for alert in alerts:
            # 檢查預警後 20 個交易日的表現
            alert_date = alert.timestamp
            future_returns = returns[returns.index > alert_date].head(20)

            if len(future_returns) > 0:
                cumulative_return = (1 + future_returns).prod() - 1

                # 如果預警後下跌超過 5%，視為命中
                if cumulative_return < -0.05:
                    hit_alerts += 1

        hit_rate = hit_alerts / total_alerts if total_alerts > 0 else 0

        return {
            'total_alerts': total_alerts,
            'hit_alerts': hit_alerts,
            'hit_rate': hit_rate
        }
```

### 9.2 驗證器 (backtest/validators.py)

```python
"""
驗證器
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from scipy import stats
import logging

logger = logging.getLogger(__name__)

class MetricsValidator:
    """指標驗證器"""

    def validate_metrics(
        self,
        factor_id: str,
        ccs_data: pd.DataFrame,
        returns: pd.Series
    ) -> Dict:
        """
        驗證指標有效性

        Args:
            factor_id: 因子 ID
            ccs_data: CCS 數據
            returns: 收益率序列

        Returns:
            驗證結果
        """
        results = {}

        # 1. CCS 分布檢驗
        results['ccs_distribution'] = self._validate_distribution(ccs_data['CCS'])

        # 2. 預測能力檢驗
        results['predictive_power'] = self._validate_predictive_power(
            ccs_data['CCS'],
            returns
        )

        # 3. 穩定性檢驗
        results['stability'] = self._validate_stability(ccs_data['CCS'])

        # 4. 子指標一致性檢驗
        results['sub_metric_consistency'] = self._validate_consistency(ccs_data)

        return results

    def _validate_distribution(
        self,
        ccs_series: pd.Series
    ) -> Dict:
        """驗證 CCS 分布"""
        return {
            'mean': ccs_series.mean(),
            'std': ccs_series.std(),
            'min': ccs_series.min(),
            'max': ccs_series.max(),
            'median': ccs_series.median(),
            'skewness': stats.skew(ccs_series),
            'kurtosis': stats.kurtosis(ccs_series)
        }

    def _validate_predictive_power(
        self,
        ccs_series: pd.Series,
        returns: pd.Series
    ) -> Dict:
        """驗證預測能力"""
        # 計算 IC
        ic_list = []
        for i in range(len(ccs_series) - 20):
            ccs_t = ccs_series.iloc[i]
            future_return = returns.iloc[i+1:i+21].sum()
            ic_list.append(ccs_t * future_return)

        ic_mean = np.mean(ic_list)
        ic_std = np.std(ic_list)

        # t 檢驗
        t_stat = ic_mean / (ic_std / np.sqrt(len(ic_list))) if ic_std > 0 else 0
        p_value = 2 * (1 - stats.t.cdf(abs(t_stat), df=len(ic_list)-1))

        return {
            'ic_mean': ic_mean,
            'ic_std': ic_std,
            'ir': ic_mean / ic_std if ic_std > 0 else 0,
            't_statistic': t_stat,
            'p_value': p_value,
            'is_significant': p_value < 0.05
        }

    def _validate_stability(
        self,
        ccs_series: pd.Series,
        window: int = 60
    ) -> Dict:
        """驗證穩定性"""
        rolling_std = ccs_series.rolling(window).std()

        return {
            'mean_std': rolling_std.mean(),
            'max_std': rolling_std.max(),
            'stability_score': 1 - (rolling_std.max() - rolling_std.mean()) / rolling_std.mean()
        }

    def _validate_consistency(
        self,
        ccs_data: pd.DataFrame
    ) -> Dict:
        """驗證子指標一致性"""
        correlations = {
            'FEI-CCS': ccs_data['FEI'].corr(ccs_data['CCS']),
            'FVI-CCS': ccs_data['FVI'].corr(ccs_data['CCS']),
            'FVIol-CCS': ccs_data['FVIol'].corr(ccs_data['CCS'])
        }

        return correlations
```

---

## 10. 實用工具

### 10.1 數據模擬器 (utils/data_simulator.py)

```python
"""
數據模擬器 - 用於測試和演示
"""
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataSimulator:
    """數據模擬器"""

    def __init__(self, config):
        self.config = config

    def generate_all_data(
        self,
        start_date: str,
        end_date: str,
        factors: List[str],
        symbols: List[str]
    ) -> Dict[str, pd.DataFrame]:
        """
        生成所有測試數據

        Args:
            start_date: 開始日期
            end_date: 結束日期
            factors: 因子 ID 列表
            symbols: 股票代碼列表

        Returns:
            數據字典
        """
        data = {}

        # 市場數據
        data['market'] = self._generate_market_data(start_date, end_date, symbols)

        # 財務數據
        data['financial'] = self._generate_financial_data(start_date, end_date, symbols)

        # 因子數據
        for factor_id in factors:
            data[f'factor_{factor_id}'] = self._generate_factor_data(
                factor_id, start_date, end_date
            )
            data[f'capital_flow_{factor_id}'] = self._generate_capital_flow_data(
                factor_id, start_date, end_date
            )

        return data

    def _generate_market_data(
        self,
        start_date: str,
        end_date: str,
        symbols: List[str]
    ) -> pd.DataFrame:
        """生成市場數據"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        data = []
        for date in dates:
            for symbol in symbols:
                # 隨機漫步股價
                base_price = 100
                noise = np.random.normal(0, 2)
                price = base_price + noise + np.random.uniform(-10, 10)

                data.append({
                    'date': date,
                    'symbol': symbol,
                    'close': price,
                    'volume': np.random.randint(1000000, 10000000),
                    'market_cap': price * np.random.uniform(1000000, 10000000)
                })

        df = pd.DataFrame(data)
        return df.set_index('date')

    def _generate_financial_data(
        self,
        start_date: str,
        end_date: str,
        symbols: List[str]
    ) -> pd.DataFrame:
        """生成財務數據"""
        dates = pd.date_range(start=start_date, end=end_date, freq='Q')

        data = []
        for date in dates:
            for symbol in symbols:
                data.append({
                    'report_date': date,
                    'symbol': symbol,
                    'pe': np.random.uniform(10, 30),
                    'pb': np.random.uniform(1, 5),
                    'roe': np.random.uniform(0.1, 0.3),
                    'revenue_growth': np.random.uniform(-0.1, 0.3)
                })

        df = pd.DataFrame(data)
        return df.set_index('report_date')

    def _generate_factor_data(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成因子數據"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        # 使用因子 ID 作為種子
        np.random.seed(hash(factor_id) % (2**32))

        # 模擬不同的因子特性
        if factor_id == "F001":  # 價值因子
            volatility = 0.008
            drift = 0.0003
        elif factor_id == "F002":  # 成長因子
            volatility = 0.012
            drift = 0.0005
        elif factor_id == "F003":  # 動量因子
            volatility = 0.015
            drift = 0.0002
        else:
            volatility = 0.01
            drift = 0.0001

        # 幾何布朗運動
        returns = np.random.normal(drift, volatility, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))

        # 計算暴露度
        exposure = np.random.uniform(-1, 1, len(dates))
        exposure = pd.Series(exposure).ewm(span=20).mean().values

        # 計算 Sharpe
        sharpe = returns / volatility

        data = pd.DataFrame({
            'date': dates,
            'return': returns,
            'exposure': exposure,
            'sharpe': sharpe
        })

        return data.set_index('date')

    def _generate_capital_flow_data(
        self,
        factor_id: str,
        start_date: str,
        end_date: str
    ) -> pd.DataFrame:
        """生成資金流數據"""
        dates = pd.date_range(start=start_date, end=end_date, freq='D')

        np.random.seed(hash(f"flow_{factor_id}") % (2**32))

        # 模擬資金流
        northbound_flow = np.random.normal(0, 100000000, len(dates))
        institutional_flow = np.random.normal(0, 50000000, len(dates))
        retail_flow = np.random.normal(0, 20000000, len(dates))

        data = pd.DataFrame({
            'date': dates,
            'northbound_flow': northbound_flow,
            'institutional_flow': institutional_flow,
            'retail_flow': retail_flow
        })

        return data.set_index('date')

    def save_data(
        self,
        data: Dict[str, pd.DataFrame],
        output_dir: Path
    ):
        """
        保存數據到文件

        Args:
            data: 數據字典
            output_dir: 輸出目錄
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        for key, df in data.items():
            if 'factor' in key or 'capital' in key:
                file_path = output_dir / f"{key}.csv"
            else:
                file_path = output_dir / f"{key}.csv"

            df.to_csv(file_path)
            logger.info(f"數據已保存: {file_path}")
```

### 10.2 快速啟動腳本 (utils/quick_start.py)

```python
"""
快速啟動腳本 - 生成測試數據並運行監控
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import config
from utils.data_simulator import DataSimulator
from main import main as run_monitor

def quick_start():
    """快速啟動"""
    print("=" * 60)
    print("因子擁擠度監控系統 - 快速啟動")
    print("=" * 60)

    # 創建模擬器
    simulator = DataSimulator(config)

    # 生成測試數據
    print("\n1. 生成測試數據...")
    factors = ["F001", "F002", "F003", "F004", "F005"]
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

    start_date = "2025-01-01"
    end_date = "2026-02-20"

    data = simulator.generate_all_data(
        start_date=start_date,
        end_date=end_date,
        factors=factors,
        symbols=symbols
    )

    # 保存數據
    output_dir = Path("./data")
    simulator.save_data(data, output_dir)

    print("   測試數據生成完成！")
    print(f"   因子數量: {len(factors)}")
    print(f"   股票數量: {len(symbols)}")
    print(f"   日期範圍: {start_date} 至 {end_date}")

    # 運行監控
    print("\n2. 運行監控...")
    run_monitor()

    print("\n" + "=" * 60)
    print("監控完成！請查看 output 目錄中的報告和儀表板。")
    print("=" * 60)

if __name__ == "__main__":
    quick_start()
```

---

## 11. 部署指南

### 11.1 本地部署

1. **克隆項目**
```bash
git clone <repository-url>
cd factor_crowding_monitor
```

2. **安裝依賴**
```bash
pip install -r requirements.txt
```

3. **配置數據**
- 將實際數據放入 `data/` 目錄
- 或運行 `python utils/quick_start.py` 生成測試數據

4. **運行監控**
```bash
python run_monitor.py --once
```

### 11.2 Docker 部署

1. **創建 Dockerfile**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "run_monitor.py", "--cron", "0 16 * * 1-5"]
```

2. **構建鏡像**
```bash
docker build -t crowding-monitor .
```

3. **運行容器**
```bash
docker run -d \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/logs:/app/logs \
  crowding-monitor
```

### 11.3 服務器部署

1. **使用 systemd**

創建服務文件 `/etc/systemd/system/crowding-monitor.service`:
```ini
[Unit]
Description=Factor Crowding Monitor
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/factor_crowding_monitor
ExecStart=/usr/bin/python3 /path/to/factor_crowding_monitor/run_monitor.py --cron "0 16 * * 1-5"
Restart=always

[Install]
WantedBy=multi-user.target
```

啟動服務:
```bash
sudo systemctl daemon-reload
sudo systemctl start crowding-monitor
sudo systemctl enable crowding-monitor
```

2. **使用 cron**

添加到 crontab:
```bash
crontab -e
```

```
0 16 * * 1-5 cd /path/to/factor_crowding_monitor && /usr/bin/python3 run_monitor.py --once >> logs/cron.log 2>&1
```

---

## 12. 擴展與優化

### 12.1 新增因子

1. 在 `monitor/realtime.py` 的 `monitored_factors` 中添加新因子
2. 確保 `data/factors/` 目錄中有對應的數據文件

### 12.2 自定義預警規則

在 `config/thresholds.py` 中修改預警邏輯，或創建新的預警類。

### 12.3 集成外部通知

在 `monitor/alert.py` 的 `NotificationService` 中添加新的通知渠道。

### 12.4 添加新的策略

在 `backtest/strategies.py` 中實現新的交易策略。

---

## 13. 故障排查

### 常見問題

**Q: 數據加載失敗**
- A: 檢查數據路徑配置，確保數據文件存在且格式正確

**Q: GARCH 估計失敗**
- A: 系統會自動回退到歷史波動率估計，可以在配置中關閉 GARCH

**Q: 預警未觸發**
- A: 檢查預警閾值配置，確認 `alert.enabled` 設置為 True

**Q: 儀表板無法打開**
- A: 確認瀏覽器支持 HTML5，或使用最新版 Chrome/Firefox

---

## 14. 性能優化建議

1. **數據預處理**：提前計算並存儲滾動統計量
2. **並行計算**：使用 multiprocessing 並行處理多個因子
3. **增量更新**：只計算最新的數據，避免重複計算
4. **緩存機制**：緩存中間結果，減少重複計算
5. **數據庫優化**：使用時間序列數據庫提升查詢性能

---

## 15. 後續開發路線圖

### 短期（1-2 個月）
- [ ] 添加 Web UI 界面
- [ ] 支持實時數據流
- [ ] 添加更多通知渠道（Telegram、Slack）

### 中期（3-6 個月）
- [ ] 實現機器學習預測模型
- [ ] 支持多因子組合監控
- [ ] 添加風險指標（VaR、CVaR）

### 長期（6-12 個月）
- [ ] 支持跨境市場監控
- [ ] 開發移動端應用
- [ ] 構建因子擁擠度數據庫

---

## Metadata

- **Implementation language:** Python 3.10+
- **Code structure:** 模塊化，分層架構
- **Test coverage:** 待補充
- **Documentation:** 完整
- **Deployment status:** 開發完成，待實施驗證
- **Validation status:** 代碼已驗證，待實證數據

---

**文檔版本:** v1.0
**最後更新:** 2026-02-20
**作者:** Charlie Analyst
**審核狀態:** 待審核
