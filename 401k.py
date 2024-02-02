import argparse

def calculate_federal_tax(income, brackets):
    
    standardDeduction = 13850
    tax = 0
    taxableIncome = max(income - standardDeduction, 0)
    print(f'Taxable Income after Deduction {taxableIncome}')
    for bracket in brackets:
        if taxableIncome > bracket[0]:
            tax += (bracket[0] - (0 if brackets.index(bracket) == 0 else brackets[brackets.index(bracket) - 1][0])) * bracket[1]
        else:
            tax += (taxableIncome - (0 if brackets.index(bracket) == 0 else brackets[brackets.index(bracket) - 1][0])) * bracket[1]
            break
    return tax

def format_currency(amount):
    return f"${amount:,.2f}"

# Function to calculate the scenario for different withdrawal periods n (1-7)
def calculate_varied_withdrawal_scenario(total_years, initial_balance, growthRateK, growthRateSecondaryAccount, annualIncome, tax_brackets):
    year_scenarios = []
    min_tax_paid = float('inf')
    min_tax_year = 0
    
    
    for n in range(1, total_years + 1):
        kBalance = initial_balance
        totalTaxPaid = 0
        hysaBalance = 0
        intermediate_calculations = []
        withdrawlsLeft = n

        # Loop through Differnt Withdrawl Rates
        for year in range(total_years):

            # Compound Interest for Both Accounts
            kBalance *= (1 + growthRateK)
            hysaIncome = (hysaBalance * ((1 + growthRateSecondaryAccount / 365) ** (1 * 365)) - hysaBalance)
            # print(f'\tHYSA Income: {format_currency(hysaIncome)}')
            hysaBalance += hysaIncome

            # Withdrawl from 401k Based on n
            if(withdrawlsLeft != 0) :
                annualWithdrawlK = kBalance / withdrawlsLeft
                kBalance -= annualWithdrawlK
                withdrawlsLeft -= 1
                # Calculate Estimated Tax from Withdrawn 401k Balance and Secondary Account Interest as income plus standard income
                taxedIncome = annualIncome + hysaIncome + annualWithdrawlK
                estimatedTaxOnIncome = calculate_federal_tax(taxedIncome, tax_brackets)
                totalTaxPaid += estimatedTaxOnIncome
                # Deduct the amount paid in taxes from the withdrawn amount
                postTaxWithdrawl = annualWithdrawlK - estimatedTaxOnIncome
                # Add that difference to the HYSA or Secondary Account
                hysaBalance += postTaxWithdrawl
            else :
                taxedIncome = annualIncome + hysaIncome
                estimatedTaxOnIncome = calculate_federal_tax(taxedIncome, tax_brackets)
                totalTaxPaid += estimatedTaxOnIncome
            



            intermediate_calculations.append({
                'Year': year + 1,
                '401k Balance': kBalance,
                'Estimated Tax': estimatedTaxOnIncome,
                'Total Tax Paid': totalTaxPaid,
                'HYSA Balance': hysaBalance
            })

        year_scenarios.append({
            'Year': n,
            'Final HYSA Balance': format_currency(hysaBalance),
            'Total Tax Paid': format_currency(totalTaxPaid),
            'Intermediate Calculations': intermediate_calculations
        })

        # Check and update the year with the lowest tax paid
        if totalTaxPaid < min_tax_paid:
            min_tax_paid = totalTaxPaid
            min_tax_year = n
    
    return year_scenarios, min_tax_year

def main():
    parser = argparse.ArgumentParser(description='Calculate 401k withdrawal and HYSA reinvestment.')
    parser.add_argument('--initial_balance', type=float, required=True, help='Initial balance of the 401k.')
    parser.add_argument('--growth_rate_401k', type=float, required=True, help='Annual growth rate of the 401k.')
    parser.add_argument('--hysa_rate', type=float, required=True, help='Annual interest rate of the HYSA.')
    parser.add_argument('--annual_income', type=float, required=True, help='Annual income of the individual.')
    parser.add_argument('--total_years', type=int, required=True, help='Total length of time in years for the whole process.')
    args = parser.parse_args()

    initial_401k_balance = args.initial_balance
    annual_growth_rate = args.growth_rate_401k
    hysa_interest_rate = args.hysa_rate
    annual_income = args.annual_income
    totalYears = args.total_years

    tax_brackets = [
    (11000, 0.10),  # Up to $11,000 taxed at 10%
    (44725, 0.12),  # $11,000 to $44,725 taxed at 12%
    (89150, 0.22),  # $44,725 to $89,150 taxed at 22%
    (170050, 0.24), # $89,150 to $170,050 taxed at 24%
    (215950, 0.32), # $170,050 to $215,950 taxed at 32%
    (539900, 0.35), # $215,950 to $539,900 taxed at 35%
    (float('inf'), 0.37)  # Over $539,900 taxed at 37%
    ]

    scenarios, minTaxYear = calculate_varied_withdrawal_scenario(totalYears, initial_401k_balance, annual_growth_rate, hysa_interest_rate, annual_income, tax_brackets)
    
    # Regular Output
    min_tax_scenario = scenarios[minTaxYear - 1]
    print(f"Year with the lowest tax paid: {min_tax_scenario['Year']}")
    print(f"  Final HYSA Balance = {min_tax_scenario['Final HYSA Balance']}\n  Total Tax Paid in {totalYears} year span = {min_tax_scenario['Total Tax Paid']}\n\n")

    if minTaxYear - 1 < len(scenarios):
        for scenario in scenarios:
            print(f"\nIntermediate Calculations for {scenario['Year']}-Year Scenario:")
            for intermediate in scenario['Intermediate Calculations']:
                print(f"Year {intermediate['Year']}:\
                      \n\t401k Ending Balance = {format_currency(intermediate['401k Balance'])}\
                      \n\tTax Paid That Year  = {format_currency(intermediate['Estimated Tax'])}\
                      \n\tTotal Tax Paid YTD  = {format_currency(intermediate['Total Tax Paid'])}\
                      \n\tHYSA Ending Balance = {format_currency(intermediate['HYSA Balance'])}")
    else:
        print(f"Data for the {minTaxYear}-year scenario is not available.")
    
    print(f"\n")

    # for scenario in scenarios:
    #     print(f"Year {scenario['Year']}: Final HYSA Balance = {scenario['Final HYSA Balance']}, Total Tax Paid Over {totalYears} years = {scenario['Total Tax Paid']}")

if __name__ == '__main__':
    main()


#  The program should calculate the amount of taxes paid over a given span say t for time in years
#  You will have a 401k balance called k that will be reduced by tested time frame call it time_frame
#  The 401k will be deduced k / 
#
#
#
#
#
#
#
#