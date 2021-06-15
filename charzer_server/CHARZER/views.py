from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from customer.models import Charger

def homepage(request):
    chargers = Charger.objects
    return render(request, 'home.html', {'chargers':chargers})

def detail(request, charger_id):
    charger = get_object_or_404(Charger, pk=charger_id)
    return render(request, 'detail.html', {'charger':charger})