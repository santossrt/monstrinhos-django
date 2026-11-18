from django.core.management.base import BaseCommand

from monstrinhos.models import Monstrinho


class Command(BaseCommand):
    help = "Adiciona seis monstrinhos de exemplo sem duplicar nem alterar os existentes."

    def handle(self, *args, **options):
        exemplos = [
            ("Fagulha", "fogo", 12),
            ("Braseiro", "fogo", 24),
            ("Gotinha", "agua", 8),
            ("Marulho", "agua", 19),
            ("Broto", "planta", 5),
            ("Musguinho", "planta", 16),
        ]
        criados = 0
        for nome, elemento, nivel in exemplos:
            _, criado = Monstrinho.objects.get_or_create(
                nome_normalizado=nome.casefold(),
                defaults={"nome": nome, "elemento": elemento, "nivel": nivel},
            )
            criados += int(criado)
        self.stdout.write(self.style.SUCCESS(f"{criados} monstrinho(s) adicionado(s) à coleção."))
