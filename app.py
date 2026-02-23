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
st.caption("Quiz com bônus por sequência de acertos 🔥")


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

CSV_HEADERS = ["timestamp_utc", "student_name", "score", "total", "percent", "max_streak"]


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
                row["score"] = int(row["score"])
                row["total"] = int(row["total"])
                row["percent"] = float(row["percent"])
                row["max_streak"] = int(row.get("max_streak", 0))
                rows.append(row)
            except Exception:
                pass
    return rows


def append_score(student_name: str, score: int, total: int, max_streak: int):
    ensure_scores_file()
    percent = (score / total) * 100 if total else 0.0
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(SCORES_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ts, student_name, score, total, f"{percent:.2f}", max_streak])


def clear_scores():
    if SCORES_FILE.exists():
        SCORES_FILE.unlink()
    ensure_scores_file()


# =========================
# UI HELPERS
# =========================
def difficulty_bar(level: str):
    # Barra visual (0-100)
    mapping = {"Fácil": 30, "Médio": 60, "Difícil": 90}
    colors = {"Fácil": "🟩", "Médio": "🟨", "Difícil": "🟥"}
    value = mapping.get(level, 50)
    st.markdown(f"**Dificuldade:** {colors.get(level,'🟨')} {level}")
    st.progress(value / 100)


def streak_bonus_points(streak: int) -> int:
    # bônus progressivo: só começa a pontuar no 2º acerto seguido
    # streak=1 -> +0, streak=2 -> +1, streak=3 -> +2, ...
    return max(0, streak - 1)


# =========================
# QUESTÕES (30) — variedade
# =========================
# Cada questão:
# {
#   id, level ("Fácil"/"Médio"/"Difícil"), prompt, code(optional),
#   options, answer, explain
# }
QUESTIONS = [
    # --- Fácil (conceito e básicos) ---
    {
        "id": "Q01", "level": "Fácil",
        "prompt": "Qual das declarações abaixo é válida em Java?",
        "options": ['boolean ok = true;', 'boolean ok = "true";', 'boolean ok = 1;', "boolean ok = True;"],
        "answer": 'boolean ok = true;',
        "explain": "boolean recebe apenas true/false (sem aspas).",
    },
    {
        "id": "Q02", "level": "Fácil",
        "prompt": "Qual expressão resulta em um boolean (true/false)?",
        "options": ["10 + 5", "idade >= 18", "nota * 2", '"18"'],
        "answer": "idade >= 18",
        "explain": "Comparações produzem boolean.",
    },
    {
        "id": "Q03", "level": "Fácil",
        "prompt": "Qual operador representa o 'E' lógico em Java?",
        "options": ["&&", "||", "!", "=="],
        "answer": "&&",
        "explain": "&& é AND (E lógico).",
    },
    {
        "id": "Q04", "level": "Fácil",
        "prompt": "Qual operador representa o 'OU' lógico em Java?",
        "options": ["&&", "||", "!=", "<="],
        "answer": "||",
        "explain": "|| é OR (OU lógico).",
    },
    {
        "id": "Q05", "level": "Fácil",
        "prompt": "Qual operador representa o 'NÃO' lógico em Java?",
        "options": ["!", "&&", "||", "=="],
        "answer": "!",
        "explain": "! inverte o boolean.",
    },
    {
        "id": "Q06", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int a = 5, b = 7;\nSystem.out.println(a > b);",
        "options": ["true", "false", "5", "7"],
        "answer": "false",
        "explain": "5 não é maior que 7.",
    },
    {
        "id": "Q07", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int a = 5;\nSystem.out.println(a == 5);",
        "options": ["true", "false", "5", "erro"],
        "answer": "true",
        "explain": "a é igual a 5.",
    },
    {
        "id": "Q08", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "boolean matriculado = false;\nSystem.out.println(!matriculado);",
        "options": ["true", "false", "erro", "!false"],
        "answer": "true",
        "explain": "!false = true.",
    },
    {
        "id": "Q09", "level": "Fácil",
        "prompt": "Qual alternativa descreve melhor um boolean?",
        "options": ["Um texto com letras", "Um número inteiro", "Um tipo que representa verdadeiro/falso", "Um tipo para decimais"],
        "answer": "Um tipo que representa verdadeiro/falso",
        "explain": "boolean representa true/false.",
    },
    {
        "id": "Q10", "level": "Fácil",
        "prompt": "O que este código imprime?",
        "code": "int nota = 6;\nSystem.out.println(nota >= 6);",
        "options": ["true", "false", "6", "erro"],
        "answer": "true",
        "explain": "6 >= 6 é true.",
    },

    # --- Médio (AND/OR, dupla negação, parênteses) ---
    {
        "id": "Q11", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "int idade = 16;\nboolean temRG = true;\nSystem.out.println(idade >= 18 && temRG);",
        "options": ["true", "false", "16", "erro"],
        "answer": "false",
        "explain": "false && true = false.",
    },
    {
        "id": "Q12", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "int idade = 16;\nboolean temRG = true;\nSystem.out.println(idade >= 18 || temRG);",
        "options": ["true", "false", "erro", "16"],
        "answer": "true",
        "explain": "false || true = true.",
    },
    {
        "id": "Q13", "level": "Médio",
        "prompt": "O que este código imprime?",
        "code": "boolean matriculado = false;\nSystem.out.println(!!matriculado);",
        "options": ["true", "false", "erro", "!!false"],
        "answer": "false",
        "explain": "Dupla negação retorna o valor original.",
    },
    {
        "id": "Q14", "level": "Médio",
        "prompt": "Traduza: “Entra se tem ingresso E não está banido”.",
        "options": ["temIngresso && !banido", "temIngresso || !banido", "!temIngresso && banido", "temIngresso && banido"],
        "answer": "temIngresso && !banido",
        "explain": "Precisa ter ingresso e NÃO estar banido.",
    },
    {
        "id": "Q15", "level": "Médio",
        "prompt": "Traduza: “Pode fazer substitutiva se faltou OU teve atestado”.",
        "options": ["faltou && temAtestado", "faltou || temAtestado", "!faltou || temAtestado", "faltou && !temAtestado"],
        "answer": "faltou || temAtestado",
        "explain": "OU: basta uma condição.",
    },
    {
        "id": "Q16", "level": "Médio",
        "prompt": "Traduza: “Desconto se é aluno E (pagou em dia OU tem bolsa)”.",
        "options": ["ehAluno && pagouEmDia || temBolsa", "ehAluno && (pagouEmDia || temBolsa)", "(ehAluno && pagouEmDia) || temBolsa", "ehAluno || (pagouEmDia && temBolsa)"],
        "answer": "ehAluno && (pagouEmDia || temBolsa)",
        "explain": "Parênteses garantem o agrupamento correto.",
    },
    {
        "id": "Q17", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "int idade = 18;\nboolean autorizacao = false;\nSystem.out.println(idade >= 18 && autorizacao);",
        "options": ["true", "false", "erro", "18"],
        "answer": "false",
        "explain": "true && false = false.",
    },
    {
        "id": "Q18", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = false;\nSystem.out.println(!(a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "a && b = false; !false = true.",
    },
    {
        "id": "Q19", "level": "Médio",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = false;\nSystem.out.println(a && (b || true));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "(b || true) = true; a && true = true.",
    },
    {
        "id": "Q20", "level": "Médio",
        "prompt": "Qual condição é equivalente a “NÃO (A OU B)”?",
        "options": ["!A || !B", "!A && !B", "A && B", "!(A && B)"],
        "answer": "!A && !B",
        "explain": "Lei de De Morgan: !(A || B) == (!A && !B).",
    },

    # --- Difícil (precedência e armadilhas comuns) ---
    {
        "id": "Q21", "level": "Difícil",
        "prompt": "Precedência: o que imprime?",
        "code": "boolean x = true;\nboolean y = false;\nSystem.out.println(x || y && false);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "&& vem antes: y && false = false; x || false = true.",
    },
    {
        "id": "Q22", "level": "Difícil",
        "prompt": "Precedência: o que imprime?",
        "code": "boolean x = false;\nboolean y = true;\nSystem.out.println(x || y && false);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "false",
        "explain": "&& antes: y && false = false; x || false = false.",
    },
    {
        "id": "Q23", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "int a = 2;\nint b = 3;\nSystem.out.println(!(a > b) && (b > 0));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "a>b é false; !false=true; b>0 é true; true && true = true.",
    },
    {
        "id": "Q24", "level": "Difícil",
        "prompt": "Qual expressão é equivalente a “A OU (B E C)”?",
        "options": ["(A || B) && C", "A || (B && C)", "(A && B) || C", "A && (B || C)"],
        "answer": "A || (B && C)",
        "explain": "Cuidado com agrupamento: é OR com um AND dentro.",
    },
    {
        "id": "Q25", "level": "Difícil",
        "prompt": "Qual condição corrige a intenção: “loginOk se usuario e senha não estão vazios” (sem usar texto livre)?",
        "options": [
            'usuario != "" && senha != ""',
            'usuario == "" && senha == ""',
            'usuario != "" || senha != ""',
            '!usuario && !senha'
        ],
        "answer": 'usuario != "" && senha != ""',
        "explain": "Didático: ambos não vazios usando &&. (Em Java real, preferir .isEmpty())",
    },
    {
        "id": "Q26", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean a = false;\nboolean b = false;\nSystem.out.println(!(a || b) || (a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "a||b=false; !(false)=true; (a&&b)=false; true||false=true.",
    },
    {
        "id": "Q27", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean a = true;\nboolean b = true;\nSystem.out.println(!(a && b) || (a && b));",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "É uma tautologia: X ou não-X (aqui reescrita) -> sempre true.",
    },
    {
        "id": "Q28", "level": "Difícil",
        "prompt": "Qual é o resultado de: true && false || true ?",
        "options": ["true", "false", "erro", "depende"],
        "answer": "true",
        "explain": "&& antes: true&&false=false; false||true=true.",
    },
    {
        "id": "Q29", "level": "Difícil",
        "prompt": "Qual expressão é equivalente a “(A E B) OU (A E C)”?",
        "options": ["A && (B || C)", "(A || B) && C", "(A && B) || C", "A || (B && C)"],
        "answer": "A && (B || C)",
        "explain": "Fatoração: A&&(B||C).",
    },
    {
        "id": "Q30", "level": "Difícil",
        "prompt": "O que imprime?",
        "code": "boolean A = false;\nboolean B = true;\nboolean C = true;\nSystem.out.println(A || B && !C);",
        "options": ["true", "false", "erro", "depende"],
        "answer": "false",
        "explain": "!C=false; B && false = false; A || false = false.",
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
    st.session_state.score = 0
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
if "q_index" not in st.session_state:
    reset_quiz_progress()


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
    st.caption("Digite seu nome para iniciar o quiz de boolean (com bônus por sequência).")

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
        st.success(f"Aluno: **{st.session_state.student_name}**")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Pontuação", f"{st.session_state.score} / {total}")
        with c2:
            st.metric("🔥 Streak", st.session_state.streak)
        with c3:
            st.metric("🏆 Max streak", st.session_state.max_streak)

        st.metric("Questão", f"{st.session_state.q_index + 1} / {total}")

        # fim
        if st.session_state.q_index >= total:
            st.success("🎉 Quiz finalizado!")
            percent = (st.session_state.score / total) * 100
            st.metric("Desempenho (%)", f"{percent:.1f}%")

            if not st.session_state.saved_score:
                append_score(st.session_state.student_name, st.session_state.score, total, st.session_state.max_streak)
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

            choice = st.radio("Escolha a alternativa:", q["options"], index=0, disabled=disabled)

            if not st.session_state.show_feedback:
                if st.button("✅ Confirmar"):
                    correct = (choice == q["answer"])

                    # streak + bônus
                    if correct:
                        st.session_state.streak += 1
                        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.streak)
                        bonus = streak_bonus_points(st.session_state.streak)
                        st.session_state.score += 1 + bonus
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

                st.info(f"📌 Explicação: {st.session_state.last_explain}")

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
            # Melhor tentativa por aluno: maior percent; empate: maior score; empate: maior max_streak; empate: mais recente
            best_by_student = {}
            for r in rows:
                name = (r.get("student_name") or "").strip()
                if not name:
                    continue

                key = (r["percent"], r["score"], r.get("max_streak", 0), r["timestamp_utc"])
                if name not in best_by_student:
                    best_by_student[name] = r
                else:
                    cur = best_by_student[name]
                    cur_key = (cur["percent"], cur["score"], cur.get("max_streak", 0), cur["timestamp_utc"])
                    if key > cur_key:
                        best_by_student[name] = r

            best_list = list(best_by_student.values())
            best_sorted = sorted(
                best_list,
                key=lambda x: (x["percent"], x["score"], x.get("max_streak", 0), x["timestamp_utc"]),
                reverse=True
            )

            st.markdown("## 🏆 Ranking (Top 10) — com medalhas")
            medals = {1: "🥇", 2: "🥈", 3: "🥉"}

            ranking_table = []
            for i, r in enumerate(best_sorted[:10], start=1):
                ranking_table.append({
                    "Posição": f"{medals.get(i, '🏅')} {i}",
                    "Aluno": r["student_name"],
                    "Pontos": f"{r['score']}/{r['total']}",
                    "%": f"{r['percent']:.1f}%",
                    "🔥 Max streak": r.get("max_streak", 0),
                    "Última (UTC)": r["timestamp_utc"],
                })

            st.dataframe(ranking_table, use_container_width=True, hide_index=True)

            bottom10 = sorted(
                best_list,
                key=lambda x: (x["percent"], x["score"], x.get("max_streak", 0), x["timestamp_utc"])
            )[:10]

            st.markdown("### 🧯 Bottom 10 (piores alunos)")
            bottom_table = []
            for i, r in enumerate(bottom10, start=1):
                bottom_table.append({
                    "Posição": i,
                    "Aluno": r["student_name"],
                    "Pontos": f"{r['score']}/{r['total']}",
                    "%": f"{r['percent']:.1f}%",
                    "🔥 Max streak": r.get("max_streak", 0),
                    "Última (UTC)": r["timestamp_utc"],
                })
            st.dataframe(bottom_table, use_container_width=True, hide_index=True)

            st.markdown("### 🕒 Últimos 25 registros (raw)")
            last = sorted(rows, key=lambda x: x["timestamp_utc"], reverse=True)[:25]
            st.dataframe(last, use_container_width=True, hide_index=True)

            st.caption(f"Armazenamento local: `{SCORES_FILE.as_posix()}`")
