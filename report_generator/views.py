"""Route handlers for the UI."""

import csv

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(req: HttpRequest) -> HttpResponse:
    return render(req, 'index.html')

def get_report(req: HttpRequest) -> HttpResponse:
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