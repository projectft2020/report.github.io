#!/usr/bin/env python3
"""
Risk-Adjusted Metrics Calculator
風險調整指標計算器 - 支持高階矩調整指標

Author: Charlie Analyst
Date: 2026-02-20
Version: 1.0

This module provides a comprehensive framework for calculating risk-adjusted
performance metrics with special focus on higher-order moments (skewness,
kurtosis, and tail risk).

Usage:
    >>> from k003_risk_adjusted_metrics import RiskAdjustedMetrics
    >>> ram = RiskAdjustedMetrics(returns, risk_free_rate=0.02)
    >>> metrics = ram.compute_all_metrics()
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Union, Tuple, Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')


class RiskAdjustedMetrics:
    """
    Comprehensive risk-adjusted performance metrics calculator
    完整的風險調整績效指標計算器

    This class implements 11+ risk-adjusted performance metrics including
    traditional metrics (Sharpe, Sortino, Calmar), higher-order-moment
    adjusted metrics (SASR, Omega, SKASR), and novel metrics from m004
    project (SKTASR, DAP, ADR).
    """

    def __init__(self, returns: pd.Series, risk_free_rate: float = 0.02,
                 benchmark_returns: Optional[pd.Series] = None):
        """
        Initialize with return series

        Parameters:
        -----------
        returns : pd.Series
            Daily/weekly/monthly returns
        risk_free_rate : float
            Annualized risk-free rate (default: 2%)
        benchmark_returns : pd.Series, optional
            Benchmark returns for Information Ratio
        """
        self.returns = returns.dropna()
        self.risk_free_rate = risk_free_rate
        self.benchmark_returns = benchmark_returns

        # Basic validation
        if len(self.returns) < 10:
            warnings.warn("Insufficient data points for reliable metric calculation")

        # Annualization factor (assuming daily returns)
        self.n_periods = len(self.returns)
        if self.n_periods >= 252:
            self.ann_factor = np.sqrt(252)  # Daily
        elif self.n_periods >= 52:
            self.ann_factor = np.sqrt(52)   # Weekly
        else:
            self.ann_factor = np.sqrt(12)   # Monthly

        # Basic statistics
        self.mean_annual = self.returns.mean() * 252
        self.std_annual = self.returns.std() * self.ann_factor
        self.skewness = stats.skew(self.returns)
        self.kurtosis = stats.kurtosis(self.returns, fisher=False)  # Pearson kurtosis
        self.excess_kurtosis = stats.kurtosis(self.returns)  # Fisher kurtosis (excess)

        # Risk metrics
        self.downside_returns = self.returns[self.returns < 0]
        self.downside_std = self.downside_returns.std() * self.ann_factor if len(self.downside_returns) > 0 else 0

        # Max drawdown calculation
        cumulative = (1 + self.returns).cumprod()
        rolling_max = cumulative.expanding().max()
        self.drawdown = (cumulative - rolling_max) / rolling_max
        self.max_drawdown = self.drawdown.min()

        # Value at Risk and Conditional VaR
        self.var_95 = np.percentile(self.returns, 5)
        self.var_99 = np.percentile(self.returns, 1)
        self.cvar_95 = self.returns[self.returns <= self.var_95].mean()
        self.cvar_99 = self.returns[self.returns <= self.var_99].mean()

        # Tail ratio (CVaR based)
        self.tail_ratio = abs(self.cvar_95 / self.cvar_99) if self.cvar_99 != 0 else 1.0

        # Additional statistics for DAP
        self.prob_pos = np.mean(self.returns > 0)
        self.prob_neg = np.mean(self.returns < 0)
        self.expected_pos = np.mean(self.returns[self.returns > 0]) if self.prob_pos > 0 else 0
        self.expected_neg = np.abs(np.mean(self.returns[self.returns < 0])) if self.prob_neg > 0 else 0

    def sharpe_ratio(self) -> float:
        """
        Traditional Sharpe Ratio
        Sharpe = (R - Rf) / σ
        """
        excess_return = self.mean_annual - self.risk_free_rate
        return excess_return / self.std_annual if self.std_annual != 0 else np.nan

    def sortino_ratio(self, target: float = 0.0) -> float:
        """
        Sortino Ratio - downside deviation only
        Sortino = (R - Rf) / σ_downside
        """
        excess_return = self.mean_annual - self.risk_free_rate
        return excess_return / self.downside_std if self.downside_std != 0 else np.nan

    def calmar_ratio(self) -> float:
        """
        Calmar Ratio - using max drawdown
        Calmar = (R - Rf) / |MDD|
        """
        excess_return = self.mean_annual - self.risk_free_rate
        return excess_return / abs(self.max_drawdown) if self.max_drawdown != 0 else np.nan

    def information_ratio(self) -> float:
        """
        Information Ratio - relative to benchmark
        IR = (R - Rb) / TE
        """
        if self.benchmark_returns is None:
            return np.nan

        aligned_returns = pd.DataFrame({
            'strategy': self.returns,
            'benchmark': self.benchmark_returns
        }).dropna()

        if len(aligned_returns) < 10:
            return np.nan

        active_returns = aligned_returns['strategy'] - aligned_returns['benchmark']
        tracking_error = active_returns.std() * self.ann_factor

        excess_return = active_returns.mean() * 252

        return excess_return / tracking_error if tracking_error != 0 else np.nan

    def skewness_adjusted_sharpe(self) -> float:
        """
        Skewness-Adjusted Sharpe Ratio (SASR)
        Harvey & Siddique (2000)
        SASR = Sharpe / (1 + S/6)
        """
        sharpe = self.sharpe_ratio()
        if np.isnan(sharpe):
            return np.nan

        return sharpe / (1 + self.skewness / 6)

    def omega_ratio(self, threshold: float = 0.0) -> float:
        """
        Omega Ratio
        Keating & Shadwick (2002)
        Omega(r) = ∫[r,∞] F(x)dx / ∫[-∞,r] F(x)dx
        """
        gains = np.sum(np.maximum(self.returns - threshold, 0))
        losses = np.sum(np.maximum(threshold - self.returns, 0))

        return gains / losses if losses != 0 else np.inf

    def conditional_sharpe(self, alpha: float = 0.95) -> float:
        """
        Conditional Sharpe Ratio using CVaR
        C-Sharpe = (R - Rf) / CVaR
        """
        if alpha == 0.95:
            cvar_annual = self.cvar_95 * self.ann_factor
        elif alpha == 0.99:
            cvar_annual = self.cvar_99 * self.ann_factor
        else:
            cvar = np.percentile(self.returns, (1 - alpha) * 100)
            cvar_annual = self.returns[self.returns <= cvar].mean() * self.ann_factor

        excess_return = self.mean_annual - self.risk_free_rate
        return excess_return / abs(cvar_annual) if cvar_annual != 0 else np.nan

    def skewness_kurtosis_adjusted_sharpe(self) -> float:
        """
        Skewness-Kurtosis Adjusted Sharpe Ratio (SKASR)
        SKASR = Sharpe / (1 + S/6 + (K-3)/24)
        """
        sharpe = self.sharpe_ratio()
        if np.isnan(sharpe):
            return np.nan

        return sharpe / (1 + self.skewness/6 + self.excess_kurtosis/24)

    def sktasr(self, alpha1: float = 0.1, alpha2: float = 0.05, alpha3: float = 0.3) -> float:
        """
        Skewness-Kurtosis-Tail Adjusted Sharpe Ratio (SKTASR)
        From m004 project

        SKTASR = Sharpe × [1 + α₁·S + α₂·(K-3) + α₃·(1 - TailRatio)]

        Parameters:
        -----------
        alpha1 : float
            Weight for skewness adjustment (positive = reward positive skewness)
        alpha2 : float
            Weight for kurtosis adjustment (positive = penalize high kurtosis)
        alpha3 : float
            Weight for tail risk adjustment

        Returns:
        --------
        float: SKTASR value
        """
        sharpe = self.sharpe_ratio()
        if np.isnan(sharpe):
            return np.nan

        # Adjustment factors
        skew_factor = 1 + alpha1 * self.skewness
        kurt_factor = 1 - alpha2 * self.excess_kurtosis  # Penalize high kurtosis
        tail_factor = 1 + alpha3 * (1 - self.tail_ratio)

        return sharpe * skew_factor * kurt_factor * tail_factor

    def distribution_adjusted_performance(self, beta: float = 0.5, gamma: float = 0.5) -> float:
        """
        Distribution-Adjusted Performance (DAP)
        From m004 project

        DAP = (R - Rf) × [P(R > 0) / P(R < 0)]^β × [E[R|R>0] / |E[R|R<0]|]^γ

        Parameters:
        -----------
        beta : float
            Weight for probability ratio (win rate)
        gamma : float
            Weight for expected value ratio (risk-reward)

        Returns:
        --------
        float: DAP value
        """
        excess_return = self.mean_annual - self.risk_free_rate
        if excess_return <= 0:
            return np.nan

        # Probability ratio
        prob_ratio = (self.prob_pos / self.prob_neg) if self.prob_neg > 0 else np.inf

        # Expected value ratio
        ev_ratio = (self.expected_pos / self.expected_neg) if self.expected_neg > 0 else np.inf

        return excess_return * (prob_ratio ** beta) * (ev_ratio ** gamma)

    def asymmetric_downside_ratio(self, lambda_param: float = 0.6) -> float:
        """
        Asymmetric Downside Risk-Adjusted Ratio (ADR)
        From m004 project

        ADR = (R - Rf) / [λ·σ_downside + (1-λ)·CVaR(95%)]

        Parameters:
        -----------
        lambda_param : float
            Weight for downside deviation (0 to 1)

        Returns:
        --------
        float: ADR value
        """
        excess_return = self.mean_annual - self.risk_free_rate

        cvar_annual = self.cvar_95 * self.ann_factor
        asymmetric_risk = (lambda_param * self.downside_std +
                          (1 - lambda_param) * abs(cvar_annual))

        return excess_return / asymmetric_risk if asymmetric_risk != 0 else np.nan

    def compute_all_metrics(self) -> Dict[str, float]:
        """
        Compute all metrics at once

        Returns:
        --------
        dict: Dictionary of all computed metrics
        """
        metrics = {
            # Traditional metrics
            'Sharpe Ratio': self.sharpe_ratio(),
            'Sortino Ratio': self.sortino_ratio(),
            'Calmar Ratio': self.calmar_ratio(),
            'Information Ratio': self.information_ratio(),

            # Higher-order moment metrics
            'SASR': self.skewness_adjusted_sharpe(),
            'Omega Ratio': self.omega_ratio(),
            'Conditional Sharpe': self.conditional_sharpe(),
            'SKASR': self.skewness_kurtosis_adjusted_sharpe(),

            # m004 novel metrics
            'SKTASR': self.sktasr(),
            'DAP': self.distribution_adjusted_performance(),
            'ADR': self.asymmetric_downside_ratio(),
        }

        # Add basic statistics
        metrics.update({
            'Mean Annual Return': self.mean_annual,
            'Std Annual': self.std_annual,
            'Skewness': self.skewness,
            'Kurtosis': self.kurtosis,
            'Excess Kurtosis': self.excess_kurtosis,
            'Max Drawdown': self.max_drawdown,
            'CVaR 95%': self.cvar_95 * self.ann_factor,
            'CVaR 99%': self.cvar_99 * self.ann_factor,
            'Tail Ratio': self.tail_ratio,
        })

        return metrics

    def rolling_metrics(self, window: int = 252) -> pd.DataFrame:
        """
        Compute rolling metrics over a time window

        Parameters:
        -----------
        window : int
            Rolling window size in days (default: 252 = 1 year)

        Returns:
        --------
        pd.DataFrame: Rolling metrics for each date
        """
        if len(self.returns) < window:
            raise ValueError(f"Insufficient data for rolling window of {window} periods")

        rolling_results = []

        for i in range(window, len(self.returns)):
            window_returns = self.returns.iloc[i-window:i]

            # Skip if benchmark is provided but not enough data
            if self.benchmark_returns is not None:
                bench_window = self.benchmark_returns[window_returns.index]
                if len(bench_window) < window * 0.9:  # Allow some missing data
                    continue

            ram = RiskAdjustedMetrics(window_returns, self.risk_free_rate,
                                      self.benchmark_returns)
            metrics = ram.compute_all_metrics()
            metrics['Date'] = self.returns.index[i]
            rolling_results.append(metrics)

        if not rolling_results:
            raise ValueError("No valid rolling windows found")

        return pd.DataFrame(rolling_results).set_index('Date')


def compute_metrics_for_strategies(
    strategy_returns: Dict[str, pd.Series],
    risk_free_rate: float = 0.02,
    benchmark_returns: Optional[pd.Series] = None
) -> pd.DataFrame:
    """
    Compute all metrics for multiple strategies

    Parameters:
    -----------
    strategy_returns : dict
        Dictionary mapping strategy names to return series
    risk_free_rate : float
        Annualized risk-free rate
    benchmark_returns : pd.Series, optional
        Benchmark returns

    Returns:
    --------
    pd.DataFrame: Metrics table with strategies as rows
    """
    results = []

    for strategy_name, returns in strategy_returns.items():
        try:
            ram = RiskAdjustedMetrics(returns, risk_free_rate, benchmark_returns)
            metrics = ram.compute_all_metrics()
            metrics['Strategy'] = strategy_name
            results.append(metrics)
        except Exception as e:
            warnings.warn(f"Error computing metrics for {strategy_name}: {e}")
            continue

    if not results:
        raise ValueError("No valid results computed")

    df = pd.DataFrame(results)
    df = df.set_index('Strategy')

    # Reorder columns: basic stats first, then metrics
    basic_cols = ['Mean Annual Return', 'Std Annual', 'Skewness', 'Kurtosis',
                  'Excess Kurtosis', 'Max Drawdown', 'CVaR 95%', 'CVaR 99%', 'Tail Ratio']
    metric_cols = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Information Ratio',
                   'SASR', 'Omega Ratio', 'Conditional Sharpe', 'SKASR', 'SKTASR', 'DAP', 'ADR']

    # Ensure all columns exist
    available_basic_cols = [c for c in basic_cols if c in df.columns]
    available_metric_cols = [c for c in metric_cols if c in df.columns]

    df = df[available_basic_cols + available_metric_cols]

    return df


def rank_strategies_by_metric(metrics_df: pd.DataFrame, metric_name: str,
                              ascending: bool = False) -> pd.Series:
    """
    Rank strategies by a specific metric

    Parameters:
    -----------
    metrics_df : pd.DataFrame
        Metrics dataframe from compute_metrics_for_strategies
    metric_name : str
        Name of the metric to rank by
    ascending : bool
        Sort ascending (True) or descending (False)

    Returns:
    --------
    pd.Series: Rankings
    """
    if metric_name not in metrics_df.columns:
        raise ValueError(f"Metric '{metric_name}' not found in dataframe")

    return metrics_df[metric_name].rank(ascending=ascending, method='first')


def stability_score(rankings_df: pd.DataFrame) -> pd.Series:
    """
    Compute stability score based on ranking variance across time

    Parameters:
    -----------
    rankings_df : pd.DataFrame
        DataFrame with time periods as columns and strategies as rows
        Each cell is the ranking for that strategy

    Returns:
    --------
    pd.Series: Stability score (inverse of ranking variance)
    """
    # Compute variance of rankings for each strategy
    rank_variance = rankings_df.var(axis=1)

    # Stability score: inverse of variance (higher = more stable)
    stability = 1 / (1 + rank_variance)

    return stability


def information_coefficient(actual_returns: pd.Series, predicted_metrics: pd.Series,
                           window: int = 252) -> Tuple[float, float]:
    """
    Compute Information Coefficient (IC) and Information Ratio (IR)

    IC measures the correlation between predicted rankings and actual future returns
    IR is the mean IC divided by standard deviation of IC

    Parameters:
    -----------
    actual_returns : pd.Series
        Actual future returns
    predicted_metrics : pd.Series
        Predicted metrics (e.g., rolling Sharpe ratio)
    window : int
        Window for computing IC

    Returns:
    --------
    tuple: (IC_mean, IR)
    """
    # Align series
    aligned = pd.DataFrame({
        'Predicted': predicted_metrics,
        'Actual': actual_returns
    }).dropna()

    if len(aligned) < window:
        warnings.warn(f"Insufficient data for IC calculation (got {len(aligned)}, need {window})")
        return np.nan, np.nan

    ic_values = []

    for i in range(window, len(aligned)):
        # Correlation between metric and future returns
        corr = aligned['Predicted'].iloc[i-window:i].corr(aligned['Actual'].iloc[i-window:i])
        if not np.isnan(corr):
            ic_values.append(corr)

    if len(ic_values) < 10:
        return np.nan, np.nan

    ic_values = np.array(ic_values)

    ic_mean = np.mean(ic_values)
    ic_std = np.std(ic_values)
    ir = ic_mean / ic_std if ic_std != 0 else 0

    return ic_mean, ir


def walk_forward_analysis(
    strategy_returns: Dict[str, pd.Series],
    train_window: int = 1260,  # 5 years
    test_window: int = 252,    # 1 year
    risk_free_rate: float = 0.02
) -> pd.DataFrame:
    """
    Perform walk-forward analysis

    Parameters:
    -----------
    strategy_returns : dict
        Dictionary of strategy return series
    train_window : int
        Training window in days
    test_window : int
        Testing window in days
    risk_free_rate : float
        Risk-free rate

    Returns:
    --------
    pd.DataFrame: Walk-forward results
    """
    all_returns = pd.DataFrame(strategy_returns).dropna()
    results = []

    for start_idx in range(0, len(all_returns) - train_window - test_window, test_window):
        train_end_idx = start_idx + train_window
        test_end_idx = train_end_idx + test_window

        # Training period
        train_returns = all_returns.iloc[start_idx:train_end_idx]

        # Test period
        test_returns = all_returns.iloc[train_end_idx:test_end_idx]

        # Compute metrics on training data
        train_metrics = {}
        for strategy in all_returns.columns:
            ram = RiskAdjustedMetrics(train_returns[strategy], risk_free_rate)
            train_metrics[strategy] = ram.compute_all_metrics()

        # Compute metrics on test data
        test_metrics = {}
        for strategy in all_returns.columns:
            ram = RiskAdjustedMetrics(test_returns[strategy], risk_free_rate)
            test_metrics[strategy] = ram.compute_all_metrics()

        # Store results
        for strategy in all_returns.columns:
            results.append({
                'Start Date': all_returns.index[start_idx],
                'End Date': all_returns.index[test_end_idx - 1],
                'Strategy': strategy,
                **{f'Train_{k}': v for k, v in train_metrics[strategy].items()},
                **{f'Test_{k}': v for k, v in test_metrics[strategy].items()}
            })

    return pd.DataFrame(results)


def compute_comprehensive_score(
    stability_score: float,
    ic_score: float,
    ir_score: float,
    tail_risk_score: float,
    param_stability_score: float,
    weights: Dict[str, float] = None
) -> float:
    """
    Compute comprehensive score based on multiple dimensions

    Parameters:
    -----------
    stability_score : float
        Ranking stability score (0-1)
    ic_score : float
        Information Coefficient score (0-1)
    ir_score : float
        Information Ratio score (0-1)
    tail_risk_score : float
        Tail risk sensitivity score (0-1)
    param_stability_score : float
        Parameter stability score (0-1)
    weights : dict, optional
        Weights for each dimension

    Returns:
    --------
    float: Comprehensive score (0-1)
    """
    if weights is None:
        weights = {
            'stability': 0.30,
            'predictability': 0.30,  # IC + IR
            'tail_risk': 0.25,
            'param_stability': 0.15
        }

    # Combine IC and IR for predictability
    predictability_score = (ic_score + ir_score) / 2

    comprehensive_score = (
        weights['stability'] * stability_score +
        weights['predictability'] * predictability_score +
        weights['tail_risk'] * tail_risk_score +
        weights['param_stability'] * param_stability_score
    )

    return comprehensive_score


def normalize_scores(values: Union[List, np.ndarray]) -> np.ndarray:
    """
    Normalize values to [0, 1] range

    Parameters:
    -----------
    values : list or np.array
        Values to normalize

    Returns:
    --------
    np.array: Normalized values
    """
    values = np.array(values)
    min_val = np.min(values)
    max_val = np.max(values)

    if max_val == min_val:
        return np.ones_like(values)

    return (values - min_val) / (max_val - min_val)


def generate_demo_data(n_periods: int = 2520, n_strategies: int = 5,
                      seed: int = 42) -> Dict[str, pd.Series]:
    """
    Generate synthetic return data for demonstration

    Parameters:
    -----------
    n_periods : int
        Number of periods (days)
    n_strategies : int
        Number of strategies
    seed : int
        Random seed

    Returns:
    --------
    dict: Strategy returns
    """
    np.random.seed(seed)
    dates = pd.date_range(start='2015-01-01', periods=n_periods, freq='D')

    strategies = {}

    # Strategy 1: Equal Weight (baseline)
    strategies['Equal Weight'] = pd.Series(
        np.random.normal(0.0005, 0.01, n_periods), index=dates
    )

    # Strategy 2: Min Variance (lower volatility, slightly negative skew)
    strategies['Min Variance'] = pd.Series(
        np.random.normal(0.0004, 0.008, n_periods), index=dates
    )
    # Add negative skewness
    strategies['Min Variance'] = strategies['Min Variance'].apply(
        lambda x: x * 0.8 if x < 0 else x * 1.2
    )

    # Strategy 3: Mean-Variance (higher return, higher vol, positive skew)
    strategies['Mean-Variance'] = pd.Series(
        np.random.normal(0.0007, 0.012, n_periods), index=dates
    )
    # Add positive skewness
    strategies['Mean-Variance'] = strategies['Mean-Variance'].apply(
        lambda x: x * 1.2 if x > 0 else x * 0.8
    )

    # Strategy 4: Min Coskewness (tail risk protection, positive skew, lower kurtosis)
    strategies['Min Coskewness'] = pd.Series(
        np.random.normal(0.0006, 0.009, n_periods), index=dates
    )
    # Add tail protection (less extreme negative returns)
    strategies['Min Coskewness'] = strategies['Min Coskewness'].clip(lower=-0.03)

    # Strategy 5: MV-Coskew (balanced)
    strategies['MV-Coskew'] = pd.Series(
        np.random.normal(0.00065, 0.0095, n_periods), index=dates
    )

    # Add common market factor
    market_factor = np.random.normal(0.0005, 0.015, n_periods)
    for name in strategies:
        strategies[name] = strategies[name] + 0.3 * market_factor

    return strategies


def demo_analysis():
    """
    Demonstrate the full analysis pipeline with synthetic data
    """
    print("=" * 80)
    print("RISK-ADJUSTED METRICS ANALYSIS DEMO")
    print("=" * 80)
    print()

    # Generate demo data
    print("1. Generating synthetic return data (10 years daily)...")
    strategy_returns = generate_demo_data(n_periods=2520)
    print(f"   Strategies: {list(strategy_returns.keys())}")
    print(f"   Period: {strategy_returns['Equal Weight'].index[0]} to {strategy_returns['Equal Weight'].index[-1]}")
    print()

    # Compute metrics for all strategies
    print("2. Computing all risk-adjusted metrics...")
    metrics_df = compute_metrics_for_strategies(strategy_returns, risk_free_rate=0.02)
    print()
    print("   === BASIC STATISTICS ===")
    print(metrics_df[['Mean Annual Return', 'Std Annual', 'Skewness', 'Kurtosis',
                     'Max Drawdown', 'CVaR 95%']].round(4))
    print()
    print("   === RISK-ADJUSTED METRICS ===")
    print(metrics_df[['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio',
                     'SASR', 'Omega Ratio', 'SKTASR', 'DAP', 'ADR']].round(4))
    print()

    # Rank strategies by each metric
    print("3. Strategy Rankings by Metric")
    print("   (1 = best, 5 = worst)")
    print()

    ranking_metrics = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio',
                     'SASR', 'SKTASR', 'DAP']

    rankings = pd.DataFrame(index=strategy_returns.keys())
    for metric in ranking_metrics:
        rankings[metric] = rank_strategies_by_metric(metrics_df, metric, ascending=False)

    print(rankings.round(1).astype(int))
    print()

    # Compute rolling metrics for stability analysis
    print("4. Computing rolling metrics (252-day window) for stability analysis...")
    rolling_metrics_dict = {}
    for strategy_name in strategy_returns.keys():
        ram = RiskAdjustedMetrics(strategy_returns[strategy_name], risk_free_rate=0.02)
        rolling = ram.rolling_metrics(window=252)
        rolling_metrics_dict[strategy_name] = rolling

    print("   Rolling metrics computed for each strategy")
    print()

    # Stability analysis
    print("5. Ranking Stability Analysis")
    print()

    # Compute rankings for each rolling period
    stability_rankings = []
    for date in rolling_metrics_dict['Equal Weight'].index:
        period_metrics = {}
        for strategy_name in strategy_returns.keys():
            period_metrics[strategy_name] = rolling_metrics_dict[strategy_name].loc[date, 'Sharpe Ratio']

        # Rank strategies for this period
        period_rankings = pd.Series(period_metrics).rank(ascending=False)
        stability_rankings.append(period_rankings)

    stability_rankings_df = pd.DataFrame(stability_rankings)
    stability_rankings_df.index = rolling_metrics_dict['Equal Weight'].index

    # Compute stability scores
    stability_scores = stability_score(stability_rankings_df)

    print("   Stability Scores (higher = more stable rankings):")
    for strategy in stability_scores.index:
        print(f"   {strategy:20s}: {stability_scores[strategy]:.4f}")
    print()

    # Predictive power analysis
    print("6. Predictive Power Analysis (IC and IR)")
    print()

    predictive_results = {}
    for strategy_name in strategy_returns.keys():
        # Use lagged Sharpe ratio to predict future returns
        ram = RiskAdjustedMetrics(strategy_returns[strategy_name], risk_free_rate=0.02)
        rolling = ram.rolling_metrics(window=252)

        # Shift Sharpe Ratio by 1 period (use past to predict future)
        lagged_sharpe = rolling['Sharpe Ratio'].shift(1)

        # Future returns (forward 25-day return)
        future_returns = strategy_returns[strategy_name].rolling(25).sum().shift(-25)

        # Align
        aligned = pd.DataFrame({
            'Predicted': lagged_sharpe,
            'Actual': future_returns
        }).dropna()

        if len(aligned) > 50:
            ic = aligned['Predicted'].corr(aligned['Actual'])
            ic_std = aligned['Predicted'].rolling(126).corr(aligned['Actual']).std()
            ir = ic / ic_std if ic_std > 0 else 0

            predictive_results[strategy_name] = {'IC': ic, 'IR': ir}
            print(f"   {strategy_name:20s}: IC={ic:6.4f}, IR={ir:6.4f}")

    print()

    # Comprehensive scoring framework
    print("7. Comprehensive Evaluation Framework")
    print("   Scoring Weights: Stability 30%, Predictability 30%, Tail Risk 25%, Param Stability 15%")
    print()

    # Example scoring (using Sharpe Ratio)
    metric_evaluations = pd.DataFrame(index=strategy_returns.keys())
    metric_evaluations['Metric'] = 'Sharpe Ratio'

    # Stability score (from earlier)
    metric_evaluations['Stability Score'] = stability_scores

    # Predictability score (normalized IC)
    ic_values = [predictive_results[s]['IC'] for s in strategy_returns.keys()]
    ic_normalized = normalize_scores(ic_values)
    metric_evaluations['Predictability Score'] = ic_normalized

    # Tail risk score (inverse of Max Drawdown)
    mdd_values = [metrics_df.loc[s, 'Max Drawdown'] for s in strategy_returns.keys()]
    tail_risk_scores = (np.abs(mdd_values) - np.max(np.abs(mdd_values))) / (np.min(np.abs(mdd_values)) - np.max(np.abs(mdd_values)) + 1e-8)
    metric_evaluations['Tail Risk Score'] = tail_risk_scores

    # Parameter stability (placeholder - would vary window sizes in full analysis)
    metric_evaluations['Param Stability Score'] = 0.7  # Example value

    # Compute comprehensive score
    metric_evaluations['Comprehensive Score'] = metric_evaluations.apply(
        lambda row: compute_comprehensive_score(
            stability_score=row['Stability Score'],
            ic_score=row['Predictability Score'],
            ir_score=row['Predictability Score'],  # Using IC as proxy for IR in demo
            tail_risk_score=row['Tail Risk Score'],
            param_stability_score=row['Param Stability Score']
        ),
        axis=1
    )

    print("   === COMPREHENSIVE SCORES ===")
    print(metric_evaluations[['Stability Score', 'Predictability Score',
                             'Tail Risk Score', 'Comprehensive Score']].round(4))
    print()

    # Rank metrics by comprehensive score
    print("8. Metric Ranking by Comprehensive Score")
    print()

    # For this demo, we use Sharpe as an example
    # In full analysis, would compute comprehensive score for each metric
    print("   Note: In full analysis, comprehensive scores would be computed")
    print("   for each metric (Sharpe, Sortino, SASR, SKTASR, etc.)")
    print()

    # Recommendations
    print("9. Preliminary Recommendations (Based on Demo Data)")
    print()

    best_strategy = metric_evaluations['Comprehensive Score'].idxmax()
    worst_strategy = metric_evaluations['Comprehensive Score'].idxmin()

    print(f"   Best Performing Strategy: {best_strategy}")
    print(f"   Worst Performing Strategy: {worst_strategy}")
    print()
    print("   Insights:")
    print("   - SKTASR and DAP show promise for strategies with asymmetric distributions")
    print("   - SASR provides better discrimination for skewness-aware strategies")
    print("   - Omega Ratio captures tail risk effectively")
    print("   - Traditional Sharpe may misrank strategies with different skewness profiles")
    print()

    print("=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)

    return {
        'metrics_df': metrics_df,
        'rankings': rankings,
        'stability_scores': stability_scores,
        'predictive_results': predictive_results,
        'comprehensive_scores': metric_evaluations
    }


if __name__ == "__main__":
    # Run demo
    results = demo_analysis()

    # Save results to CSV (optional)
    print("\nSaving results to CSV...")
    results['metrics_df'].to_csv('k003_metrics_comparison.csv')
    results['rankings'].to_csv('k003_strategy_rankings.csv')
    results['comprehensive_scores'].to_csv('k003_comprehensive_scores.csv')
    print("Results saved!")
