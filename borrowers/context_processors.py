from .models import CompanySettings


def company_settings(request):

    company = CompanySettings.objects.first()

    return {
        "company": company,
    }