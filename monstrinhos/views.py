from django.contrib import messages
from django.db import IntegrityError, transaction
from django.db.models import Case, Count, F, IntegerField, Q, Sum, Value, When
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MonstrinhoForm
from .models import Monstrinho


def home(request):
    monstrinhos = Monstrinho.objects.all()
    busca = request.GET.get("q", "").strip()
    elemento = request.GET.get("elemento", "")
    if busca:
        monstrinhos = monstrinhos.filter(nome__icontains=busca)
    if elemento in Monstrinho.Elemento.values:
        monstrinhos = monstrinhos.filter(elemento=elemento)
    else:
        elemento = ""

    # Sessão: cada navegador tem seu próprio contador de visitas à coleção.
    visitas = request.session.get("visitas", 0) + 1
    request.session["visitas"] = visitas
    totais = Monstrinho.objects.aggregate(
        total=Count("pk"),
        total_fogo=Count("pk", filter=Q(elemento="fogo")),
        total_agua=Count("pk", filter=Q(elemento="agua")),
        total_planta=Count("pk", filter=Q(elemento="planta")),
        total_alimentacoes=Sum("alimentacoes", default=0),
    )
    return render(
        request,
        "monstrinhos/home.html",
        {
            "monstrinhos": monstrinhos,
            "elementos": Monstrinho.Elemento.choices,
            "busca": busca,
            "elemento_selecionado": elemento,
            "visitas": visitas,
            **totais,
        },
    )


def detalhe(request, pk):
    monstrinho = get_object_or_404(Monstrinho, pk=pk)
    return render(request, "monstrinhos/detalhe.html", {"monstrinho": monstrinho})


def cadastrar(request):
    form = MonstrinhoForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid():
        try:
            with transaction.atomic():
                monstrinho = form.save()
        except IntegrityError:
            # A restrição também resolve dois cadastros simultâneos com o mesmo nome.
            form.add_error("nome", "Já existe um monstrinho com esse nome.")
        else:
            messages.success(request, f"{monstrinho.nome} chegou à sua coleção!")
            return redirect(monstrinho)
    return render(request, "monstrinhos/cadastrar.html", {"form": form})


@require_POST
def alimentar(request, pk):
    monstrinho = get_object_or_404(Monstrinho, pk=pk)
    # Uma única atualização no banco evita perder incrementos simultâneos.
    Monstrinho.objects.filter(pk=pk).update(
        alimentacoes=F("alimentacoes") + 1,
        nivel=Case(
            When(nivel__lt=50, then=F("nivel") + 1),
            default=Value(50),
            output_field=IntegerField(),
        ),
    )
    monstrinho.refresh_from_db()
    if monstrinho.nivel == 50:
        messages.success(request, f"{monstrinho.nome} foi alimentado! Nível máximo: 50.")
    else:
        messages.success(request, f"{monstrinho.nome} foi alimentado e chegou ao nível {monstrinho.nivel}!")
    return redirect(monstrinho)
