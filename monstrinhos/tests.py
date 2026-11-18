"""Testes das regras da coleção e das requisições ao servidor."""
from io import StringIO

from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse

from .forms import MonstrinhoForm
from .models import Monstrinho


class MonstrinhoModelTests(TestCase):
    def test_representacao_e_url(self):
        monstrinho = Monstrinho.objects.create(nome="Fagulha", elemento="fogo")
        self.assertEqual(str(monstrinho), "Fagulha")
        self.assertEqual(monstrinho.nivel, 1)
        self.assertEqual(monstrinho.alimentacoes, 0)
        self.assertEqual(monstrinho.get_absolute_url(), f"/monstrinho/{monstrinho.pk}/")

    def test_nome_e_normalizado_ao_salvar(self):
        monstrinho = Monstrinho.objects.create(nome="  Astro   Azul  ", elemento="agua")
        self.assertEqual(monstrinho.nome, "Astro Azul")
        self.assertEqual(monstrinho.nome_normalizado, "astro azul")

    def test_full_clean_recusa_niveis_fora_do_intervalo(self):
        for nivel in [0, 51, -1]:
            with self.subTest(nivel=nivel), self.assertRaises(ValidationError):
                Monstrinho(nome="Broto", elemento="planta", nivel=nivel).full_clean()

    def test_full_clean_aceita_limites_do_intervalo(self):
        for nivel in [1, 50]:
            with self.subTest(nivel=nivel):
                Monstrinho(nome="Broto", elemento="planta", nivel=nivel).full_clean()

    def test_full_clean_recusa_elemento_invalido(self):
        with self.assertRaises(ValidationError):
            Monstrinho(nome="Raio", elemento="eletrico").full_clean()

    def test_banco_recusa_niveis_invalidos_sem_formulario(self):
        for nivel in [0, 51]:
            with self.subTest(nivel=nivel), self.assertRaises(IntegrityError), transaction.atomic():
                Monstrinho.objects.create(nome="Broto", elemento="planta", nivel=nivel)

    def test_banco_recusa_elemento_invalido(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Monstrinho.objects.create(nome="Raio", elemento="raio")

    def test_banco_recusa_nome_vazio(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Monstrinho.objects.create(nome="   ", elemento="fogo")

    def test_banco_recusa_nome_duplicado_inclusive_casefold_unicode(self):
        Monstrinho.objects.create(nome="Água", elemento="agua")
        for nome in ["Água", "água", " ÁGUA ", "A\u0301gua"]:
            with self.subTest(nome=nome), self.assertRaises(IntegrityError), transaction.atomic():
                Monstrinho.objects.create(nome=nome, elemento="agua")

    def test_renomear_atualiza_chave_unica(self):
        monstrinho = Monstrinho.objects.create(nome="Bolinha", elemento="planta")
        monstrinho.nome = " Verdinho "
        monstrinho.save(update_fields=["nome"])
        monstrinho.refresh_from_db()
        self.assertEqual(monstrinho.nome_normalizado, "verdinho")
        self.assertEqual(monstrinho.nome, "Verdinho")


class MonstrinhoFormTests(TestCase):
    def test_formulario_valido_normaliza_nome(self):
        form = MonstrinhoForm({"nome": "  Astro   Azul ", "elemento": "agua", "nivel": "50"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().nome, "Astro Azul")

    def test_niveis_invalidos_geram_erro_no_campo(self):
        for nivel in ["0", "51", "1.5", "texto", ""]:
            with self.subTest(nivel=nivel):
                form = MonstrinhoForm({"nome": "Fagulha", "elemento": "fogo", "nivel": nivel})
                self.assertFalse(form.is_valid())
                self.assertIn("nivel", form.errors)

    def test_nome_duplicado_gera_erro_no_campo(self):
        Monstrinho.objects.create(nome="Água Viva", elemento="agua")
        form = MonstrinhoForm({"nome": "  ÁGUA   VIVA ", "elemento": "planta", "nivel": "4"})
        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_nome_em_branco_e_recusado(self):
        form = MonstrinhoForm({"nome": "   ", "elemento": "fogo", "nivel": "1"})
        self.assertFalse(form.is_valid())
        self.assertIn("nome", form.errors)

    def test_elemento_fora_das_escolhas_e_recusado(self):
        form = MonstrinhoForm({"nome": "Raio", "elemento": "raio", "nivel": "1"})
        self.assertFalse(form.is_valid())
        self.assertIn("elemento", form.errors)

    def test_formulario_de_edicao_aceita_proprio_nome(self):
        monstrinho = Monstrinho.objects.create(nome="Broto", elemento="planta")
        form = MonstrinhoForm({"nome": "Broto", "elemento": "planta", "nivel": "5"}, instance=monstrinho)
        self.assertTrue(form.is_valid(), form.errors)


class MonstrinhoViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.fogo = Monstrinho.objects.create(nome="Fagulha", elemento="fogo", nivel=12)
        cls.agua = Monstrinho.objects.create(nome="Gotinha", elemento="agua", nivel=8)
        cls.planta = Monstrinho.objects.create(nome="Broto", elemento="planta", nivel=50)

    def test_home_renderiza_colecao_e_totais(self):
        response = self.client.get(reverse("monstrinhos:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "monstrinhos/home.html")
        self.assertEqual(response.context["total"], 3)
        self.assertEqual(response.context["total_fogo"], 1)
        self.assertEqual(response.context["total_agua"], 1)
        self.assertEqual(response.context["total_planta"], 1)

    def test_home_filtra_nome_e_elemento(self):
        response = self.client.get("/", {"q": "goti", "elemento": "agua"})
        self.assertEqual(list(response.context["monstrinhos"]), [self.agua])
        self.assertEqual(response.context["total"], 3)

    def test_filtro_invalido_nao_oculta_colecao(self):
        response = self.client.get("/", {"elemento": "raio"})
        self.assertEqual(len(response.context["monstrinhos"]), 3)
        self.assertEqual(response.context["elemento_selecionado"], "")

    def test_busca_sem_resultado(self):
        response = self.client.get("/", {"q": "inexistente"})
        self.assertEqual(len(response.context["monstrinhos"]), 0)
        self.assertEqual(response.status_code, 200)

    def test_contador_de_visitas_e_individual_por_sessao(self):
        self.client.get("/")
        response = self.client.get("/")
        self.assertEqual(response.context["visitas"], 2)
        outro_navegador = Client()
        self.assertEqual(outro_navegador.get("/").context["visitas"], 1)

    def test_detalhe_e_404_para_id_inexistente(self):
        response = self.client.get(self.fogo.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Fagulha")
        self.assertEqual(self.client.get("/monstrinho/9999/").status_code, 404)

    def test_formulario_abre(self):
        response = self.client.get(reverse("monstrinhos:cadastrar"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "monstrinhos/cadastrar.html")

    def test_cadastro_persiste_e_redireciona(self):
        response = self.client.post("/novo/", {"nome": "Marulho", "elemento": "agua", "nivel": "19"})
        monstrinho = Monstrinho.objects.get(nome="Marulho")
        self.assertRedirects(response, monstrinho.get_absolute_url())
        self.assertEqual(monstrinho.nivel, 19)

    def test_cadastro_invalido_preserva_dados_e_exibe_erros(self):
        response = self.client.post("/novo/", {"nome": "Fagulha", "elemento": "fogo", "nivel": "51"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("nome", response.context["form"].errors)
        self.assertIn("nivel", response.context["form"].errors)
        self.assertEqual(response.context["form"]["nome"].value(), "Fagulha")
        self.assertEqual(Monstrinho.objects.count(), 3)

    def test_alimentar_so_aceita_post(self):
        url = reverse("monstrinhos:alimentar", args=[self.fogo.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.fogo.refresh_from_db()
        self.assertEqual(self.fogo.alimentacoes, 0)

    def test_alimentar_atualiza_banco_e_redireciona(self):
        url = reverse("monstrinhos:alimentar", args=[self.fogo.pk])
        response = self.client.post(url)
        self.assertRedirects(response, self.fogo.get_absolute_url())
        self.fogo.refresh_from_db()
        self.assertEqual(self.fogo.nivel, 13)
        self.assertEqual(self.fogo.alimentacoes, 1)

    def test_alimentacoes_repetidas_nao_ultrapassam_nivel_50(self):
        self.fogo.nivel = 49
        self.fogo.save(update_fields=["nivel"])
        url = reverse("monstrinhos:alimentar", args=[self.fogo.pk])
        self.client.post(url)
        self.client.post(url)
        self.fogo.refresh_from_db()
        self.assertEqual(self.fogo.nivel, 50)
        self.assertEqual(self.fogo.alimentacoes, 2)

    def test_alimentar_no_nivel_maximo_conta_alimentacao(self):
        self.client.post(reverse("monstrinhos:alimentar", args=[self.planta.pk]))
        self.planta.refresh_from_db()
        self.assertEqual(self.planta.nivel, 50)
        self.assertEqual(self.planta.alimentacoes, 1)

    def test_alimentar_id_inexistente_retorna_404(self):
        self.assertEqual(self.client.post("/monstrinho/9999/alimentar/").status_code, 404)

    def test_post_sem_csrf_e_bloqueado(self):
        navegador = Client(enforce_csrf_checks=True)
        self.assertEqual(navegador.post("/novo/", {"nome": "Teste"}).status_code, 403)
        self.assertEqual(
            navegador.post(reverse("monstrinhos:alimentar", args=[self.fogo.pk])).status_code, 403
        )

    def test_post_com_csrf_valido_alimenta(self):
        navegador = Client(enforce_csrf_checks=True)
        navegador.get(self.fogo.get_absolute_url())
        token = navegador.cookies["csrftoken"].value
        response = navegador.post(
            reverse("monstrinhos:alimentar", args=[self.fogo.pk]),
            {"csrfmiddlewaretoken": token},
        )
        self.assertEqual(response.status_code, 302)

    def test_admin_exige_login(self):
        response = self.client.get("/admin/")
        self.assertRedirects(response, "/admin/login/?next=/admin/")


class PopularMonstrinhosTests(TestCase):
    def test_comando_e_idempotente_e_preserva_dados_existentes(self):
        existente = Monstrinho.objects.create(nome="FAGULHA", elemento="fogo", nivel=42)
        call_command("popular_monstrinhos", stdout=StringIO())
        call_command("popular_monstrinhos", stdout=StringIO())
        self.assertEqual(Monstrinho.objects.count(), 6)
        existente.refresh_from_db()
        self.assertEqual(existente.nivel, 42)
        self.assertEqual(existente.nome, "FAGULHA")
        self.assertSetEqual(set(Monstrinho.objects.values_list("elemento", flat=True)), {"fogo", "agua", "planta"})
