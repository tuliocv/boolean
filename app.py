import os
import csv
import random
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st


# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Jogo de Boolean (Java)", page_icon="✅", layout="centered")
st.title("✅ Jogo: Boolean em Java")
st.caption(":)")


# =========================
# ADMIN CREDENTIALS
# =========================
def get_admin_credentials():
    try:
        user = st.secrets["admin"]["user"]
        pwd = st.secrets["admin"]["pass"]
        return user, pwd
    except Exception:
        return os.getenv("ADMIN_USER", "admin"), os.getenv("ADMIN_PASS", "admin")


ADMIN_USER, ADMIN_PASS = get_admin_credentials()


# =========================
# STORAGE (CSV)
# =========================
DATA_DIR = Path("data")
SCORES_FILE = DATA_DIR / "boolean_scores.csv"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# NOVO: separa acerto oficial e pontuação final
CSV_HEADERS = [
    "timestamp_utc",
    "student_name",
    "base_correct",        # acertos oficiais (0..30)
    "final_points",        # acertos + bônus
    "total",
    "percent_official",    # % oficial baseado só em acertos
    "max_streak"
]


def ensure_scores_file():
    if not SCORES_FILE.exists():
        with open(SCORES_FILE, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(CSV_HEADERS)


def load_scores():
    ensure_scores_file()
    rows = []
    with open(SCORES_FILE, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["base_correct"] = int(row.get("base_correct", 0))
                row["final_points"] = int(row.get("final_points", 0))
                row["total"] = int(row.get("total", 0))
                row["percent_official"] = float(row.get("percent_official", 0.0))
                row["max_streak"] = int(row.get("max_streak", 0))
                rows.append(row)
            except Exception:
                pass
    return rows


def append_score(student_name: str, base_correct: int, final_points: int, total: int, max_streak: int):
    ensure_scores_file()
    percent_official = (base_correct / total) * 100 if total else 0.0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(SCORES_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([
            ts, student_name, base_correct, final_points, total, f"{percent_official:.2f}", max_streak
        ])


def clear_scores():
    if SCORES_FILE.exists():
        SCORES_FILE.unlink()
    ensure_scores_file()


# =========================
# UI HELPERS
# =========================
def difficulty_bar(level: str):
    mapping = {"Fácil": 30, "Médio": 60, "Difícil": 90}
    colors = {"Fácil": "🟩", "Médio": "🟨", "Difícil": "🟥"}
    value = mapping.get(level, 50)
    st.markdown(f"**Dificuldade:** {colors.get(level,'🟨')} {level}")
    st.progress(value / 100)


def streak_bonus_points(streak: int) -> int:
    # streak=1 -> +0, streak=2 -> +1, streak=3 -> +2, ...
    return max(0, streak - 1)


def shuffle_options_keep_answer(options: list[str], answer: str) -> list[str]:
    """
    Embaralha as opções para reduzir padrão (A/B) e manter a resposta presente.
    """
    opts = options[:]
    random.shuffle(opts)
    # garantia: resposta está na lista (se o autor errou, corrige)
    if answer not in opts:
        opts[-1] = answer
        random.shuffle(opts)
    return opts


# =========================
# QUESTÕES (30) — variedade + explicação didática
# =========================
# OBS: mantendo sua lista, mas reforçando as explicações de forma mais didática.
QUESTIONS = [
    # --- Fácil ---
    {
        "id": "Q01", "level": "Fácil",
        "prompt": "Qual das declarações abaixo é válida em Java?",
        "options": ['boolean ok = true;', 'boolean ok = "true";', 'boolean ok = 1;', "boolean ok = True;"],
        "answer": 'boolean ok = true;',
        "explain": (
            "Em Java, o tipo **boolean** só aceita **dois valores literais**: **true** e **false**.\n"
            "- `\"true\"` (com aspas) é **String**, não boolean.\n"
            "- `1` é inteiro.\n"
            "- `True` (T maiúsculo) **não existe** em Java (é `true`)."
        ),
    },
    {
        "id": "Q02", "level": "Fácil",
        "prompt": "Qual expressão resulta em um boolean (true/false)?",
        "options": ["10 + 5", "idade >= 18", "nota * 2", '"18"'],
        "answer": "idade >= 18",
        "explain": (
            "Operadores de comparação (`>=`, `<=`, `>`, `<`, `==`, `!=`) **sempre produzem boolean**.\n"
            "- `10 + 5` e `nota * 2` produzem números.\n"
            "- `\"18\"` é texto (String)."
        ),
    },
    {
        "id": "Q03", "level": "Fácil",
        "prompt": "Qual operador representa o 'E' lógico em Java?",
        "options": ["&&", "||", "!", "=="],
        "answer": "&&",
        "explain": (
            "`&&` é o operador lógico **AND (E)**.\n"
            "- Só é `true` quando **as duas partes** são true."
        ),
    },
    {
        "id": "Q04", "level": "Fácil",
        "prompt": "Qual operador representa o 'OU' lógico em Java?",
        "options": ["&&", "||", "!=", "<="],
        "answer": "||",
        "explain": (
            "`||` é o operador lógico **OR (OU)**.\n"
            "- É `true` quando **pelo menos uma parte** é true."
        ),
    },
    {
        "id": "Q05", "level": "Fácil",
        "prompt": "Qual operador representa o 'NÃO' lógico em Java?",
        "options": ["!", "&&", "||", "=="],
        "answer": "!",
        "explain": (
            "`!` é o operador lógico **NOT (NÃO)**.\n"
            "- Inverte o valor: `!true` vira `false` e `!false` vira `true`."
        ),
    },
    {
        "id": "Q06", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int a = 5, b = 7;\nSystem.out.println(a > b);",
        "options": ["true", "false", "5", "7"],
        "answer": "false",
        "explain": (
            "Passo a passo:\n"
            "1) `a > b` vira `5 > 7`\n"
            "2) `5 > 7` é **falso**\n"
            "3) imprime `false`."
        ),
    },
    {
        "id": "Q07", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int a = 5;\nSystem.out.println(a == 5);",
        "options": ["true", "false", "5", "erro"],
        "answer": "true",
        "explain": (
            "`==` compara **igualdade**.\n"
            "1) `a == 5` vira `5 == 5`\n"
            "2) é **verdadeiro** → imprime `true`."
        ),
    },
    {
        "id": "Q08", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "boolean matriculado = false;\nSystem.out.println(!matriculado);",
        "options": ["true", "false", "erro", "!false"],
        "answer": "true",
        "explain": (
            "1) `matriculado` vale `false`\n"
            "2) `!matriculado` = `!false` = `true`\n"
            "3) imprime `true`."
        ),
    },
    {
        "id": "Q09", "level": "Fácil",
        "prompt": "Qual alternativa descreve melhor um boolean?",
        "options": ["Um texto com letras", "Um número inteiro", "Um tipo que representa verdadeiro/falso", "Um tipo para decimais"],
        "answer": "Um tipo que representa verdadeiro/falso",
        "explain": "boolean é um tipo lógico com apenas **dois valores possíveis**: `true` ou `false`.",
    },
    {
        "id": "Q10", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int nota = 6;\nSystem.out.println(nota >= 6);",
        "options": ["true", "false", "6", "erro"],
        "answer": "true",
        "explain": (
            "1) `nota >= 6` vira `6 >= 6`\n"
            "2) é verdadeiro porque **igual** também conta no `>=`.\n"
            "3) imprime `true`."
        ),
    },

    # --- Médio ---
    {
        "id": "Q11", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "int idade = 16;\nboolean temRG = true;\nSystem.out.println(idade >= 18 && temRG);",
        "options": ["true", "false", "16", "erro"],
        "answer": "false",
        "explain": (
            "Vamos quebrar a expressão em duas partes:\n"
            "1) `idade >= 18` → `16 >= 18` → **false**\n"
            "2) `temRG` → **true**\n"
            "3) `false && true` → **false** (no AND, se uma parte é false, tudo é false)."
        ),
    },
    {
        "id": "Q12", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "int idade = 16;\nboolean temRG = true;\nSystem.out.println(idade >= 18 || temRG);",
        "options": ["true", "false", "erro", "16"],
        "answer": "true",
        "explain": (
            "No OR, basta uma parte ser true:\n"
            "1) `idade >= 18` → `16 >= 18` → false\n"
            "2) `temRG` → true\n"
            "3) `false || true` → **true**."
        ),
    },
    {
        "id": "Q13", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "boolean matriculado = false;\nSystem.out.println(!!matriculado);",
        "options": ["true", "false", "erro", "!!false"],
        "answer": "false",
        "explain": (
            "Dupla negação cancela:\n"
            "1) `!matriculado` → `!false` → true\n"
            "2) `!!matriculado` → `!true` → false\n"
            "Resultado final: `false`."
        ),
    },
    {
        "id": "Q14", "level": "Médio",
        "prompt": "Traduza: “Entra se tem ingresso E não está banido”.",
        "options": ["temIngresso && !banido", "temIngresso || !banido", "!temIngresso && banido", "temIngresso && banido"],
        "answer": "temIngresso && !banido",
        "explain": (
            "A frase tem dois pedaços:\n"
            "- 'tem ingresso'  → `temIngresso`\n"
            "- 'não está banido' → `!banido`\n"
            "E o 'E' vira `&&`: `temIngresso && !banido`."
        ),
    },
    {
        "id": "Q15", "level": "Médio",
        "prompt": "Traduza: “Pode fazer substitutiva se faltou OU teve atestado”.",
        "options": ["faltou && temAtestado", "faltou || temAtestado", "!faltou || temAtestado", "faltou && !temAtestado"],
        "answer": "faltou || temAtestado",
        "explain": (
            "No 'OU', uma condição basta:\n"
            "Se faltou **ou** tem atestado → `faltou || temAtestado`."
        ),
    },
    {
        "id": "Q16", "level": "Médio",
        "prompt": "Traduza: “Desconto se é aluno E (pagou em dia OU tem bolsa)”.",
        "options": ["ehAluno && pagouEmDia || temBolsa", "ehAluno && (pagouEmDia || temBolsa)", "(ehAluno && pagouEmDia) || temBolsa", "ehAluno || (pagouEmDia && temBolsa)"],
        "answer": "ehAluno && (pagouEmDia || temBolsa)",
        "explain": (
            "A frase exige **ser aluno** e, além disso, cumprir **uma** de duas condições.\n"
            "Por isso precisamos de parênteses:\n"
            "`ehAluno && (pagouEmDia || temBolsa)`."
        ),
    },
    {
        "id": "Q17", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "int idade = 18;\nboolean autorizacao = false;\nSystem.out.println(idade >= 18 && autorizacao);",
        "options": ["true", "false", "erro", "18"],
        "answer": "false",
        "explain": (
            "1) `idade >= 18` → `18 >= 18` → true\n"
            "2) `autorizacao` → false\n"
            "3) `true && false` → **false**."
        ),
    },
    {
        "id": "Q18", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = false;\nSystem.out.println(!(a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "1) Avalie dentro dos parênteses: `a && b` → `true && false` → false\n"
            "2) Negue o resultado: `!false` → true\n"
            "Imprime `true`."
        ),
    },
    {
        "id": "Q19", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = false;\nSystem.out.println(a && (b || true));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "1) Primeiro parênteses: `b || true` → `false || true` → true\n"
            "2) Depois AND: `a && true` → `true && true` → true\n"
            "Imprime `true`."
        ),
    },
    {
        "id": "Q20", "level": "Médio",
        "prompt": "Qual condição é equivalente a “NÃO (A OU B)”?",
        "options": ["!A || !B", "!A && !B", "A && B", "!(A && B)"],
        "answer": "!A && !B",
        "explain": (
            "Lei de De Morgan:\n"
            "`!(A || B)` equivale a `(!A && !B)`.\n"
            "Ou seja: para NÃO ter (A ou B), precisa não ter A **e** não ter B."
        ),
    },

    # --- Difícil ---
    {
        "id": "Q21", "level": "Difícil",
        "prompt": "Precedência: o que imprime?",
        "code": "boolean x = true;\nboolean y = false;\nSystem.out.println(x || y && false);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "Regra de precedência: `&&` é avaliado antes de `||`.\n"
            "1) `y && false` → `false && false` → false\n"
            "2) `x || (resultado)` → `true || false` → true\n"
            "Imprime `true`."
        ),
    },
    {
        "id": "Q22", "level": "Difícil",
        "prompt": "Precedência: o que imprime?",
        "code": "boolean x = false;\nboolean y = true;\nSystem.out.println(x || y && false);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "false",
        "explain": (
            "1) `y && false` → `true && false` → false\n"
            "2) `x || false` → `false || false` → false\n"
            "Imprime `false`."
        ),
    },
    {
        "id": "Q23", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "int a = 2;\nint b = 3;\nSystem.out.println(!(a > b) && (b > 0));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "1) `a > b` → `2 > 3` → false\n"
            "2) `!(a > b)` → `!false` → true\n"
            "3) `b > 0` → `3 > 0` → true\n"
            "4) `true && true` → true\n"
            "Imprime `true`."
        ),
    },
    {
        "id": "Q24", "level": "Difícil",
        "prompt": "Qual expressão é equivalente a “A OU (B E C)”?",
        "options": ["(A || B) && C", "A || (B && C)", "(A && B) || C", "A && (B || C)"],
        "answer": "A || (B && C)",
        "explain": (
            "A frase diz: é A **ou** (B **e** C juntos).\n"
            "Então precisa manter o AND agrupado: `A || (B && C)`."
        ),
    },
    {
        "id": "Q25", "level": "Difícil",
        "prompt": "Qual condição representa: “loginOk se usuario e senha não estão vazios”?",
        "options": [
            'usuario != "" && senha != ""',
            'usuario == "" && senha == ""',
            'usuario != "" || senha != ""',
            '!usuario && !senha'
        ],
        "answer": 'usuario != "" && senha != ""',
        "explain": (
            "A intenção é: **os dois** precisam estar preenchidos.\n"
            "Isso pede `&&`.\n"
            "Obs.: em Java real, strings devem ser checadas com `.isEmpty()`/`.equals()`."
        ),
    },
    {
        "id": "Q26", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean a = false;\nboolean b = false;\nSystem.out.println(!(a || b) || (a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "1) `a || b` → `false || false` → false\n"
            "2) `!(a || b)` → `!false` → true\n"
            "3) `a && b` → `false && false` → false\n"
            "4) `true || false` → true\n"
            "Imprime `true`."
        ),
    },
    {
        "id": "Q27", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = true;\nSystem.out.println(!(a && b) || (a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "Seja `X = (a && b)`.\n"
            "A expressão vira `!X || X`.\n"
            "Isso é sempre verdadeiro (tautologia): se X é true, o lado direito é true; se X é false, `!X` é true."
        ),
    },
    {
        "id": "Q28", "level": "Difícil",
        "prompt": "Qual é o resultado de: true && false || true ?",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": (
            "Precedência:\n"
            "1) `true && false` → false\n"
            "2) `false || true` → true\n"
            "Resultado: true."
        ),
    },
    {
        "id": "Q29", "level": "Difícil",
        "prompt": "Qual expressão é equivalente a “(A E B) OU (A E C)”?",
        "options": ["A && (B || C)", "(A || B) && C", "(A && B) || C", "A || (B && C)"],
        "answer": "A && (B || C)",
        "explain": (
            "Fatorando A:\n"
            "(A && B) || (A && C) = A && (B || C).\n"
            "Isso reduz repetição e mostra a estrutura lógica."
        ),
    },
    {
        "id": "Q30", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean A = false;\nboolean B = true;\nboolean C = true;\nSystem.out.println(A || B && !C);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "false",
        "explain": (
            "Precedência: `!` depois `&&` depois `||`.\n"
            "1) `!C` → `!true` → false\n"
            "2) `B && !C` → `true && false` → false\n"
            "3) `A || (resultado)` → `false || false` → false\n"
            "Imprime `false`."
        ),
    },
]


# =========================
# SESSION STATE
# =========================
def reset_quiz_order():
    order = list(range(len(QUESTIONS)))
    random.shuffle(order)
    st.session_state.q_order = order


def reset_quiz_progress():
    st.session_state.q_index = 0

    # NOVO: separa acertos oficiais e pontuação final
    st.session_state.base_correct = 0     # acertos (0..30)
    st.session_state.final_points = 0     # acertos + bônus

    st.session_state.streak = 0
    st.session_state.max_streak = 0

    st.session_state.show_feedback = False
    st.session_state.last_correct = None
    st.session_state.last_explain = None
    st.session_state.last_answer = None
    st.session_state.last_bonus = 0

    st.session_state.saved_score = False


def reset_all():
    reset_quiz_order()
    reset_quiz_progress()


if "student_name" not in st.session_state:
    st.session_state.student_name = ""
if "admin_authed" not in st.session_state:
    st.session_state.admin_authed = False
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "q_order" not in st.session_state:
    reset_all()


# =========================
# NAV
# =========================
st.sidebar.title("📌 Menu")
view = st.sidebar.radio("Ir para:", ["👤 Aluno", "🔐 Admin"], index=0)


# ==========================================================
# VIEW: STUDENT
# ==========================================================
if view == "👤 Aluno":
    st.subheader("👤 Área do aluno")
    st.caption("Digite seu nome para iniciar o quiz de boolean. O % oficial considera apenas acertos (sem bônus).")

    if not st.session_state.student_name:
        nome = st.text_input("Nome do aluno:", placeholder="Ex.: Maria Silva")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚀 Iniciar"):
                nome_limpo = (nome or "").strip()
                if len(nome_limpo) < 3:
                    st.warning("⚠️ Informe um nome com pelo menos 3 caracteres.")
                else:
                    st.session_state.student_name = nome_limpo
                    reset_all()
                    st.rerun()
        with col2:
            if st.button("🧹 Limpar"):
                st.session_state.student_name = ""
                reset_all()
                st.rerun()

    else:
        total = len(QUESTIONS)

        # % oficial (sem bônus)
        percent_official_live = (st.session_state.base_correct / total) * 100 if total else 0.0

        st.success(f"Aluno: **{st.session_state.student_name}**")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("✅ Acertos oficiais", f"{st.session_state.base_correct}/{total}")
        with c2:
            st.metric("📈 % oficial", f"{percent_official_live:.1f}%")
        with c3:
            st.metric("🏁 Pontuação final", st.session_state.final_points)
        with c4:
            st.metric("🔥 Streak", st.session_state.streak)

        st.caption("Pontuação final = acertos + bônus por sequência. % oficial = somente acertos / total.")

        # fim
        if st.session_state.q_index >= total:
            st.success("🎉 Quiz finalizado!")

            percent_official = (st.session_state.base_correct / total) * 100 if total else 0.0

            st.metric("✅ Acertos oficiais", f"{st.session_state.base_correct}/{total}")
            st.metric("📈 % oficial de acerto", f"{percent_official:.1f}%")
            st.metric("🏁 Pontuação final (com bônus)", st.session_state.final_points)
            st.metric("🏆 Maior streak", st.session_state.max_streak)

            if not st.session_state.saved_score:
                append_score(
                    st.session_state.student_name,
                    st.session_state.base_correct,
                    st.session_state.final_points,
                    total,
                    st.session_state.max_streak
                )
                st.session_state.saved_score = True

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔁 Refazer"):
                    reset_all()
                    st.rerun()
            with col2:
                if st.button("👤 Trocar aluno"):
                    st.session_state.student_name = ""
                    reset_all()
                    st.rerun()

        else:
            # questão atual
            qpos = st.session_state.q_order[st.session_state.q_index]
            q = QUESTIONS[qpos]

            st.progress(st.session_state.q_index / total)
            difficulty_bar(q["level"])

            st.markdown(f"### {q['id']} — {q['prompt']}")
            if q.get("code"):
                st.code(q["code"], language="java")

            disabled = st.session_state.show_feedback

            # NOVO: embaralhar opções por questão para reduzir padrão A/B
            options = shuffle_options_keep_answer(q["options"], q["answer"])

            # mostra como A/B/C/D visualmente
            letters = ["A", "B", "C", "D"]
            labeled = [f"{letters[i]}) {opt}" for i, opt in enumerate(options)]
            label_to_value = {labeled[i]: options[i] for i in range(len(options))}

            choice_label = st.radio("Escolha a alternativa:", labeled, index=0, disabled=disabled)
            choice = label_to_value[choice_label]

            if not st.session_state.show_feedback:
                if st.button("✅ Confirmar"):
                    correct = (choice == q["answer"])

                    if correct:
                        # acerto oficial
                        st.session_state.base_correct += 1

                        # streak e bônus
                        st.session_state.streak += 1
                        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.streak)

                        bonus = streak_bonus_points(st.session_state.streak)

                        # pontuação final: 1 ponto pelo acerto + bônus
                        st.session_state.final_points += 1 + bonus
                        st.session_state.last_bonus = bonus
                    else:
                        st.session_state.streak = 0
                        st.session_state.last_bonus = 0

                    st.session_state.last_correct = correct
                    st.session_state.last_explain = q["explain"]
                    st.session_state.last_answer = q["answer"]
                    st.session_state.show_feedback = True
                    st.rerun()

            # feedback
            if st.session_state.show_feedback:
                if st.session_state.last_correct:
                    if st.session_state.last_bonus > 0:
                        st.success(f"✅ Correto! 🔥 Bônus de sequência: +{st.session_state.last_bonus}")
                    else:
                        st.success("✅ Correto!")
                else:
                    st.error(f"❌ Incorreto. Resposta certa: **{st.session_state.last_answer}**")

                st.info("📌 Justificativa (didática):")
                st.write(st.session_state.last_explain)

                if st.button("➡️ Próximo"):
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.session_state.last_correct = None
                    st.session_state.last_explain = None
                    st.session_state.last_answer = None
                    st.session_state.last_bonus = 0
                    st.rerun()


# ==========================================================
# VIEW: ADMIN
# ==========================================================
else:
    st.subheader("🔐 Área do administrador")
    st.caption("Login para ver ranking com medalhas, top/bottom 10, e limpar respostas.")

    if not st.session_state.admin_authed:
        user = st.text_input("Usuário")
        pwd = st.text_input("Senha", type="password")

        if st.button("🔓 Entrar"):
            if user == ADMIN_USER and pwd == ADMIN_PASS:
                st.session_state.admin_authed = True
                st.rerun()
            else:
                st.error("Usuário ou senha inválidos.")

        st.info("Configure em `.streamlit/secrets.toml` (recomendado).")
    else:
        st.success("✅ Admin autenticado.")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🚪 Sair (logout)"):
                st.session_state.admin_authed = False
                st.session_state.confirm_clear = False
                st.rerun()

        with col2:
            if st.button("🗑️ Limpar todas as respostas"):
                st.session_state.confirm_clear = True

        if st.session_state.confirm_clear:
            st.warning("⚠️ Tem certeza que deseja apagar TODAS as respostas? Essa ação é irreversível.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Confirmar exclusão"):
                    clear_scores()
                    st.session_state.confirm_clear = False
                    st.success("✔️ Todas as respostas foram apagadas.")
                    st.rerun()
            with c2:
                if st.button("❌ Cancelar"):
                    st.session_state.confirm_clear = False
                    st.rerun()

        rows = load_scores()
        if not rows:
            st.info("Ainda não há pontuações registradas.")
        else:
            # Melhor tentativa por aluno:
            # 1) % oficial (acertos/total)
            # 2) pontuação final
            # 3) max streak
            # 4) mais recente
            best_by_student = {}
            for r in rows:
                name = (r.get("student_name") or "").strip()
                if not name:
                    continue

                key = (
                    r["percent_official"],
                    r["final_points"],
                    r.get("max_streak", 0),
                    r["timestamp_utc"]
                )
                if name not in best_by_student:
                    best_by_student[name] = r
                else:
                    cur = best_by_student[name]
                    cur_key = (
                        cur["percent_official"],
                        cur["final_points"],
                        cur.get("max_streak", 0),
                        cur["timestamp_utc"]
                    )
                    if key > cur_key:
                        best_by_student[name] = r

            best_list = list(best_by_student.values())
            best_sorted = sorted(
                best_list,
                key=lambda x: (x["percent_official"], x["final_points"], x.get("max_streak", 0), x["timestamp_utc"]),
                reverse=True
            )

            st.markdown("## 🏆 Ranking (Top 10) — com medalhas")
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            ranking_table = []
            for i, r in enumerate(best_sorted[:10], start=1):
                ranking_table.append({
                    "Posição": f"{medals.get(i, '🏅')} {i}",
                    "Aluno": r["student_name"],
                    "✅ Acertos": f"{r['base_correct']}/{r['total']}",
                    "📈 % oficial": f"{r['percent_official']:.1f}%",
                    "🏁 Pontos finais": r["final_points"],
                    "🔥 Max streak": r.get("max_streak", 0),
                    "Última (UTC)": r["timestamp_utc"],
                })

            st.dataframe(ranking_table, use_container_width=True, hide_index=True)

            bottom10 = sorted(
                best_list,
                key=lambda x: (x["percent_official"], x["final_points"], x.get("max_streak", 0), x["timestamp_utc"])
            )[:10]

            st.markdown("### 🧯 Bottom 10 (piores alunos)")
            bottom_table = []
            for i, r in enumerate(bottom10, start=1):
                bottom_table.append({
                    "Posição": i,
                    "Aluno": r["student_name"],
                    "✅ Acertos": f"{r['base_correct']}/{r['total']}",
                    "📈 % oficial": f"{r['percent_official']:.1f}%",
                    "🏁 Pontos finais": r["final_points"],
                    "🔥 Max streak": r.get("max_streak", 0),
                    "Última (UTC)": r["timestamp_utc"],
                })
            st.dataframe(bottom_table, use_container_width=True, hide_index=True)

            st.markdown("### 🕒 Últimos 25 registros (raw)")
            last = sorted(rows, key=lambda x: x["timestamp_utc"], reverse=True)[:25]
            st.dataframe(last, use_container_width=True, hide_index=True)

            st.caption(f"Armazenamento local: `{SCORES_FILE.as_posix()}`")
