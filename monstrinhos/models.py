import unicodedata

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


def normalizar_nome(nome):
    """Retira espaços repetidos e padroniza a representação dos acentos."""
    return unicodedata.normalize("NFC", " ".join((nome or "").split()))


class Monstrinho(models.Model):
    class Elemento(models.TextChoices):
        FOGO = "fogo", "Fogo"
        AGUA = "agua", "Água"
        PLANTA = "planta", "Planta"

    nome = models.CharField("nome", max_length=60, unique=True)
    # A chave oculta também identifica BOLINHA e Bolinha como o mesmo nome.
    nome_normalizado = models.CharField(max_length=180, unique=True, editable=False, blank=True)
    elemento = models.CharField("elemento", max_length=6, choices=Elemento.choices)
    nivel = models.PositiveSmallIntegerField(
        "nível", default=1, validators=[MinValueValidator(1), MaxValueValidator(50)]
    )
    alimentacoes = models.PositiveIntegerField("alimentações", default=0, editable=False)
    criado_em = models.DateTimeField("cadastrado em", auto_now_add=True)

    class Meta:
        ordering = ["nome"]
        verbose_name = "monstrinho"
        verbose_name_plural = "monstrinhos"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(nivel__gte=1, nivel__lte=50), name="nivel_entre_1_e_50"
            ),
            models.CheckConstraint(
                condition=models.Q(elemento__in=["fogo", "agua", "planta"]),
                name="elemento_valido",
            ),
            models.CheckConstraint(condition=~models.Q(nome=""), name="nome_nao_vazio"),
        ]

    def __str__(self):
        return self.nome

    def clean(self):
        super().clean()
        self.nome = normalizar_nome(self.nome)
        self.nome_normalizado = self.nome.casefold()
        if not self.nome:
            raise ValidationError({"nome": "Informe um nome para o monstrinho."})
        existentes = type(self).objects.filter(nome_normalizado=self.nome_normalizado)
        if self.pk:
            existentes = existentes.exclude(pk=self.pk)
        if existentes.exists():
            raise ValidationError({"nome": "Já existe um monstrinho com esse nome."})

    def save(self, *args, **kwargs):
        # A chave única também é preenchida ao usar objects.create() no terminal.
        self.nome = normalizar_nome(self.nome)
        self.nome_normalizado = self.nome.casefold()
        if kwargs.get("update_fields") is not None and "nome" in kwargs["update_fields"]:
            kwargs["update_fields"] = set(kwargs["update_fields"]) | {"nome_normalizado"}
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("monstrinhos:detalhe", kwargs={"pk": self.pk})
