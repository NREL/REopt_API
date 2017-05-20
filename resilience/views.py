from django.shortcuts import render
import json
from django.http import HttpResponse
from django.views.static import serve

def index(request):
    "Resilience Model NRELs"
    return render(request,'template.html',{})
