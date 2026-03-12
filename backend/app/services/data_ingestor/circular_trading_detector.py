"""Circular trading detection for Intelli-Credit system."""

from typing import List, Dict
from app.models.financial import GSTData, Transaction
from app.models.alerts import CircularTradingAlert


class Discrepancy:
    """Represents a discrepancy between GSTR versions."""
    
    def __init__(self, field: str, gstr_2a_value: float, gstr_3b_value: float, difference: float):
        self.field = field
        self.gstr_2a_value = gstr_2a_value
        self.gstr_3b_value = gstr_3b_value
        self.difference = difference
        self.percentage_diff = abs(difference / gstr_2a_value * 100) if gstr_2a_value != 0 else 0.0


class CircularTradingDetector:
    """Detects circular trading patterns by cross-checking GST and bank data."""
    
    # Threshold for high-risk deposit ratio (70% as per requirement 3.4)
    HIGH_RISK_DEPOSIT_THRESHOLD = 0.70
    
    # Threshold for significant mismatch between GSTR versions (10%)
    GSTR_MISMATCH_THRESHOLD = 0.10
    
    def detect_circular_trading(
        self, 
        gst_data: GSTData, 
        bank_transactions: List[Transaction]
    ) -> CircularTradingAlert:
        """
        Cross-check GST sales vs bank deposits to detect circular trading.
        
        Validates Requirements 3.1, 3.3, 3.4:
        - 3.1: Cross-check sales amounts against actual deposits
        - 3.3: Generate alert with specific discrepancies and amounts
        - 3.4: Mark as high-risk when deposits < 70% of GST sales
        
        Args:
            gst_data: GST return data containing sales information
            bank_transactions: List of bank transactions
            
        Returns:
            CircularTradingAlert with detection results
        """
        # Calculate total bank deposits (credits)
        bank_deposits = sum(txn.credit for txn in bank_transactions)
        gst_sales = gst_data.sales
        
        # Calculate mismatch percentage
        if gst_sales > 0:
            deposit_ratio = bank_deposits / gst_sales
            mismatch_percentage = abs(1.0 - deposit_ratio) * 100
        else:
            deposit_ratio = 0.0
            mismatch_percentage = 0.0
        
        # Determine if circular trading is detected
        detected = deposit_ratio < self.HIGH_RISK_DEPOSIT_THRESHOLD
        
        # Determine severity
        if deposit_ratio < 0.50:
            severity = "high"
        elif deposit_ratio < self.HIGH_RISK_DEPOSIT_THRESHOLD:
            severity = "medium"
        else:
            severity = "low"
        
        # Build discrepancy list
        discrepancies = []
        if detected:
            discrepancies.append(
                f"Bank deposits (₹{bank_deposits:,.2f}) are {deposit_ratio*100:.1f}% "
                f"of reported GST sales (₹{gst_sales:,.2f})"
            )
            discrepancies.append(
                f"Deposit shortfall: ₹{gst_sales - bank_deposits:,.2f}"
            )
            if deposit_ratio < 0.50:
                discrepancies.append(
                    "CRITICAL: Less than 50% of sales reflected in bank deposits"
                )
        
        return CircularTradingAlert(
            detected=detected,
            severity=severity,
            discrepancies=discrepancies,
            gst_sales=gst_sales,
            bank_deposits=bank_deposits,
            mismatch_percentage=mismatch_percentage
        )
    
    def compare_gstr_versions(
        self, 
        gstr_2a: GSTData, 
        gstr_3b: GSTData
    ) -> List[Discrepancy]:
        """
        Compare GSTR-2A and GSTR-3B for mismatches.
        
        Validates Requirement 3.2:
        - Flag application when significant mismatch exists between GSTR-2A and GSTR-3B
        
        Args:
            gstr_2a: GSTR-2A data (purchases from supplier perspective)
            gstr_3b: GSTR-3B data (summary return)
            
        Returns:
            List of Discrepancy objects for significant mismatches
        """
        discrepancies = []
        
        # Compare purchases
        purchase_diff = abs(gstr_2a.purchases - gstr_3b.purchases)
        if gstr_2a.purchases > 0:
            purchase_diff_pct = purchase_diff / gstr_2a.purchases
            if purchase_diff_pct > self.GSTR_MISMATCH_THRESHOLD:
                discrepancies.append(
                    Discrepancy(
                        field="purchases",
                        gstr_2a_value=gstr_2a.purchases,
                        gstr_3b_value=gstr_3b.purchases,
                        difference=gstr_3b.purchases - gstr_2a.purchases
                    )
                )
        
        # Compare sales
        sales_diff = abs(gstr_2a.sales - gstr_3b.sales)
        if gstr_2a.sales > 0:
            sales_diff_pct = sales_diff / gstr_2a.sales
            if sales_diff_pct > self.GSTR_MISMATCH_THRESHOLD:
                discrepancies.append(
                    Discrepancy(
                        field="sales",
                        gstr_2a_value=gstr_2a.sales,
                        gstr_3b_value=gstr_3b.sales,
                        difference=gstr_3b.sales - gstr_2a.sales
                    )
                )
        
        # Compare tax paid
        tax_diff = abs(gstr_2a.tax_paid - gstr_3b.tax_paid)
        if gstr_2a.tax_paid > 0:
            tax_diff_pct = tax_diff / gstr_2a.tax_paid
            if tax_diff_pct > self.GSTR_MISMATCH_THRESHOLD:
                discrepancies.append(
                    Discrepancy(
                        field="tax_paid",
                        gstr_2a_value=gstr_2a.tax_paid,
                        gstr_3b_value=gstr_3b.tax_paid,
                        difference=gstr_3b.tax_paid - gstr_2a.tax_paid
                    )
                )
        
        return discrepancies
