#!/usr/bin/env python3
"""
KPI Calculator für Financial Data Analysis.
Berechnet wichtige Finanzkennzahlen aus den extrahierten Financial Statements.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import logging
from dataclasses import dataclass

# Import the logger
from scrape_quarterlies import logger

@dataclass
class KPIResult:
    """Data class für KPI-Berechnungen."""
    ticker: str
    quarter: str
    year: int
    quarter_num: int
    kpi_name: str
    value: float
    unit: str
    category: str  # 'profitability', 'liquidity', 'leverage', 'efficiency'

class KPICalculator:
    """
    Calculator für wichtige Finanzkennzahlen (KPIs).
    """
    
    def __init__(self):
        """Initialize KPI Calculator."""
        logger.info("🧮 Initializing KPI Calculator")
    
    def calculate_kpis(self, financial_data: Dict[str, Any], ticker: str, 
                      year: int, quarter: int) -> List[KPIResult]:
        """
        Berechnet alle wichtigen KPIs aus Financial Data.
        
        Args:
            financial_data (Dict[str, Any]): Extrahierte Financial Data
            ticker (str): Stock ticker symbol
            year (int): Year
            quarter (int): Quarter
            
        Returns:
            List[KPIResult]: Liste der berechneten KPIs
        """
        kpis = []
        
        try:
            # Extrahiere die wichtigsten Accounts
            income_data = financial_data.get('income_statement', {})
            balance_data = financial_data.get('balance_sheet', {})
            cashflow_data = financial_data.get('cash_flow', {})
            
            # Revenue (bereits verfügbar)
            revenue = self._get_account_value(income_data, ['Revenue', 'Total Revenue', 'Net Sales'])
            if revenue:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Revenue",
                    value=revenue,
                    unit="USD",
                    category="profitability"
                ))
            
            # Gross Profit
            gross_profit = self._get_account_value(income_data, ['Gross Profit', 'Gross Income'])
            if gross_profit:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Gross Profit",
                    value=gross_profit,
                    unit="USD",
                    category="profitability"
                ))
            
            # Gross Margin (berechnet)
            if revenue and gross_profit and revenue > 0:
                gross_margin = (gross_profit / revenue) * 100
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Gross Margin",
                    value=gross_margin,
                    unit="%",
                    category="profitability"
                ))
            
            # Operating Income
            operating_income = self._get_account_value(income_data, 
                ['Operating Income', 'Operating Profit', 'Income from Operations'])
            if operating_income:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Operating Income",
                    value=operating_income,
                    unit="USD",
                    category="profitability"
                ))
            
            # Operating Margin (berechnet)
            if revenue and operating_income and revenue > 0:
                operating_margin = (operating_income / revenue) * 100
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Operating Margin",
                    value=operating_margin,
                    unit="%",
                    category="profitability"
                ))
            
            # Net Income
            net_income = self._get_account_value(income_data, 
                ['Net Income', 'Net Earnings', 'Net Profit'])
            if net_income:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Net Income",
                    value=net_income,
                    unit="USD",
                    category="profitability"
                ))
            
            # Net Margin (berechnet)
            if revenue and net_income and revenue > 0:
                net_margin = (net_income / revenue) * 100
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Net Margin",
                    value=net_margin,
                    unit="%",
                    category="profitability"
                ))
            
            # Total Assets
            total_assets = self._get_account_value(balance_data, 
                ['Total Assets', 'Assets'])
            if total_assets:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Total Assets",
                    value=total_assets,
                    unit="USD",
                    category="balance_sheet"
                ))
            
            # Total Liabilities
            total_liabilities = self._get_account_value(balance_data, 
                ['Total Liabilities', 'Liabilities'])
            if total_liabilities:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Total Liabilities",
                    value=total_liabilities,
                    unit="USD",
                    category="balance_sheet"
                ))
            
            # Shareholders Equity
            shareholders_equity = self._get_account_value(balance_data, 
                ['Shareholders Equity', 'Stockholders Equity', 'Total Equity'])
            if shareholders_equity:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Shareholders Equity",
                    value=shareholders_equity,
                    unit="USD",
                    category="balance_sheet"
                ))
            
            # Debt-to-Equity Ratio (berechnet)
            if total_liabilities and shareholders_equity and shareholders_equity > 0:
                debt_to_equity = total_liabilities / shareholders_equity
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Debt-to-Equity Ratio",
                    value=debt_to_equity,
                    unit="ratio",
                    category="leverage"
                ))
            
            # Current Assets
            current_assets = self._get_account_value(balance_data, 
                ['Current Assets', 'Total Current Assets'])
            if current_assets:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Current Assets",
                    value=current_assets,
                    unit="USD",
                    category="liquidity"
                ))
            
            # Current Liabilities
            current_liabilities = self._get_account_value(balance_data, 
                ['Current Liabilities', 'Total Current Liabilities'])
            if current_liabilities:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Current Liabilities",
                    value=current_liabilities,
                    unit="USD",
                    category="liquidity"
                ))
            
            # Current Ratio (berechnet)
            if current_assets and current_liabilities and current_liabilities > 0:
                current_ratio = current_assets / current_liabilities
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Current Ratio",
                    value=current_ratio,
                    unit="ratio",
                    category="liquidity"
                ))
            
            # Operating Cash Flow
            operating_cash_flow = self._get_account_value(cashflow_data, 
                ['Operating Cash Flow', 'Cash from Operations', 'Net Cash from Operating Activities'])
            if operating_cash_flow:
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Operating Cash Flow",
                    value=operating_cash_flow,
                    unit="USD",
                    category="cash_flow"
                ))
            
            # Free Cash Flow (berechnet: Operating Cash Flow - CapEx)
            capex = self._get_account_value(cashflow_data, 
                ['Capital Expenditures', 'CapEx', 'Purchases of Property and Equipment'])
            if operating_cash_flow and capex:
                free_cash_flow = operating_cash_flow - abs(capex)  # CapEx is usually negative
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Free Cash Flow",
                    value=free_cash_flow,
                    unit="USD",
                    category="cash_flow"
                ))
            
            # Return on Assets (ROA) - berechnet
            if net_income and total_assets and total_assets > 0:
                roa = (net_income / total_assets) * 100
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Return on Assets (ROA)",
                    value=roa,
                    unit="%",
                    category="efficiency"
                ))
            
            # Return on Equity (ROE) - berechnet
            if net_income and shareholders_equity and shareholders_equity > 0:
                roe = (net_income / shareholders_equity) * 100
                kpis.append(KPIResult(
                    ticker=ticker,
                    quarter=f"{year}Q{quarter}",
                    year=year,
                    quarter_num=quarter,
                    kpi_name="Return on Equity (ROE)",
                    value=roe,
                    unit="%",
                    category="efficiency"
                ))
            
            logger.info(f"🧮 Calculated {len(kpis)} KPIs for {ticker} {year}Q{quarter}")
            return kpis
            
        except Exception as e:
            logger.error(f"❌ Error calculating KPIs for {ticker} {year}Q{quarter}: {e}")
            return []
    
    def _get_account_value(self, data: Dict[str, Any], possible_names: List[str]) -> Optional[float]:
        """
        Sucht nach einem Account-Wert basierend auf verschiedenen möglichen Namen.
        
        Args:
            data (Dict[str, Any]): Account-Daten
            possible_names (List[str]): Mögliche Account-Namen
            
        Returns:
            Optional[float]: Account-Wert oder None
        """
        for name in possible_names:
            for account_name, values in data.items():
                if name.lower() in account_name.lower():
                    if values and len(values) > 0:
                        # Nimm den ersten Wert (meist der aktuellste)
                        value = values[0]
                        if isinstance(value, (int, float)):
                            return float(value)
        return None
    
    def calculate_quarterly_growth(self, kpis: List[KPIResult], kpi_name: str) -> List[Dict[str, Any]]:
        """
        Berechnet das Quartalswachstum für einen spezifischen KPI.
        
        Args:
            kpis (List[KPIResult]): Liste der KPIs
            kpi_name (str): Name des KPIs
            
        Returns:
            List[Dict[str, Any]]: Wachstumsdaten
        """
        # Filtere KPIs nach Name
        filtered_kpis = [kpi for kpi in kpis if kpi.kpi_name == kpi_name]
        
        # Sortiere nach Jahr und Quartal
        filtered_kpis.sort(key=lambda x: (x.year, x.quarter_num))
        
        growth_data = []
        for i in range(1, len(filtered_kpis)):
            current = filtered_kpis[i]
            previous = filtered_kpis[i-1]
            
            if previous.value != 0:
                growth_rate = ((current.value - previous.value) / abs(previous.value)) * 100
                growth_data.append({
                    'quarter': current.quarter,
                    'current_value': current.value,
                    'previous_value': previous.value,
                    'growth_rate': growth_rate,
                    'unit': current.unit
                })
        
        return growth_data
    
    def export_kpis_to_dataframe(self, kpis: List[KPIResult]) -> pd.DataFrame:
        """
        Exportiert KPIs zu einem Pandas DataFrame.
        
        Args:
            kpis (List[KPIResult]): Liste der KPIs
            
        Returns:
            pd.DataFrame: DataFrame mit KPI-Daten
        """
        data = []
        for kpi in kpis:
            data.append({
                'ticker': kpi.ticker,
                'quarter': kpi.quarter,
                'year': kpi.year,
                'quarter_num': kpi.quarter_num,
                'kpi_name': kpi.kpi_name,
                'value': kpi.value,
                'unit': kpi.unit,
                'category': kpi.category
            })
        
        return pd.DataFrame(data)


# Example usage
if __name__ == "__main__":
    # Beispiel Financial Data
    sample_financial_data = {
        'income_statement': {
            'Revenue': [123456000, 98765000],
            'Gross Profit': [45678000, 34567000],
            'Operating Income': [23456000, 18765000],
            'Net Income': [15678000, 12345000]
        },
        'balance_sheet': {
            'Total Assets': [500000000, 450000000],
            'Total Liabilities': [200000000, 180000000],
            'Shareholders Equity': [300000000, 270000000],
            'Current Assets': [150000000, 135000000],
            'Current Liabilities': [80000000, 72000000]
        },
        'cash_flow': {
            'Operating Cash Flow': [25000000, 23000000],
            'Capital Expenditures': [-5000000, -4000000]
        }
    }
    
    # KPI Calculator initialisieren
    calculator = KPICalculator()
    
    # KPIs berechnen
    kpis = calculator.calculate_kpis(sample_financial_data, "AAPL", 2024, 2)
    
    # Ergebnisse anzeigen
    print(f"📊 Calculated {len(kpis)} KPIs:")
    for kpi in kpis:
        print(f"   {kpi.kpi_name}: {kpi.value:,.2f} {kpi.unit} ({kpi.category})")
    
    # Zu DataFrame exportieren
    df = calculator.export_kpis_to_dataframe(kpis)
    print(f"\n📋 DataFrame shape: {df.shape}")
    print(df.head())
