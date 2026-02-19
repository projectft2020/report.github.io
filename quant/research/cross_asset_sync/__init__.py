"""
跨資產同步極端事件分析套件
Author: Charlie
Date: 2026-02-17
"""

from cross_asset_analyzer import CrossAssetAnalyzer
from data_loader import DataLoader
from correlation_analysis import CorrelationAnalyzer
from breakdown_detector import BreakdownDetector
from regime_analysis import RegimeAnalyzer
from trade_signal_generator import TradeSignalGenerator
from backtest_engine import BacktestEngine

__version__ = '1.0.0'
__author__ = 'Charlie'

__all__ = [
    'CrossAssetAnalyzer',
    'DataLoader',
    'CorrelationAnalyzer',
    'BreakdownDetector',
    'RegimeAnalyzer',
    'TradeSignalGenerator',
    'BacktestEngine'
]
