import uuid

from borrowers.models import CompanySettings


class CompanyService:

    @staticmethod
    def get():
        return CompanySettings.objects.first()

    @staticmethod
    def currency():
        company = CompanySettings.objects.first()
        return company.currency_symbol if company else "₦"

    @staticmethod
    def prefix():
        company = CompanySettings.objects.first()
        return company.receipt_prefix if company else "CWLS"

    @staticmethod
    def footer():
        company = CompanySettings.objects.first()
        return company.report_footer if company else ""


def generate_receipt_number():
    prefix = CompanyService.prefix()
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"