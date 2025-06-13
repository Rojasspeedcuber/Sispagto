from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pagamento
from .forms import PagamentoForm, CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def listar_pagamentos(request):
    pagamentos = Pagamento.objects.filter(owner=request.user)
    return render(request, 'core/listar_pagamentos.html', {'pagamentos': pagamentos})

@login_required
def adicionar_pagamento(request):
    if request.method == 'POST':
        form = PagamentoForm(request.POST)
        if form.is_valid():
            pagamento = form.save(commit=False)
            pagamento.owner = request.user # Associa o pagamento ao usuário logado
            pagamento.save()
            return redirect('listar_pagamentos')
    else:
        form = PagamentoForm()
    return render(request, 'core/adicionar_pagamento.html', {'form': form})