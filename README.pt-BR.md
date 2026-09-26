# STATICS LAB

🇧🇷 **Você está lendo em português** · 🇺🇸 [Read in English](README.md)

![Python](https://img.shields.io/badge/python-3.x-3776AB?logo=python&logoColor=white)
![Status](https://img.shields.io/badge/status-projeto%20educacional-yellow)

> Um laboratório computacional educacional para analisar uma treliça plana (2D) usando Python, álgebra linear e equilíbrio estático.

---

## Sumário

- [Visão Geral](#visão-geral)
- [Demonstração](#demonstração)
- [Definição do Problema](#definição-do-problema)
- [Modelo Físico](#modelo-físico)
- [Hipóteses](#hipóteses)
- [Modelo Matemático](#modelo-matemático)
- [Decomposição das Forças](#decomposição-das-forças)
- [Modelo de Carregamento](#modelo-de-carregamento)
- [Método Numérico](#método-numérico)
- [Validação do Equilíbrio](#validação-do-equilíbrio)
- [Exemplo](#exemplo)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [statics.py](#staticspy)
- [visualization.py](#visualizationpy)
- [Instalação](#instalação)
- [Executando o Projeto](#executando-o-projeto)
- [Filosofia de Desenvolvimento](#filosofia-de-desenvolvimento)
- [Roadmap](#roadmap)
- [Limitações](#limitações)
- [Validação](#validação)
- [Propósito Educacional](#propósito-educacional)
- [Tecnologias](#tecnologias)
- [Licença](#licença)

---

## Visão Geral

Uma **treliça** é uma estrutura formada por barras retas e esbeltas, conectadas em nós (juntas) e carregadas apenas nesses nós, de modo que cada barra suporte uma força puramente axial — tração ou compressão. Treliças são uma das estruturas fundamentais da engenharia mecânica e civil, e sua análise é um dos lugares mais claros onde **estática** e **álgebra linear** se encontram.

O **Statics Lab** é um pequeno projeto educacional que modela uma treliça plana, monta suas equações de equilíbrio e resolve as forças internas nas barras e as reações de apoio usando Python e NumPy. O objetivo não é construir uma ferramenta completa de análise estrutural, mas sim percorrer — do início ao fim, em código — a cadeia que conecta um problema físico de engenharia a um modelo matemático, e esse modelo a uma solução numérica.

A versão atual analisa uma única treliça plana fixa, **estaticamente determinada**, com:

- 5 nós;
- 7 barras;
- apoio articulado (pino) no nó A;
- apoio móvel (rolete) no nó B;
- uma carga vertical aplicada em um nó escolhido.

Versões futuras devem permitir que o usuário escolha onde a carga é aplicada e observe como as forças internas respondem (veja [Roadmap](#roadmap)).

## Demonstração

![Visualização da treliça](assets/truss_visualization.png)

*Recurso esperado — ainda não incluído no repositório.* Quando disponível, a imagem acima mostrará a geometria da treliça, os apoios e uma carga vertical aplicada no nó D, conforme gerado por `visualization.py`.

## Definição do Problema

A pergunta central que este projeto explora é:

> Como as forças internas de uma treliça estaticamente determinada mudam quando uma carga é aplicada em diferentes nós?

O fluxo de trabalho pretendido (e ainda parcialmente futuro) é:

1. Escolher um nó onde uma carga será aplicada.
2. Definir a massa de um bloco colocado nesse nó.
3. Calcular o peso correspondente.
4. Resolver as forças internas nas barras e as reações de apoio.
5. Classificar cada barra como tração ou compressão.
6. Verificar que as equações de equilíbrio são satisfeitas.
7. Eventualmente, avaliar a posição da carga segundo critérios explicitamente definidos.

O passo 7 — avaliar se um determinado nó é um local "adequado" para a carga — **ainda não está implementado**. É uma extensão planejada (veja [Roadmap](#roadmap) e [Limitações](#limitações)), não uma funcionalidade atual.

## Modelo Físico

**Nós**

| Nó | x (m) | y (m) |
|----|------:|------:|
| A  | 0.0   | 0.0   |
| B  | 4.0   | 0.0   |
| C  | 0.0   | 3.0   |
| D  | 2.0   | 1.5   |
| E  | 2.0   | 0.0   |

**Barras**

| Barra |
|-------|
| AC    |
| AD    |
| CD    |
| DE    |
| DB    |
| EB    |
| AE    |

- O nó **A** é um **apoio articulado (pino)** (restringe deslocamento horizontal e vertical).
- O nó **B** é um **apoio móvel (rolete)** (restringe apenas o deslocamento vertical).
- A estrutura é totalmente **plana (2D)**.
- **D** está no ponto médio do segmento **CB**.
- **E** está no ponto médio do segmento **AB**.
- O triângulo externo **A–B–C** tem lados de 4 m, 3 m e 5 m — a conhecida relação 3-4-5. Essa relação se aplica apenas à geometria externa; as barras internas (AD, CD, DB, DE, AE) têm geometrias e ângulos próprios e distintos.

## Hipóteses

O modelo se baseia em um conjunto de simplificações explícitas que definem seu escopo:

- treliça plana (2D);
- juntas idealizadas como pinos sem atrito;
- barras suportam apenas força axial (sem flexão);
- cargas aplicadas apenas nos nós;
- o apoio A fornece reações horizontal e vertical;
- o apoio B fornece apenas reação vertical;
- a estrutura está em equilíbrio estático;
- aceleração da gravidade $g = 9{,}81\ \text{m/s}^2$;
- o modelo atual suporta uma única carga vertical por vez;
- as barras são tratadas como elementos de treliça ideais e sem peso próprio;
- **deformação não é modelada atualmente**;
- **propriedades do material não são modeladas atualmente**;
- **flambagem não é modelada atualmente**;
- **distribuição de tensão dentro das barras não é modelada atualmente**.

## Modelo Matemático

Cada nó da treliça deve satisfazer o equilíbrio estático em ambas as direções:

$$
\sum F_x = 0 \qquad \sum F_y = 0
$$

Com 5 nós, isso resulta em:

$$
2 \times 5 = 10
$$

equações de equilíbrio independentes.

O vetor de incógnitas combina as 7 forças internas das barras com os 3 componentes de reação dos apoios:

$$
7 + 3 = 10
$$

incógnitas — exatamente o número de equações, o que é o que torna a treliça **estaticamente determinada**.

O sistema é montado em um único sistema linear:

$$
\mathbf{A}\mathbf{x} = \mathbf{b}
$$

onde:

- $\mathbf{A}$ é a matriz de equilíbrio, construída a partir dos vetores unitários de direção de cada barra que se encontra em cada nó;
- $\mathbf{x}$ é o vetor de incógnitas;
- $\mathbf{b}$ é o vetor de cargas externas.

$$
\mathbf{x} =
\begin{bmatrix}
F_{AC} & F_{AD} & F_{CD} & F_{DE} & F_{DB} & F_{EB} & F_{AE} & A_x & A_y & B_y
\end{bmatrix}^{T}
$$

Por convenção, uma força interna **positiva** significa **tração**, e uma força interna **negativa** significa **compressão**.

## Decomposição das Forças

Em vez de codificar manualmente um seno e um cosseno para cada barra, a implementação decompõe a força de cada barra ao longo do seu **vetor unitário de direção**, calculado diretamente a partir das coordenadas dos nós. Isso generaliza bem para qualquer geometria, sem tratar cada barra como um caso especial.

Como exemplo, para a barra **AD**:

$$
\vec{AD} = (2,\ 1{,}5), \qquad |\vec{AD}| = 2{,}5
$$

$$
\hat{u}_{AD} = \frac{(2,\ 1{,}5)}{2{,}5} = (0{,}8,\ 0{,}6)
$$

Aqui $0{,}8 = \cos\theta$ e $0{,}6 = \sin\theta$ para essa barra em particular. Uma força $F_{AD}$ atuando ao longo de AD contribui, portanto, com:

$$
F_x = 0{,}8\,F_{AD}, \qquad F_y = 0{,}6\,F_{AD}
$$

nas equações de equilíbrio de cada uma de suas extremidades. Todas as barras da treliça são tratadas da mesma forma, cada uma com seu próprio vetor unitário.

## Modelo de Carregamento

A carga aplicada vem de uma massa colocada em um nó:

$$
P = m\,g
$$

onde $P$ é a carga resultante em newtons, $m$ é a massa em quilogramas, e $g = 9{,}81\ \text{m/s}^2$.

Por exemplo, uma massa de 100 kg produz:

$$
P = 100 \times 9{,}81 = 981\ \text{N}
$$

A carga é aplicada **verticalmente para baixo** no nó escolhido. Massa e força/peso são mantidas como grandezas distintas em todo o modelo.

## Método Numérico

O sistema linear é montado automaticamente a partir da geometria e da conectividade da treliça — nada na matriz de equilíbrio é derivado manualmente para cada caso. O fluxo é:

```
Geometria
  ↓
Conectividade dos nós
  ↓
Vetores unitários
  ↓
Matriz de equilíbrio
  ↓
Vetor de cargas
  ↓
Sistema linear (A x = b)
  ↓
Solver do NumPy
  ↓
Forças internas + reações
```

O sistema linear é resolvido com:

```python
np.linalg.solve(A, b)
```

Trata-se de um clássico **método de equilíbrio de nós para uma treliça estaticamente determinada**, e não de um método dos elementos finitos (MEF/FEM). Não há matriz de rigidez, funções de forma ou discretização envolvidas.

## Validação do Equilíbrio

O projeto não se limita a produzir uma solução — ele também verifica se a solução de fato satisfaz o equilíbrio, calculando o resíduo:

$$
\mathbf{r} = \mathbf{A}\mathbf{x} + \mathbf{f}_{ext}
$$

Uma solução válida deve apresentar:

$$
\mathbf{r} \approx \mathbf{0}
$$

Valores muito pequenos e não nulos (da ordem da precisão de ponto flutuante) são esperados e são simplesmente consequência da aritmética de precisão finita, não um erro de modelagem.

## Exemplo

**Caso de carga:** uma massa de 100 kg posicionada no nó **D**.

$$
m = 100\ \text{kg}, \qquad P = 981\ \text{N}
$$

**Reações de apoio**

$$
A_x = 0\ \text{N}, \qquad A_y = 490{,}5\ \text{N}, \qquad B_y = 490{,}5\ \text{N}
$$

**Forças internas nas barras**

| Barra | Força (N) | Estado         |
|-------|----------:|----------------|
| AC    |      0,00 | Força nula     |
| AD    |   -817,50 | Compressão     |
| CD    |      0,00 | Força nula     |
| DE    |     ≈ 0   | Força nula     |
| DB    |   -817,50 | Compressão     |
| EB    |    654,00 | Tração         |
| AE    |    654,00 | Tração         |

Convenção de sinais: **positivo = tração, negativo = compressão**.

## Estrutura do Projeto

**Estrutura atual**

```
statics-lab/
├── src/
│   ├── statics.py
│   └── visualization.py
└── README.md
```

**Estrutura planejada**

```
statics-lab/
├── src/
│   ├── statics.py
│   └── visualization.py
├── tests/
├── README.md
├── README.pt-BR.md
├── LICENSE
└── .gitignore
```

## statics.py

`src/statics.py` é o núcleo do projeto. É responsável por:

- geometria da treliça (coordenadas dos nós);
- topologia da treliça (conectividade barra–nó);
- cálculo dos vetores unitários de direção de cada barra;
- montagem da matriz de equilíbrio;
- montagem do vetor de cargas;
- resolução do sistema linear;
- classificação da força de cada barra como tração ou compressão;
- validação dos resíduos de equilíbrio.

Um exemplo mínimo de uso:

```python
solution = solve_truss("D", 100.0)
```

Isso resolve a treliça para uma carga de 100 kg aplicada no nó D e retorna as forças internas e as reações de apoio.

## visualization.py

`src/visualization.py` é responsável pela parte gráfica do projeto. Atualmente, ele:

- desenha a geometria da treliça;
- desenha os nós;
- desenha os apoios;
- desenha a carga aplicada;
- exibe as forças resultantes.

Também é a base para futura interatividade (veja [Roadmap](#roadmap)), mas a interatividade completa — como clicar para posicionar uma carga — **ainda não existe**.

## Instalação

Clone o repositório:

```bash
git clone <repository-url>
cd statics-lab
```

Instale as dependências:

```bash
python -m pip install numpy matplotlib
```

Opcionalmente, use um ambiente virtual.

**Windows**

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install numpy matplotlib
```

**Linux / macOS**

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install numpy matplotlib
```

## Executando o Projeto

Execute o solver pelo terminal:

```bash
python src/statics.py
```

Isso monta a matriz de equilíbrio para a geometria atual, resolve as forças internas e as reações, e reporta os resultados.

Abra a visualização:

```bash
python src/visualization.py
```

Isso desenha a treliça, seus apoios e a carga aplicada.

## Filosofia de Desenvolvimento

O Statics Lab é construído de forma incremental, seguindo a mesma sequência que um engenheiro usaria para abordar o problema manualmente antes de escrever qualquer código:

1. modelar o problema físico;
2. derivar as equações governantes;
3. implementar um solver;
4. validar os resultados;
5. visualizar a estrutura e a solução;
6. adicionar interatividade;
7. expandir as capacidades do modelo.

A complexidade é adicionada em camadas, uma de cada vez — o projeto não usa, nem afirma usar, técnicas além do que está atualmente implementado.

## Roadmap

**Fase 1 — Solver Estrutural**

- [x] Definir geometria fixa
- [x] Definir conectividade da treliça
- [x] Definir reações de apoio
- [x] Montar matriz de equilíbrio
- [x] Resolver forças internas
- [x] Classificar tração/compressão
- [x] Verificar resíduos de equilíbrio

**Fase 2 — Visualização**

- [x] Desenhar geometria da treliça
- [x] Desenhar nós
- [x] Desenhar apoios
- [x] Desenhar carga aplicada
- [ ] Melhorar a visualização das forças
- [ ] Adicionar setas de reação
- [ ] Adicionar diagrama de engenharia mais elaborado

**Fase 3 — Interação**

- [ ] Selecionar nó de carga
- [ ] Selecionar massa
- [ ] Recalcular automaticamente
- [ ] Exibir valores de força
- [ ] Destacar tração/compressão
- [ ] Posicionamento interativo da carga

**Fase 4 — Interpretação Estrutural**

- [ ] Definir critérios explícitos para posicionamento da carga
- [ ] Identificar barras mais carregadas
- [ ] Introduzir métricas educacionais relacionadas à segurança
- [ ] Explicar as limitações do modelo simplificado

**Fase 5 — Extensões**

- [ ] Múltiplas cargas
- [ ] Geometrias de treliça mais complexas
- [ ] Análise de cisalhamento/momento onde fisicamente apropriado
- [ ] Cálculo de tensões
- [ ] Propriedades de material
- [ ] Considerações de flambagem
- [ ] Visualização educacional de falha

## Limitações

O modelo atual é intencionalmente simplificado. Ele:

- é bidimensional (2D) apenas;
- é estático, não dinâmico;
- trata a treliça como uma estrutura idealizada, articulada em pinos;
- aplica cargas apenas nos nós;
- **não** modela deformação;
- **não** modela elasticidade;
- **não** modela a tensão real dentro das seções das barras;
- **não** modela flambagem;
- **não** modela ligações reais (não articuladas);
- **não** considera imperfeições geométricas;
- **não** é uma ferramenta de dimensionamento estrutural;
- **não deve** ser usado para tomar decisões de segurança sobre estruturas reais.

Uma futura funcionalidade de "local adequado para a carga" (veja Roadmap, Fase 4) será uma classificação dentro deste modelo educacional, baseada em critérios explicitamente definidos — **não** será uma afirmação sobre se uma estrutura real é segura. Um local nunca é chamado de "seguro" ou "inseguro" apenas porque as forças internas calculadas são menores ou maiores.

## Validação

Além do cálculo dos resíduos (veja [Validação do Equilíbrio](#validação-do-equilíbrio)), os resultados devem ser verificados frente a:

- equilíbrio global de toda a estrutura;
- equilíbrio em cada nó individual;
- cálculos manuais (à mão);
- casos de carga simétricos;
- outros casos conhecidos e verificáveis de forma independente.

O primeiro caso de validação é a carga de 100 kg no nó D, descrita em [Exemplo](#exemplo): como D está horizontalmente na metade do caminho entre os apoios A e B, as reações verticais resultam iguais, $A_y = B_y = 490{,}5\ \text{N}$ — exatamente como esperado pela simetria.

## Propósito Educacional

O Statics Lab existe para estudar, na prática, a conexão entre:

- engenharia mecânica;
- estática;
- álgebra linear;
- Python;
- computação científica;
- visualização de dados;
- modelagem matemática.

O objetivo não é apenas produzir números — é percorrer e compreender toda a cadeia:

```
sistema físico
  → modelo matemático
  → modelo computacional
  → solução numérica
  → validação
  → visualização
```

## Tecnologias

- Python
- NumPy
- Matplotlib
- Git
- GitHub

## Licença

Os termos de licença ainda não foram definidos neste repositório. Caso um arquivo `LICENSE` seja adicionado (por exemplo, sob a MIT License), ele regerá os termos de uso — consulte o arquivo `LICENSE` do repositório para os termos atuais e oficiais.
