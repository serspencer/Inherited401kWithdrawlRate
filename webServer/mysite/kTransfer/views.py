from django.shortcuts import render
from .forms import WithdrawalCalculatorForm
from .calculator import calculate_scenarios, FILING_STATUS_CHOICES


def index(request):
    if request.method == "POST":
        form = WithdrawalCalculatorForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            results = calculate_scenarios(
                total_years=data["total_years"],
                k_initial_balance=data["k_initial_balance"],
                k_growth_rate=data["k_growth_rate"] / 100,
                secondary_init_balance=data["secondary_init_balance"] or 0,
                secondary_growth_rate=(data["secondary_growth_rate"] or 0) / 100,
                annual_income=data["annual_income"],
                filing_status=data["filing_status"],
            )
            filing_label = dict(FILING_STATUS_CHOICES)[data["filing_status"]]
            return render(
                request,
                "kTransfer/output.html",
                {
                    "results": results,
                    "form_data": data,
                    "filing_label": filing_label,
                },
            )
    else:
        form = WithdrawalCalculatorForm()

    return render(request, "kTransfer/input_form.html", {"form": form})
