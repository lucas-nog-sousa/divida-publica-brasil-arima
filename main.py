import pandas as pd
codigo_sgs = 13762 
url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo_sgs}/dados?formato=json"

df = pd.read_json(url)

# Gráfico do histórico da Dívida Bruta

import matplotlib.pyplot as plt

# 1. Ajuste e preparação dos dados reais
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")
df_filtro = df[df["data"] >= "2014-12-01"].copy()

# 2. Criação dos dados de projeção
data_ultimo_real = df_filtro["data"].max()
valor_ultimo_real = df_filtro.loc[
    df_filtro["data"] == data_ultimo_real, "valor"
].values[0]

dados_projecao = {
    "data": [
        data_ultimo_real,
        pd.to_datetime("31/12/2026", format="%d/%m/%Y"),
        #pd.to_datetime("31/01/2027", format="%d/%m/%Y"),
    ],
    "valor": [valor_ultimo_real, 83.4],
}
df_proj = pd.DataFrame(dados_projecao)

# 3. Inicializa a figura
fig, ax = plt.subplots(figsize=(16, 8))

# 4. Plota os dados reais histórico
ax.plot(
    df_filtro["data"],
    df_filtro["valor"],
    marker="o",
    color="blue",
    linewidth=2.5,
    markersize=5,
    label="Histórico Real",
)

# 5. Plota a linha de projeção futura
ax.plot(
    df_proj["data"],
    df_proj["valor"],
    linestyle="--",
    marker="o",
    color="#2ca02c",
    linewidth=2.5,
    markersize=7,
    label="Projeção (Mercado)",
)

# 6. Identifica extremos do histórico
idx_pico = df_filtro["valor"].idxmax()
idx_ultimo = df_filtro["data"].idxmax()
inicio_dilma_dados = df_filtro[df_filtro["data"] == "2014-12-01"].index
inicio_dilma = inicio_dilma_dados[0] if len(inicio_dilma_dados) > 0 else -1
fim_dilma_dados = df_filtro[df_filtro["data"] == "2016-08-01"].index
fim_dilma = fim_dilma_dados[0] if len(fim_dilma_dados) > 0 else -1

# =========================================================================
# 7. Loop de Rótulos Reais com Caixas Transparentes (Bbox)
# =========================================================================
for idx, row in df_filtro.iterrows():
    mes = row["data"].month
    ano = row["data"].year
    e_dezembro = mes == 12
    e_agosto = idx == fim_dilma
    e_inicio = idx == inicio_dilma
    e_pico = idx == idx_pico
    e_ultimo = idx == idx_ultimo

    if (e_dezembro and ano % 2 == 0) or e_agosto or e_pico or e_ultimo or e_inicio:
        texto = f"{row['valor']:.1f}"

        # Ajuste de posição padrão para cima
        offset_y = 1.0
        ha_pos = "center"

        if e_pico and not (e_dezembro or e_agosto):
            texto += " (Pico - Pós-Pandemia)"
        elif e_ultimo:
            texto += " (Último Real)"
            ha_pos = "right"
            offset_y = 1.2

        # Se for o inicio do mandato da Dilma, colocamos acima de forma limpa
        if e_inicio:
            offset_y = 1.2
            ha_pos = "right"

        # Se for o fim do mandato da Dilma, colocamos acima de forma limpa
        if e_agosto:
            offset_y = 1.2
            ha_pos = "right"

        ax.text(
            row["data"],
            row["valor"] + offset_y,
            texto,
            color="red",
            fontsize=8,
            weight="bold",
            ha=ha_pos,
            # Adiciona a caixinha com fundo branco e 65% de opacidade
            bbox=dict(
                facecolor="white",
                alpha=0.65,
                edgecolor="none",
                boxstyle="round,pad=0.2",
            ),
        )
        ax.scatter(row["data"], row["valor"], color="red", s=40, zorder=5)

# =========================================================================
# 8. Rótulos de Projeção com Caixas Transparentes (Bbox)
# =========================================================================
for idx, row in df_proj.iterrows():
    if idx == 0:
        continue

    texto_proj = f"{row['valor']:.1f}%"

    if idx == 1:
        texto_proj += "\n(Proj. Mercado Dez/26)"
        offset_proj_y = -2.8
        ha_proj = "left"
    #elif idx == 2:
    #    texto_proj += "\n(Proj. Mercado 2027)"
    #    offset_proj_y = 1.0
    #    ha_proj = "center"

    ax.text(
        row["data"],
        row["valor"] + offset_proj_y,
        texto_proj,
        color="#1e5a1e",
        fontsize=9,
        weight="bold",
        ha=ha_proj,
        # Caixa protetora para a projeção
        bbox=dict(
            facecolor="white",
            alpha=0.75,
            edgecolor="none",
            boxstyle="round,pad=0.2",
        ),
    )

# =========================================================================
# 9. Formatação de Fundo dos Mandatos (Inalterado)
# =========================================================================
d_dilma_ini = pd.to_datetime("01/01/2011", format="%d/%m/%Y")
d_temer_ini = pd.to_datetime("01/08/2016", format="%d/%m/%Y")
d_bolsonaro_ini = pd.to_datetime("01/01/2019", format="%d/%m/%Y")
d_lula_ini = pd.to_datetime("01/01/2023", format="%d/%m/%Y")
d_fim_total = df_proj["data"].max()

lim_esquerda = max(df_filtro["data"].min(), d_dilma_ini)

ax.axvspan(lim_esquerda, d_temer_ini, color="#f9e6e6", alpha=0.5)
ax.axvspan(d_temer_ini, d_bolsonaro_ini, color="#fdfdfd", alpha=0.1)
ax.axvspan(d_bolsonaro_ini, d_lula_ini, color="#e6f0fa", alpha=0.5)
ax.axvspan(d_lula_ini, '2027-01-01', color="#fdf4e8", alpha=0.5)
ax.axvspan('2027-01-01', d_fim_total, color="#e8fdf0", alpha=0.5)


def rotular_presidente(data_inicio, data_fim, nome, y_pos=45):
    pos_x = data_inicio + (data_fim - data_inicio) / 2
    ax.text(
        pos_x,
        y_pos,
        nome,
        fontsize=11,
        weight="bold",
        ha="center",
        color="#444444",
    )


rotular_presidente(lim_esquerda, d_temer_ini, "Dilma")
rotular_presidente(d_temer_ini, d_bolsonaro_ini, "Temer")
rotular_presidente(d_bolsonaro_ini, d_lula_ini, "Bolsonaro")
rotular_presidente(d_lula_ini, d_fim_total, "Lula")

d_pandemia = pd.to_datetime("01/03/2020", format="%d/%m/%Y")
ax.axvline(d_pandemia, color="black", linestyle="--", alpha=0.4, linewidth=1)
ax.text(
    d_pandemia - pd.Timedelta(days=20),
    84,
    "Início da\npandemia",
    fontsize=8,
    ha="right",
    color="#555555",
)

ax.set_title(
    "Trajetória Mensal da Dívida Bruta (% PIB) com Projeções de Fechamento",
    fontsize=15,
    weight="bold",
    pad=15,
)
ax.set_xlabel("Período", fontsize=11)
ax.set_ylabel("% do PIB", fontsize=11)
ax.grid(True, linestyle="--", alpha=0.3)
ax.set_ylim(43, 95)  # Ajuste fino no topo para acomodar as novas caixas
ax.legend(loc="upper left", bbox_to_anchor=(0, 0.90))


# ============================================================
# VARIAÇÃO DA DÍVIDA POR GESTÃO PRESIDENCIAL
# ============================================================

gestoes = [
    ("Dilma", "2014-12-01", "2016-08-01"),
    ("Temer", "2016-08-01", "2019-01-01"),
    ("Bolsonaro", "2019-01-01", "2023-01-01"),
    ("Lula", "2023-01-01", None),
]

# Posição vertical das caixas
y_caixa = 91.5

for nome, inicio, fim in gestoes:
    inicio = pd.Timestamp(inicio)

    # Última gestão: vai até a última observação real
    if fim is None:
        periodo = df_filtro[df_filtro["data"] >= inicio].copy()
    else:
        fim = pd.Timestamp(fim)
        periodo = df_filtro[
            (df_filtro["data"] >= inicio) &
            (df_filtro["data"] < fim)
        ].copy()

    if len(periodo) < 2:
        continue

    primeiro = periodo.iloc[0]
    ultimo = periodo.iloc[-1]

    variacao = ultimo["valor"] - primeiro["valor"]
    cor = "#b22222" if variacao > 0 else "#174a8b"

    texto = (
        f"{variacao:+.1f} p.p.\n"
        f"{nome}"
    )

    # Centro temporal da gestão
    centro = primeiro["data"] + (
        ultimo["data"] - primeiro["data"]
    ) / 2

    ax.text(
        centro,
        y_caixa,
        texto,
        ha="center",
        va="center",
        fontsize=9,
        fontweight="bold",
        color="white",
        bbox=dict(
            boxstyle="square,pad=0.35",
            facecolor=cor,
            edgecolor="none",
            alpha=0.95,
        ),
        zorder=10,
    )

plt.tight_layout()
plt.show()

# Grafico final com a projeção feita pelo modelo arima

import numpy as np
from pmdarima.arima import auto_arima

# 1. Garante formato de data correto no histórico principal do seu DataFrame
df["data"] = pd.to_datetime(df["data"], format="%d/%m/%Y")

# =========================================================================
# 2. CAPTURA DOS DADOS EXÓGENOS REAIS (API DO BANCO CENTRAL)
# =========================================================================
cod_sgs = 5793
url_bcb = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{cod_sgs}/dados?formato=json"
df_primario_api = pd.read_json(url_bcb)
df_primario_api["valor"] = df_primario_api["valor"] * -1

# Ajusta as colunas e formatos vindos do Banco Central
df_primario_api["data"] = pd.to_datetime(
    df_primario_api["data"], format="%d/%m/%Y"
)
df_primario_api["resultado_primario"] = df_primario_api["valor"].astype(float)
df_primario_api = df_primario_api[["data", "resultado_primario"]]

# =========================================================================
# 3. CRUZAMENTO DE DADOS (MERGE) E FILTRO LULA 3
# =========================================================================
df_consolidado = pd.merge(df, df_primario_api, on="data", how="inner")
df_lula = df_consolidado[df_consolidado["data"] >= "2023-01-01"].copy()
df_lula = df_lula.set_index("data").asfreq("MS")

# =========================================================================
# 4. SEPARAÇÃO E TREINO DO MODELO COM VARIÁVEL EXÓGENA
# =========================================================================
y_treino = df_lula["valor"]  # Dívida Bruta
X_treino = df_lula[["resultado_primario"]]  # Resultado Primário Histórico

modelo_exogeno = auto_arima(
    y_treino,
    X=X_treino,
    start_p=1,
    start_q=1,
    max_p=3,
    max_q=3,
    m=1,
    seasonal=False,
    stepwise=True,
    suppress_warnings=True,
    error_action="ignore",
)

# =========================================================================
# 5. ESTRUTURAÇÃO DAS PROJEÇÕES FUTURAS (REQUER EXÓGENA FUTURA)
# =========================================================================
ultima_data_real = df_lula.index.max()
valor_ultimo_real = float(df_lula.loc[ultima_data_real, "valor"])
ultimo_primario_real = float(df_lula.loc[ultima_data_real, "resultado_primario"])
# Projeção de mercado para dezembro de 2026
valor_mercado_dez = 83.4
data_dez_26 = pd.to_datetime("2026-12-01")
#ata_jan_27 = pd.to_datetime("2027-01-01")

# Descobre a quantidade exata de meses de projeção
passos_ate_fim = int(
    (data_dez_26.year - ultima_data_real.year) * 12
    + (data_dez_26.month - ultima_data_real.month)
)

# Cria o index temporal para os meses projetados
datas_projetadas = pd.date_range(
    start=ultima_data_real + pd.offsets.MonthBegin(1),
    periods=passos_ate_fim,
    freq="MS",
)

# Cenário de Projeção para a Exógena: Mantém o último esforço fiscal conhecido estável
X_futuro = pd.DataFrame(
    {"resultado_primario": [ultimo_primario_real] * passos_ate_fim},
    index=datas_projetadas,
)

# Executa a predição passando a matriz exógena futura obrigatoriamente
previsoes_brutas = modelo_exogeno.predict(
    n_periods=passos_ate_fim, X=X_futuro
)

valor_proj_dez = float(previsoes_brutas.loc[data_dez_26])
#valor_proj_jan = float(previsoes_brutas.loc[data_jan_27])

dados_projecao = {
    "data": [ultima_data_real, data_dez_26],#, data_jan_27],
    "valor": [valor_ultimo_real, valor_proj_dez],#, valor_proj_jan],
}
df_proj = pd.DataFrame(dados_projecao)

# =========================================================================
# 6. MONTAGEM DO GRÁFICO (16x8 COM ZOOM E VARIÁVEL EXÓGENA)
# =========================================================================
fig, ax = plt.subplots(figsize=(16, 8))
df_visual = df_lula.reset_index()

# Linha Histórica Real (Período Lula)
ax.plot(
    df_visual["data"],
    df_visual["valor"],
    marker="o",
    color="blue",
    linewidth=2.5,
    markersize=6,
    label="Histórico Real (Lula 3)",
)

# Linha Tracejada do Auto ARIMA + Variável Exógena (SARIMAX)
ax.plot(
    df_proj["data"],
    df_proj["valor"],
    linestyle="--",
    marker="o",
    color="#2ca02c",
    linewidth=2.5,
    markersize=8,
    label=f"Projeção SARIMAX {modelo_exogeno.order} (Com Resultado Primário)",
)

# Rótulos das Caixinhas Transparentes (Pontos Reais)
idx_pico = df_visual["valor"].idxmax()
idx_ultimo = df_visual.index.max()
idx_inicio = df_visual.index.min()

for idx, row in df_visual.iterrows():
    e_pico = idx == idx_pico
    e_ultimo = idx == idx_ultimo
    e_inicio = idx == idx_inicio
    mes = row["data"].month

    if e_pico or e_ultimo or e_inicio or mes == 12:
        texto = f"{row['valor']:.1f}"
        offset_y = 0.6
        ha_pos = "center"

        if e_pico and not e_ultimo:
            texto += " (Pico Período)"
        elif e_ultimo:
            texto += " (Último Real)"
            ha_pos = "right"
            offset_y = 0.4

        ax.text(
            row["data"],
            row["valor"] + offset_y,
            texto,
            color="red",
            fontsize=9,
            weight="bold",
            ha=ha_pos,
            bbox=dict(
                facecolor="white",
                alpha=0.7,
                edgecolor="none",
                boxstyle="round,pad=0.2",
            ),
        )
        ax.scatter(row["data"], row["valor"], color="red", s=50, zorder=5)

# Caixinhas de Texto Verdes para as previsões com impacto da exógena
for idx, row in df_proj.iterrows():
    if idx == 0:
        continue

    texto_proj = f"{row['valor']:.1f}%"
    if idx == 1:
        texto_proj += "\n(Previsão Modelo Dez/26)"
        offset_proj_y = 0.5
        ha_proj = "left"
    #elif idx == 2:
    #    texto_proj += "\n(Previsão 2027)"
    #    offset_proj_y = 0.5
    #    ha_proj = "center"

    ax.text(
        row["data"],
        row["valor"] + offset_proj_y,
        texto_proj,
        color="#1e5a1e",
        fontsize=9,
        weight="bold",
        ha=ha_proj,
        bbox=dict(
            facecolor="white",
            alpha=0.8,
            edgecolor="none",
            boxstyle="round,pad=0.2",
        ),
    )

# =========================================================================
# PROJEÇÃO COMPARATIVA DO MERCADO — DEZ/2026
# =========================================================================
ax.scatter(
    data_dez_26,
    valor_mercado_dez,
    color="red",
    marker="D",
    s=100,
    zorder=10,
    label="Projeção de Mercado (Dez/26)",
)

ax.annotate(
    f"{valor_mercado_dez:.1f}%\n(Proj. Mercado Dez/26)",
    xy=(data_dez_26, valor_mercado_dez),
    xytext=(12, -40), #posição da caixa
    textcoords="offset points",
    color="red",
    fontsize=9,
    fontweight="bold",
    ha="left",
    va="bottom",
    bbox=dict(
        facecolor="white",
        alpha=0.9,
        edgecolor="red",
        boxstyle="round,pad=0.3",
    ),
    arrowprops=dict(
        arrowstyle="->",
        color="red",
        lw=1.2,
    ),
)

# Formatação e Identificação de Fundo dos Períodos
d_fim_total = df_proj["data"].max()
ax.axvspan(df_visual["data"].min(), "2026-12-01", color="#fdf4e8", alpha=0.4)
ax.axvspan("2026-12-01", d_fim_total, color="#e8fdf0", alpha=0.4)

pos_texto_x = df_visual["data"].min() + (d_fim_total - df_visual["data"].min()) / 2
ax.text(
    pos_texto_x,
    df_visual["valor"].min() - 2,
    "Governo Lula 3 (Foco do Modelo com Variável Exógena)",
    fontsize=12,
    weight="bold",
    ha="center",
    color="#444444",
)

# Estética Final
ax.set_title(
    "Modelo Preditivo SARIMAX aplicado ao Endividamento Público Recente (Exógena: Resultado Primário)",
    fontsize=13,
    weight="bold",
    pad=15,
)
ax.set_xlabel("Meses de Amostragem", fontsize=11)
ax.set_ylabel("% do PIB", fontsize=11)
ax.grid(True, linestyle="--", alpha=0.3)

y_lim_min = df_visual["valor"].min() - 4
y_lim_max = max(df_visual["valor"].max(), df_proj["valor"].max(),valor_mercado_dez) + 4
ax.set_ylim(y_lim_min, y_lim_max)

ax.legend(loc="upper left")
plt.tight_layout()
plt.show()
