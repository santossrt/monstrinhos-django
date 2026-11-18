from django.contrib import admin

from .forms import MonstrinhoForm
from .models import Monstrinho


@admin.register(Monstrinho)
class MonstrinhoAdmin(admin.ModelAdmin):
    form = MonstrinhoForm
    list_display = ["nome", "elemento", "nivel", "alimentacoes", "criado_em"]
    list_filter = ["elemento"]
    search_fields = ["nome"]
    readonly_fields = ["alimentacoes", "criado_em"]
    fields = ["nome", "elemento", "nivel", "alimentacoes", "criado_em"]
