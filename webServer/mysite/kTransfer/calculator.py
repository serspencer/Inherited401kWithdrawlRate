"""
Core calculation logic for the inherited 401(k) withdrawal rate tool.

All rates are expressed as decimals (e.g. 0.07 for 7%).
Tax figures are for the 2024 tax year.
"""

# 2024 standard deductions
STANDARD_DEDUCTION = {
    "single": 14600,
    "married_jointly": 29200,
    "married_separately": 14600,
    "head_of_household": 21900,
}

# 2024 federal income tax brackets (upper limit, marginal rate)
TAX_BRACKETS = {
    "single": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
    "married_jointly": [
        (23200, 0.10),
        (94300, 0.12),
        (201050, 0.22),
        (383900, 0.24),
        (487450, 0.32),
        (731200, 0.35),
        (float("inf"), 0.37),
    ],
    "married_separately": [
        (11600, 0.10),
        (47150, 0.12),
        (100525, 0.22),
        (191950, 0.24),
        (243725, 0.32),
        (365600, 0.35),
        (float("inf"), 0.37),
    ],
    "head_of_household": [
        (16550, 0.10),
        (63100, 0.12),
        (100500, 0.22),
        (191950, 0.24),
        (243700, 0.32),
        (609350, 0.35),
        (float("inf"), 0.37),
    ],
}

FILING_STATUS_CHOICES = [
    ("single", "Single"),
    ("married_jointly", "Married Filing Jointly"),
    ("married_separately", "Married Filing Separately"),
    ("head_of_household", "Head of Household"),
]


def calculate_federal_tax(gross_income, filing_status):
    """Return estimated federal income tax for the given gross income and filing status."""
    deduction = STANDARD_DEDUCTION[filing_status]
    brackets = TAX_BRACKETS[filing_status]
    taxable_income = max(gross_income - deduction, 0)
    tax = 0.0
    prev_limit = 0
    for limit, rate in brackets:
        if taxable_income <= prev_limit:
            break
        taxed_amount = min(taxable_income, limit) - prev_limit
        tax += taxed_amount * rate
        prev_limit = limit
    return tax


def calculate_scenarios(
    total_years,
    k_initial_balance,
    k_growth_rate,
    secondary_init_balance,
    secondary_growth_rate,
    annual_income,
    filing_status,
):
    """
    Simulate withdrawing the inherited 401(k) over 1 through total_years years and
    calculate tax and savings outcomes for each scenario.

    Returns a dict with:
        scenarios           - list of per-scenario result dicts
        min_tax_year        - withdrawal period (int) that minimises total tax paid
        max_secondary_year  - withdrawal period (int) that maximises final savings balance
        min_tax_paid        - lowest total tax value across all scenarios
        max_secondary_value - highest final savings balance across all scenarios
    """
    scenarios = []
    min_tax_paid = float("inf")
    min_tax_year = 1
    max_secondary_value = float("-inf")
    max_secondary_year = 1

    for n in range(1, total_years + 1):
        balance_401k = k_initial_balance
        total_tax_paid = 0.0
        non_withdrawal_tax_accum = 0.0
        secondary_balance = secondary_init_balance
        withdrawals_left = n
        yearly_details = []

        for year in range(total_years):
            # Apply compound growth to both accounts
            balance_401k *= 1 + k_growth_rate
            secondary_after_growth = secondary_balance * (
                (1 + secondary_growth_rate / 365) ** 365
            )
            secondary_income = secondary_after_growth - secondary_balance
            secondary_balance = secondary_after_growth

            if withdrawals_left > 0:
                # Withdraw an equal share of the remaining 401(k) balance
                annual_withdrawal = balance_401k / withdrawals_left
                balance_401k -= annual_withdrawal
                withdrawals_left -= 1

                taxable_income = annual_income + secondary_income + annual_withdrawal
                tax_owed = calculate_federal_tax(taxable_income, filing_status)
                total_tax_paid += tax_owed

                # Deposit post-tax withdrawal into the secondary account
                post_tax_withdrawal = annual_withdrawal - tax_owed
                secondary_balance += post_tax_withdrawal
            else:
                # No 401(k) withdrawal — still owe tax on regular income + interest
                taxable_income = annual_income + secondary_income
                tax_owed = calculate_federal_tax(taxable_income, filing_status)
                non_withdrawal_tax_accum += tax_owed
                total_tax_paid += tax_owed
                secondary_balance -= non_withdrawal_tax_accum

            yearly_details.append(
                {
                    "year": year + 1,
                    "balance_401k": balance_401k,
                    "tax_this_year": tax_owed,
                    "total_tax_paid": total_tax_paid,
                    "secondary_balance": secondary_balance - non_withdrawal_tax_accum,
                }
            )

        final_secondary = secondary_balance - non_withdrawal_tax_accum

        if total_tax_paid < min_tax_paid:
            min_tax_paid = total_tax_paid
            min_tax_year = n

        if final_secondary > max_secondary_value:
            max_secondary_value = final_secondary
            max_secondary_year = n

        scenarios.append(
            {
                "withdrawal_years": n,
                "final_secondary_balance": final_secondary,
                "total_tax_paid": total_tax_paid,
                "net_gain": final_secondary - k_initial_balance - secondary_init_balance,
                "yearly_details": yearly_details,
            }
        )

    return {
        "scenarios": scenarios,
        "min_tax_year": min_tax_year,
        "max_secondary_year": max_secondary_year,
        "min_tax_paid": min_tax_paid,
        "max_secondary_value": max_secondary_value,
    }
