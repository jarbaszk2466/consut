import flet as ft
import requests
import threading
import time

URL_BASE = "http://192.168.1.86:5000/consulta/"
TEMPO_AUTO_BUSCA = 0.35

def main(page: ft.Page):

    page.title = "NossaConsulT V3"
    page.padding = 0
    page.bgcolor = "#000000"

    estado = {
        "lendo": False,
        "ultimo_valor": "",
        "ultimo_tempo": time.time()
    }

    # =========================
    # COMPONENTES
    # =========================
    txt_barras = ft.TextField(
        label="PRÓXIMO PRODUTO",
        width=420,
        height=80,
        text_size=24,
        autofocus=True,
        color="#FF2B2B",
        bgcolor="#1A0000",
        border_color="#FF0000"
    )

    res_nome = ft.Text(
        "SISTEMA OPERACIONAL",
        size=28,
        color="#FF2B2B",
        weight="bold",
        text_align="center"
    )

    res_preco = ft.Text(
        "R$ 0,00",
        size=80,
        color="#FF0000",
        weight="bold"
    )

    status = ft.Text(
        "⏳ AGUARDANDO...",
        size=18,
        color="#FF2B2B"
    )

    titulo = ft.Text(
        "📡 TERMINAL DE CONSULTA",
        size=30,
        color="#FF0000",
        weight="bold"
    )

    # =========================
    # FUNÇÕES
    # =========================
    def atualizar_ui(nome, preco, msg):
        res_nome.value = nome
        res_preco.value = preco
        status.value = msg

        txt_barras.value = ""
        estado["lendo"] = False

        try:
            txt_barras.focus()
        except:
            pass

        page.update()

    def consultar_thread(codigo):
        try:
            r = requests.get(f"{URL_BASE}{codigo}", timeout=3)

            if r.status_code == 200:
                dados = r.json()
                nome = str(dados.get("nome", "NÃO IDENTIFICADO")).upper()
                preco = f"R$ {float(dados.get('preco', 0)):.2f}"
                atualizar_ui(nome, preco, "✅ SUCESSO")
            else:
                atualizar_ui("❌ NÃO CADASTRADO", "", "⚠️ INVÁLIDO")

        except:
            atualizar_ui("🔌 SEM CONEXÃO", "", "❌ ERRO")

    def iniciar_busca(codigo):
        if estado["lendo"]:
            return

        codigo = codigo.strip()
        if not codigo:
            return

        estado["lendo"] = True
        status.value = "🔄 PROCESSANDO..."
        page.update()

        threading.Thread(
            target=consultar_thread,
            args=(codigo,),
            daemon=True
        ).start()

    # =========================
    # BOTÃO
    # =========================
    def clicar_buscar(e):
        iniciar_busca(txt_barras.value)

    botao = ft.Container(
        content=ft.Image(
            src="assets/botao.png",
            width=300,
            height=110,
            fit="contain"
        ),
        on_click=clicar_buscar
    )

    txt_barras.on_submit = lambda e: iniciar_busca(txt_barras.value)

    # =========================
    # AUTO BUSCA
    # =========================
    def monitorar():
        while True:
            time.sleep(0.1)

            valor = txt_barras.value

            if valor != estado["ultimo_valor"]:
                estado["ultimo_valor"] = valor
                estado["ultimo_tempo"] = time.time()
            else:
                if valor and not estado["lendo"]:
                    if time.time() - estado["ultimo_tempo"] > TEMPO_AUTO_BUSCA:
                        iniciar_busca(valor)

    threading.Thread(target=monitorar, daemon=True).start()

    # =========================
    # CARD (AGORA COM TÍTULO DENTRO)
    # =========================
    card = ft.Container(
        content=ft.Column(
            [
                titulo,      # 🔥 agora dentro
                txt_barras,
                botao,
                res_nome,
                res_preco,
                status
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=20
        ),
        padding=30,
        border_radius=20,
        bgcolor="#1A0000",
        border=ft.border.all(2, "#FF0000"),
        width=550
    )

    centro = ft.Row(
        [card],
        alignment=ft.MainAxisAlignment.CENTER,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
        expand=True
    )

    layout = ft.Stack(
        [
            ft.Container(
                content=ft.Image(
                    src="assets/fundo.png",
                    fit="cover"
                ),
                expand=True
            ),
            ft.Container(bgcolor="#00000088", expand=True),
            centro
        ],
        expand=True
    )

    page.add(layout)
    page.update()


ft.app(target=main)