from borrowers.models import CompanySettings

def company_details(request):
    company = CompanySettings.objects.first()

    return {
        "company": company,
        "currency": company.currency_symbol if company else "₦",
        "company_footer": company.report_footer if company else "",
    }