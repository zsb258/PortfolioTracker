import django


from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

def index(req: 'HttpRequest') -> 'HttpResponse':
    return render(req, 'index.html')