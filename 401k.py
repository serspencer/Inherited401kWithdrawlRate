import argparse

def calculate_federal_tax(income, brackets):
    
    standardDeduction = 13850
    tax = 0
    taxableIncome = max(income - standardDeduction, 0)
    # print(f'Taxable Income after Deduction {taxableIncome}')
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
def calculate_varied_withdrawal_scenario(total_years, initial_balance, growthRateK, secondaryAcctInitBalance, growthRateSecondaryAccount, annualIncome, taxBracket):
    year_scenarios = []
    min_tax_paid = float('inf')
    min_tax_year = 0
    maxSecondaryAcctValue = 0
    maxSecondaryAcctYear = 0
    
    
    for n in range(1, total_years + 1):
        kBalance = initial_balance                  # kBalance is 401k Balance
        totalTaxPaid = 0
        notWithdrawnTax = 0
        hysaBalance = secondaryAcctInitBalance      # hysaBalance needs to be renamed to secondary account balance
        intermediate_calculations = []
        withdrawlsLeft = n

        # print(f'Year {n} scenario')
        # print(f'\tHYSA Starting Balance {hysaBalance}')
        # Loop through Differnt Withdrawl Rates
        for year in range(total_years):

            # print(f'\tYear {year} of {n}')
            # Compound Interest for Both Accounts
            kBalance *= (1 + growthRateK)
            balanceAfterOneYear = (hysaBalance * ((1 + (growthRateSecondaryAccount / 365)) ** 365))
            # print(f'\t\tBalance After Compounding: {balanceAfterOneYear}')
            hysaIncome = balanceAfterOneYear - hysaBalance
            # print(f'\t\tHYSA Income: {format_currency(hysaIncome)}')
            hysaBalance = balanceAfterOneYear

            # Withdrawl from 401k Based on n
            if(withdrawlsLeft != 0) :
                annualWithdrawlK = kBalance / withdrawlsLeft
                kBalance -= annualWithdrawlK
                withdrawlsLeft -= 1

                # Calculate Estimated Tax from Withdrawn 401k Balance and Secondary Account Interest as income plus standard income
                taxedIncome = annualIncome + hysaIncome + annualWithdrawlK
                estimatedTaxOnIncome = calculate_federal_tax(taxedIncome, taxBracket)
                totalTaxPaid += estimatedTaxOnIncome

                # Deduct the amount paid in taxes for overall income from the withdrawn amount
                postTaxWithdrawl = annualWithdrawlK - estimatedTaxOnIncome

                # Add that difference to the HYSA or Secondary Account
                hysaBalance += postTaxWithdrawl
            else :
                # No Taxes being deducted
                taxedIncome = annualIncome + hysaIncome
                estimatedTaxOnIncome = calculate_federal_tax(taxedIncome, taxBracket)
                notWithdrawnTax += estimatedTaxOnIncome
                totalTaxPaid += estimatedTaxOnIncome
                hysaBalance -= notWithdrawnTax

            
            intermediate_calculations.append({
                'Year': year + 1,
                '401k Balance': kBalance,
                'Estimated Tax': estimatedTaxOnIncome,
                'Total Tax Paid': totalTaxPaid,
                'HYSA Balance': hysaBalance - notWithdrawnTax
            })

        # print(f'\tNot paid tax total: {format_currency(notWithdrawnTax)}')
        # Check and update the year with the lowest tax paid
        if totalTaxPaid < min_tax_paid:
            min_tax_paid = totalTaxPaid
            min_tax_year = n

        # Check and update the year with the lowest tax paid
        if hysaBalance > maxSecondaryAcctValue:
            maxSecondaryAcctValue = hysaBalance
            maxSecondaryAcctYear = n
        
        year_scenarios.append({
            'Year': n,
            'Final HYSA Balance': format_currency(hysaBalance),
            'Total Tax Paid': format_currency(totalTaxPaid),
            'Net Gain': format_currency(hysaBalance - initial_balance - secondaryAcctInitBalance),
            'Intermediate Calculations': intermediate_calculations
        })
    
    return year_scenarios, min_tax_year, maxSecondaryAcctYear

def determinTaxBracket(taxStatus) :

    taxBrackets = [None, None, None, None]

    # Single Filer
    taxBrackets[0] = [
    (11000, 0.10),  # Up to $11,000 taxed at 10%
    (44725, 0.12),  # $11,001 to $44,725 taxed at 12%
    (95375, 0.22),  # $44,726 to $95,375 taxed at 22%
    (182100, 0.24), # $95,376 to $182,100 taxed at 24%
    (231250, 0.32), # $182,101 to $231,250 taxed at 32%
    (578125, 0.35), # $231,251 to $578,125 taxed at 35%
    (float('inf'), 0.37)  # Over $578,126 taxed at 37%
    ]

    # Married Jointly
    taxBrackets[1] = [
    (22000, 0.10),  # Up to $11,000 taxed at 10%
    (89450, 0.12),  # $11,000 to $44,725 taxed at 12%
    (190750, 0.22),  # $44,725 to $89,150 taxed at 22%
    (364200, 0.24), # $89,150 to $170,050 taxed at 24%
    (462500, 0.32), # $170,050 to $215,950 taxed at 32%
    (693750, 0.35), # $215,950 to $539,900 taxed at 35%
    (float('inf'), 0.37)  # Over $539,900 taxed at 37%
    ]

    # Married Separate
    taxBrackets[2] = [
    (11000, 0.10),  # Up to $11,000 taxed at 10%
    (44725, 0.12),  # $11,001 to $44,725 taxed at 12%
    (95375, 0.22),  # $44,726 to $95,375 taxed at 22%
    (182100, 0.24), # $95,376 to $182,100 taxed at 24%
    (231250, 0.32), # $182,101 to $231,250 taxed at 32%
    (578125, 0.35), # $231,251 to $578,125 taxed at 35%
    (float('inf'), 0.37)  # Over $578,126 taxed at 37%
    ]

    # Head of Household
    taxBrackets[3] = [
    (11000, 0.10),  # Up to $11,000 taxed at 10%
    (44725, 0.12),  # $11,001 to $44,725 taxed at 12%
    (95375, 0.22),  # $44,726 to $95,375 taxed at 22%
    (182100, 0.24), # $95,376 to $182,100 taxed at 24%
    (231250, 0.32), # $182,101 to $231,250 taxed at 32%
    (578125, 0.35), # $231,251 to $578,125 taxed at 35%
    (float('inf'), 0.37)  # Over $578,126 taxed at 37%
    ]

    # print(f'Tax Bracket Info {taxBrackets[taxStatus-1]}')
    return taxBrackets[taxStatus-1]

def main():
    parser = argparse.ArgumentParser(description='Calculate 401k withdrawal and HYSA reinvestment.')
    parser.add_argument('-ib', '--kInitialBalance', type=float, required=True, help='Initial balance of the 401k.')
    parser.add_argument('-kr', '--kGrowthRate', type=float, required=True, help='Annual growth rate of the 401k.')
    parser.add_argument('-sb', '--sInitialBalance', type=float, required=False, default=0, help='Initial balance of the Secondary Account.')
    parser.add_argument('-sr', '--sGrowthRate', type=float, required=False, default=0, help='Annual interest rate of the Secondary Account.')
    parser.add_argument('-ai', '--annualIncome', type=float, required=True, help='Annual income of the individual.')
    parser.add_argument('-t', '--totalYears',  type=int, required=True, help='Total length of time in years for the whole process.')
    parser.add_argument('-fs', '--filing_status', type=int, required=False, default=1, help='\
                        1 --> Single\
                        2 --> Married Jointly\
                        3 --> Married Separately\
                        4 --> Head of Household\
                        ')
    
    args = parser.parse_args()

    initial_401k_balance = args.kInitialBalance
    secondaryAcctInitBalance = args.sInitialBalance
    annual_growth_rate = args.kGrowthRate
    hysa_interest_rate = args.sGrowthRate
    annual_income = args.annualIncome
    totalYears = args.totalYears 
    taxBracket = determinTaxBracket(args.filing_status)
    

    scenarios, minTaxYear, maxSecondaryYear = calculate_varied_withdrawal_scenario(totalYears, initial_401k_balance, annual_growth_rate, secondaryAcctInitBalance, hysa_interest_rate, annual_income, taxBracket)
    
    # Less Taxes Piad
    min_tax_scenario = scenarios[minTaxYear - 1]
    print(f"\nYear with the lowest tax paid: {min_tax_scenario['Year']}")
    print(f"  Final HYSA Balance = {min_tax_scenario['Final HYSA Balance']}\
          \n  Total Tax Paid in {totalYears} year span = {min_tax_scenario['Total Tax Paid']}")
        #   \n  Net Gain {min_tax_scenario['Net Gain']}")

    # More money in your pocket
    maxSecondaryAcctScenario = scenarios[maxSecondaryYear - 1]
    print(f"\nYear with highest Secondary Account Value: {maxSecondaryAcctScenario['Year']}")
    print(f"  Final HYSA Balance = {maxSecondaryAcctScenario['Final HYSA Balance']}\
          \n  Total Tax Paid in {totalYears} year span = {maxSecondaryAcctScenario['Total Tax Paid']}")
        #   \n  Net Gain {maxSecondaryAcctScenario['Net Gain']}")

    # # Print out Intermediate Calculations for Each Yar.  Useful for Troubleshooting
    # if minTaxYear - 1 < len(scenarios):
    #     for scenario in scenarios:
    #         print(f"\nIntermediate Calculations for {scenario['Year']}-Year Scenario:")
    #         for intermediate in scenario['Intermediate Calculations']:
    #             print(f"Year {intermediate['Year']}:\
    #                   \n\t401k Ending Balance = {format_currency(intermediate['401k Balance'])}\
    #                   \n\tTax Paid That Year  = {format_currency(intermediate['Estimated Tax'])}\
    #                   \n\tTotal Tax Paid YTD  = {format_currency(intermediate['Total Tax Paid'])}\
    #                   \n\tHYSA Ending Balance = {format_currency(intermediate['HYSA Balance'])}")
    # else:
    #     print(f"Data for the {minTaxYear}-year scenario is not available.")
    
    # print(f"\n")

    # for scenario in scenarios:
    #     print(f"Year {scenario['Year']}: Final HYSA Balance = {scenario['Final HYSA Balance']}, Total Tax Paid Over {totalYears} years = {scenario['Total Tax Paid']}")

if __name__ == '__main__':
    main()