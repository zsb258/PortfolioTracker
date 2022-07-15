"""API URLs"""

from django.urls import path

from report_generator import views as report_views
from . import views as api_views

# URLs are prefixed with `api/`
urlpatterns = [
    # Endpoint to receive new events from POST request
    path('events/', api_views.process_event, name='api_process_event'),

    # Endpoint to generate and output reports to local folder
    path('output_reports', report_views.output_reports, name='api_output_reports'),

    # Routes for retrieving newest data for live portfolio dashboard
    path(
        'get_cash_portfolio',
        report_views.get_cash_level_data,
        name='get_cash_portfolio'
    ),
    path(
        'get_position_portfolio',
        report_views.get_position_level_data,
        name='get_position_portfolio'
    ),
    path(
        'get_bond_portfolio',
        report_views.get_bond_level_data,
        name='get_bond_portfolio'
    ),
    path(
        'get_currency_portfolio',
        report_views.get_currency_level_data,
        name='get_currency_portfolio'
    ),
    path(
        'get_exclusion_data',
        report_views.get_exclusion_data,
        name='get_exclusion_data'
    ),
    path(
        'get_latest_event_id',
        report_views.get_latest_event_id,
        name='get_latest_event_id'
    ),

    # Routes to download csv reports
    path(
        'get_dummy_report',
        report_views.get_dummy_report,
        name='get_dummy_report'
    ),
    path(
        'get_cash_report',
        report_views.get_cash_report,
        name='get_cash_report'
    ),
    path(
        'get_position_report',
        report_views.get_position_report,
        name='get_position_report'
    ),
    path(
        'get_bond_report',
        report_views.get_bond_report,
        name='get_bond_report'
    ),
    path(
        'get_currency_report',
        report_views.get_currency_report,
        name='get_currency_report'
    ),
    path(
        'get_exclusion_report',
        report_views.get_exclusion_report,
        name='get_exclusion_report'
    ),
]
