from django import forms
from .calculator import FILING_STATUS_CHOICES


class WithdrawalCalculatorForm(forms.Form):
    k_initial_balance = forms.FloatField(
        label="401(k) Current Balance ($)",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 250000"}),
    )
    k_growth_rate = forms.FloatField(
        label="401(k) Annual Growth Rate (%)",
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "e.g. 7", "step": "0.1"}
        ),
    )
    secondary_init_balance = forms.FloatField(
        label="Secondary Account Starting Balance ($)",
        min_value=0,
        required=False,
        initial=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 10000"}),
        help_text="Withdrawn funds will be deposited here after taxes. Leave blank if starting from zero.",
    )
    secondary_growth_rate = forms.FloatField(
        label="Secondary Account Annual Rate (%)",
        min_value=0,
        max_value=100,
        required=False,
        initial=0,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "placeholder": "e.g. 4.5", "step": "0.1"}
        ),
        help_text="Interest/growth rate for the account the withdrawals go into (e.g. HYSA, brokerage).",
    )
    annual_income = forms.FloatField(
        label="Other Annual Income ($)",
        min_value=0,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 75000"}),
        help_text="Your income excluding 401(k) withdrawals (salary, Social Security, etc.).",
    )
    total_years = forms.IntegerField(
        label="Analysis Period (years)",
        min_value=1,
        max_value=30,
        widget=forms.NumberInput(attrs={"class": "form-control", "placeholder": "e.g. 10"}),
        help_text="The calculator will compare all withdrawal timelines from 1 year up to this number.",
    )
    filing_status = forms.ChoiceField(
        label="Filing Status",
        choices=FILING_STATUS_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
