"""Route handlers for the UI."""

import csv

from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse

from util import common_fns
from .portfolio_generator import PortfolioGenerator
from .report_generator import ReportGenerator

def output_reports(req: HttpRequest) -> HttpResponse:
    """Generate reports for all users."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            ReportGenerator().output_reports(int(target_id))
            return HttpResponse(
                f'Reports for event {target_id} are being generated to output folder.',
                content_type='text/plain',
            )

def get_dummy_report(req: HttpRequest) -> HttpResponse:
    """For testing purposes."""
    csv_filename = 'test.csv'
    response = HttpResponse(
        content_type='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename={csv_filename}'
        },
    )

    writer = csv.writer(response)
    writer.writerow(['header1', 'header1', 'header1'])
    writer.writerow(['Foo', 'Bar', 'Baz'])
    writer.writerow(['A', 'B', 'C'])

    return response

def get_cash_report(req: HttpRequest) -> HttpResponse:
    """Generate response with cash level portfolio report in csv."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            return ReportGenerator().generate_report(
                int(target_id), report_type='cash_level_portfolio', to_http_response=True
            )
    return HttpResponseBadRequest

def get_position_report(req: HttpRequest) -> HttpResponse:
    """Generate response with position level portfolio report in csv."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            return ReportGenerator().generate_report(
                int(target_id), report_type='position_level_portfolio', to_http_response=True
            )
    return HttpResponseBadRequest

def get_bond_report(req: HttpRequest) -> HttpResponse:
    """Generate response with bond level portfolio report in csv."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            return ReportGenerator().generate_report(
                int(target_id), report_type='bond_level_portfolio', to_http_response=True
            )
    return HttpResponseBadRequest

def get_currency_report(req: HttpRequest) -> HttpResponse:
    """Generate response with currency level portfolio report in csv."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            return ReportGenerator().generate_report(
                int(target_id), report_type='currency_level_portfolio', to_http_response=True
            )
    return HttpResponseBadRequest

def get_exclusion_report(req: HttpRequest) -> HttpResponse:
    """Generate response with exclusions report in csv."""
    if req.GET:
        target_id = req.GET.get('target_id')
        if target_id:
            return ReportGenerator().generate_report(
                int(target_id), report_type='exclusions', to_http_response=True
            )
    return HttpResponseBadRequest

def get_cash_level_data(req: HttpRequest) -> HttpResponse:
    """Generate cash level data for live portfolio UI."""
    return HttpResponse(
        PortfolioGenerator().generate_cash_level_data(),
        content_type='application/json',
    )

def get_position_level_data(req: HttpRequest) -> HttpResponse:
    """Generate position level data for live portfolio UI."""
    return JsonResponse(PortfolioGenerator().generate_position_level_data(), safe=False)

def get_bond_level_data(req: HttpRequest) -> HttpResponse:
    """Generate bond level data for live portfolio UI."""
    return JsonResponse(PortfolioGenerator().generate_bond_level_data(), safe=False)

def get_currency_level_data(req: HttpRequest) -> HttpResponse:
    """Generate currency level data for live portfolio UI."""
    return JsonResponse(PortfolioGenerator().generate_currency_level_data(), safe=False)

def get_exclusion_data(req: HttpRequest) -> HttpResponse:
    """Generate exclusions data for live portfolio UI."""
    return HttpResponse(
        PortfolioGenerator().generate_exclusion_data(),
        content_type='application/json',
    )

def get_latest_event_id(req: HttpRequest) -> HttpResponse:
    """Gets latest event id for live portfolio UI."""
    return HttpResponse(common_fns.get_largest_event_id())