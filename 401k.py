import argparse
from webServer.mysite.kTransfer.calculator import (
    calculate_scenarios,
    FILING_STATUS_CHOICES,
    TAX_BRACKETS,
    STANDARD_DEDUCTION,
)


def format_currency(amount):
    return f"${amount:,.2f}"


def main():
    parser = argparse.ArgumentParser(
        description="Calculate optimal withdrawal strategy for an inherited 401(k)."
    )
    parser.add_argument("-ib", "--kInitialBalance", type=float, required=True,
                        help="Initial balance of the 401(k).")
    parser.add_argument("-kr", "--kGrowthRate", type=float, required=True,
                        help="Annual growth rate of the 401(k) as a percentage (e.g. 7 for 7%%).")
    parser.add_argument("-sb", "--sInitialBalance", type=float, required=False, default=0,
                        help="Starting balance of the secondary savings account.")
    parser.add_argument("-sr", "--sGrowthRate", type=float, required=False, default=0,
                        help="Annual interest rate of the secondary account as a percentage.")
    parser.add_argument("-ai", "--annualIncome", type=float, required=True,
                        help="Annual income excluding 401(k) withdrawals.")
    parser.add_argument("-t", "--totalYears", type=int, required=True,
                        help="Number of years to analyze.")
    parser.add_argument("-fs", "--filing_status", type=str, required=False, default="single",
                        choices=[k for k, _ in FILING_STATUS_CHOICES],
                        help="Filing status: single, married_jointly, married_separately, head_of_household")

    args = parser.parse_args()

    results = calculate_scenarios(
        total_years=args.totalYears,
        k_initial_balance=args.kInitialBalance,
        k_growth_rate=args.kGrowthRate / 100,
        secondary_init_balance=args.sInitialBalance,
        secondary_growth_rate=args.sGrowthRate / 100,
        annual_income=args.annualIncome,
        filing_status=args.filing_status,
    )

    scenarios = results["scenarios"]
    min_tax_year = results["min_tax_year"]
    max_secondary_year = results["max_secondary_year"]

    min_tax_scenario = scenarios[min_tax_year - 1]
    print(f"\nYear with the lowest total tax paid: {min_tax_scenario['withdrawal_years']}")
    print(f"  Final savings balance : {format_currency(min_tax_scenario['final_secondary_balance'])}")
    print(f"  Total tax paid        : {format_currency(min_tax_scenario['total_tax_paid'])}")
    print(f"  Net gain              : {format_currency(min_tax_scenario['net_gain'])}")

    max_secondary_scenario = scenarios[max_secondary_year - 1]
    print(f"\nYear with the highest savings balance: {max_secondary_scenario['withdrawal_years']}")
    print(f"  Final savings balance : {format_currency(max_secondary_scenario['final_secondary_balance'])}")
    print(f"  Total tax paid        : {format_currency(max_secondary_scenario['total_tax_paid'])}")
    print(f"  Net gain              : {format_currency(max_secondary_scenario['net_gain'])}")


if __name__ == "__main__":
    main()
