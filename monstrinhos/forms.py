from django import forms

from .models import Monstrinho, normalizar_nome


class MonstrinhoForm(forms.ModelForm):
    class Meta:
        model = Monstrinho
        fields = ["nome", "elemento", "nivel"]
        widgets = {
            "nome": forms.TextInput(attrs={"placeholder": "Ex.: Fagulha", "autocomplete": "off"}),
            "nivel": forms.NumberInput(attrs={"min": 1, "max": 50}),
        }
        help_texts = {
            "nome": "Um nome único, com até 60 caracteres.",
            "elemento": "Escolha entre fogo, água e planta.",
            "nivel": "O nível inicial deve estar entre 1 e 50.",
        }
        error_messages = {
            "nome": {"unique": "Já existe um monstrinho com esse nome."},
            "nivel": {
                "min_value": "O nível deve ser no mínimo 1.",
                "max_value": "O nível deve ser no máximo 50.",
            },
        }

    def clean_nome(self):
        nome = normalizar_nome(self.cleaned_data["nome"])
        if not nome:
            raise forms.ValidationError("Informe um nome para o monstrinho.")
        return nome
