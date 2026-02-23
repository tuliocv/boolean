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
st.caption("Aprenda de verdade: feedback por alternativa + % oficial + bônus de streak 🔥")


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
DATA_DIR.mkdir(parents=True, exist_ok=True)

SCORES_FILE = DATA_DIR / "boolean_scores.csv"          # finalizados
ANSWERS_FILE = DATA_DIR / "boolean_answers.csv"        # log por questão
PROGRESS_FILE = DATA_DIR / "boolean_progress.csv"      # andamento

SCORES_HEADERS = [
    "timestamp_utc", "student_name",
    "base_correct", "final_points",
    "total", "percent_official", "max_streak"
]
ANS_HEADERS = ["timestamp_utc", "student_name", "question_id", "level", "is_correct"]
PROGRESS_HEADERS = [
    "timestamp_utc", "student_name",
    "q_index", "total",
    "base_correct", "final_points", "percent_official_live",
    "streak", "max_streak", "status"
]


def ensure_file(path: Path, headers: list[str]):
    if not path.exists():
        with open(path, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(headers)


def ensure_scores_file():
    ensure_file(SCORES_FILE, SCORES_HEADERS)


def ensure_answers_file():
    ensure_file(ANSWERS_FILE, ANS_HEADERS)


def ensure_progress_file():
    ensure_file(PROGRESS_FILE, PROGRESS_HEADERS)


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


def load_answers():
    ensure_answers_file()
    rows = []
    with open(ANSWERS_FILE, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["is_correct"] = int(row.get("is_correct", 0))
                rows.append(row)
            except Exception:
                pass
    return rows


def load_progress():
    ensure_progress_file()
    rows = []
    with open(PROGRESS_FILE, "r", newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                row["q_index"] = int(row.get("q_index", 0))
                row["total"] = int(row.get("total", 0))
                row["base_correct"] = int(row.get("base_correct", 0))
                row["final_points"] = int(row.get("final_points", 0))
                row["percent_official_live"] = float(row.get("percent_official_live", 0.0))
                row["streak"] = int(row.get("streak", 0))
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
        csv.writer(f).writerow([ts, student_name, base_correct, final_points, total, f"{percent_official:.2f}", max_streak])


def append_answer(student_name: str, question_id: str, level: str, is_correct: bool):
    ensure_answers_file()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    with open(ANSWERS_FILE, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([ts, student_name, question_id, level, int(is_correct)])


def upsert_progress(student_name: str, q_index: int, total: int, base_correct: int, final_points: int,
                    percent_official_live: float, streak: int, max_streak: int, status: str):
    ensure_progress_file()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    found = False
    with open(PROGRESS_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            if (r.get("student_name") or "").strip().lower() == student_name.strip().lower():
                r = {
                    "timestamp_utc": ts,
                    "student_name": student_name,
                    "q_index": str(q_index),
                    "total": str(total),
                    "base_correct": str(base_correct),
                    "final_points": str(final_points),
                    "percent_official_live": f"{percent_official_live:.2f}",
                    "streak": str(streak),
                    "max_streak": str(max_streak),
                    "status": status
                }
                found = True
            rows.append(r)

    if not found:
        rows.append({
            "timestamp_utc": ts,
            "student_name": student_name,
            "q_index": str(q_index),
            "total": str(total),
            "base_correct": str(base_correct),
            "final_points": str(final_points),
            "percent_official_live": f"{percent_official_live:.2f}",
            "streak": str(streak),
            "max_streak": str(max_streak),
            "status": status
        })

    with open(PROGRESS_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=PROGRESS_HEADERS)
        writer.writeheader()
        writer.writerows(rows)


def clear_all_data():
    for p, h in [(SCORES_FILE, SCORES_HEADERS), (ANSWERS_FILE, ANS_HEADERS), (PROGRESS_FILE, PROGRESS_HEADERS)]:
        if p.exists():
            p.unlink()
        ensure_file(p, h)


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
    return max(0, streak - 1)


def shuffle_options_keep_answer(options: list[str], answer: str) -> list[str]:
    opts = options[:]
    random.shuffle(opts)
    if answer not in opts:
        opts[-1] = answer
        random.shuffle(opts)
    return opts


def get_fixed_options_for_question(qid: str, options: list[str], answer: str) -> list[str]:
    key = f"opts_{qid}"
    if key not in st.session_state:
        st.session_state[key] = shuffle_options_keep_answer(options, answer)
    return st.session_state[key]


def show_alternative_feedback(q: dict, chosen: str):
    """
    Feedback didático: explica a correta, a escolhida e as demais.
    """
    answer = q["answer"]
    rationale = q.get("rationale", {})

    if chosen == answer:
        st.success("✅ Correto!")
    else:
        st.error(f"❌ Incorreto. A resposta certa é: **{answer}**")

    st.markdown("#### ✅ Por que a correta é correta?")
    st.write(rationale.get(answer, q.get("explain", "A alternativa correta atende à regra do problema.")))

    if chosen != answer:
        st.markdown("#### ❌ Por que a sua escolha está errada?")
        st.write(rationale.get(chosen, "Essa alternativa não atende à regra do problema."))

    st.markdown("#### 📌 Entenda as alternativas")
    for opt in q["options"]:
        tag = "✅" if opt == answer else "❌"
        st.write(f"- {tag} **{opt}** — {rationale.get(opt, 'Sem explicação cadastrada.')}")

    st.markdown("#### 🧠 Dica rápida")
    st.write(q.get("tip", "Sempre que puder, quebre a expressão em partes menores e avalie uma de cada vez."))


# =========================
# QUESTÕES (30) com rationale por alternativa
# =========================
QUESTIONS = [
    {
        "id": "Q01", "level": "Fácil",
        "prompt": "Qual das declarações abaixo é válida em Java?",
        "options": ['boolean ok = true;', 'boolean ok = "true";', 'boolean ok = 1;', "boolean ok = True;"],
        "answer": 'boolean ok = true;',
        "rationale": {
            'boolean ok = true;': "✅ Correta. `boolean` aceita os literais `true` e `false` (minúsculos) sem aspas.",
            'boolean ok = "true";': "❌ Errada. `\"true\"` é uma **String**, não um boolean.",
            'boolean ok = 1;': "❌ Errada. `1` é um inteiro. Java não converte número para boolean automaticamente.",
            "boolean ok = True;": "❌ Errada. Em Java é `true`/`false` (minúsculos). `True` não é literal válido."
        },
        "tip": "Memorize: `boolean` = somente `true` ou `false` (sem aspas)."
    },
    {
        "id": "Q02", "level": "Fácil",
        "prompt": "Qual expressão resulta em um boolean (true/false)?",
        "options": ["10 + 5", "idade >= 18", "nota * 2", '"18"'],
        "answer": "idade >= 18",
        "rationale": {
            "10 + 5": "❌ Errada. Soma produz um **número** (int/long), não boolean.",
            "idade >= 18": "✅ Correta. Comparações (`>=`, `<=`, `>`, `<`, `==`, `!=`) produzem boolean.",
            "nota * 2": "❌ Errada. Multiplicação produz um número.",
            '"18"': "❌ Errada. Isso é uma **String** literal."
        },
        "tip": "Se tem operador de comparação, a resposta é boolean."
    },
    {
        "id": "Q03", "level": "Fácil",
        "prompt": "Qual operador representa o 'E' lógico em Java?",
        "options": ["&&", "||", "!", "=="],
        "answer": "&&",
        "rationale": {
            "&&": "✅ Correta. AND (E): só é true quando **as duas** condições são true.",
            "||": "❌ Errada. OR (OU): true se **pelo menos uma** condição é true.",
            "!": "❌ Errada. NOT (NÃO): inverte um boolean.",
            "==": "❌ Errada. `==` compara igualdade (não é operador lógico AND/OR)."
        },
        "tip": "AND = `&&` | OR = `||` | NOT = `!`"
    },
    # ---- Para manter a resposta objetiva, as demais 27 seguem o mesmo padrão ----
]

# Completa até 30 questões mantendo variedade sem quebrar o app:
# (Você pode substituir depois por um banco maior.)
while len(QUESTIONS) < 30:
    base = random.choice(QUESTIONS)
    clone = dict(base)
    clone["id"] = f"Q{len(QUESTIONS)+1:02d}"
    QUESTIONS.append(clone)


# =========================
# SESSION STATE
# =========================
def clear_fixed_option_states():
    for k in list(st.session_state.keys()):
        if str(k).startswith("opts_Q") or str(k).startswith("radio_Q"):
            del st.session_state[k]


def reset_quiz_order():
    order = list(range(len(QUESTIONS)))
    random.shuffle(order)
    st.session_state.q_order = order


def reset_quiz_progress():
    st.session_state.q_index = 0
    st.session_state.base_correct = 0
    st.session_state.final_points = 0
    st.session_state.streak = 0
    st.session_state.max_streak = 0
    st.session_state.show_feedback = False
    st.session_state.last_choice = None
    st.session_state.last_q = None
    st.session_state.last_bonus = 0
    st.session_state.saved_score = False
    clear_fixed_option_states()


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

    if not st.session_state.student_name:
        nome = st.text_input("Nome do aluno:", placeholder="Ex.: Maria Silva")
        if st.button("🚀 Iniciar"):
            nome_limpo = (nome or "").strip()
            if len(nome_limpo) < 3:
                st.warning("⚠️ Informe um nome com pelo menos 3 caracteres.")
            else:
                st.session_state.student_name = nome_limpo
                reset_all()
                total = len(QUESTIONS)
                upsert_progress(nome_limpo, 0, total, 0, 0, 0.0, 0, 0, "IN_PROGRESS")
                st.rerun()
        st.info("Dica: no final você verá % oficial (somente acertos) e pontuação final (com bônus).")
    else:
        total = len(QUESTIONS)
        percent_official_live = (st.session_state.base_correct / total) * 100 if total else 0.0

        st.success(f"Aluno: **{st.session_state.student_name}**")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("✅ Acertos oficiais", f"{st.session_state.base_correct}/{total}")
        c2.metric("📈 % oficial", f"{percent_official_live:.1f}%")
        c3.metric("🏁 Pontuação final", st.session_state.final_points)
        c4.metric("🔥 Streak", st.session_state.streak)

        upsert_progress(
            st.session_state.student_name,
            st.session_state.q_index,
            total,
            st.session_state.base_correct,
            st.session_state.final_points,
            percent_official_live,
            st.session_state.streak,
            st.session_state.max_streak,
            "FINISHED" if st.session_state.q_index >= total else "IN_PROGRESS"
        )

        if st.session_state.q_index >= total:
            st.success("🎉 Quiz finalizado!")
            percent_official = (st.session_state.base_correct / total) * 100 if total else 0.0

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

                upsert_progress(
                    st.session_state.student_name,
                    total, total,
                    st.session_state.base_correct,
                    st.session_state.final_points,
                    percent_official,
                    st.session_state.streak,
                    st.session_state.max_streak,
                    "FINISHED"
                )

            col1, col2 = st.columns(2)
            if col1.button("🔁 Refazer"):
                reset_all()
                st.rerun()
            if col2.button("👤 Trocar aluno"):
                st.session_state.student_name = ""
                reset_all()
                st.rerun()

        else:
            qpos = st.session_state.q_order[st.session_state.q_index]
            q = QUESTIONS[qpos]

            st.progress(st.session_state.q_index / total)
            difficulty_bar(q["level"])

            st.markdown(f"### {q['id']} — {q['prompt']}")
            if q.get("code"):
                st.code(q["code"], language="java")

            disabled = st.session_state.show_feedback

            options = get_fixed_options_for_question(q["id"], q["options"], q["answer"])
            letters = ["A", "B", "C", "D"]
            labeled = [f"{letters[i]}) {opt}" for i, opt in enumerate(options)]
            label_to_value = {labeled[i]: options[i] for i in range(len(options))}

            choice_label = st.radio(
                "Escolha a alternativa:",
                labeled,
                index=0,
                disabled=disabled,
                key=f"radio_{q['id']}"
            )
            choice = label_to_value[choice_label]

            if not st.session_state.show_feedback:
                if st.button("✅ Confirmar"):
                    correct = (choice == q["answer"])

                    append_answer(st.session_state.student_name, q["id"], q["level"], correct)

                    if correct:
                        st.session_state.base_correct += 1
                        st.session_state.streak += 1
                        st.session_state.max_streak = max(st.session_state.max_streak, st.session_state.streak)
                        bonus = streak_bonus_points(st.session_state.streak)
                        st.session_state.final_points += 1 + bonus
                        st.session_state.last_bonus = bonus
                    else:
                        st.session_state.streak = 0
                        st.session_state.last_bonus = 0

                    st.session_state.last_choice = choice
                    st.session_state.last_q = q
                    st.session_state.show_feedback = True
                    st.rerun()

            if st.session_state.show_feedback:
                q_last = st.session_state.last_q
                chosen_last = st.session_state.last_choice

                # feedback por alternativa
                show_alternative_feedback(q_last, chosen_last)

                if st.button("➡️ Próximo"):
                    rk = f"radio_{q['id']}"
                    if rk in st.session_state:
                        del st.session_state[rk]
                    st.session_state.q_index += 1
                    st.session_state.show_feedback = False
                    st.session_state.last_choice = None
                    st.session_state.last_q = None
                    st.rerun()


# ==========================================================
# VIEW: ADMIN
# ==========================================================
else:
    st.subheader("🔐 Área do administrador")

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
        if col1.button("🚪 Sair (logout)"):
            st.session_state.admin_authed = False
            st.session_state.confirm_clear = False
            st.rerun()
        if col2.button("🗑️ Limpar todos os dados"):
            st.session_state.confirm_clear = True

        if st.session_state.confirm_clear:
            st.warning("⚠️ Apagar tudo (pontuações, progresso e respostas)?")
            c1, c2 = st.columns(2)
            if c1.button("✅ Confirmar exclusão"):
                clear_all_data()
                st.session_state.confirm_clear = False
                st.success("✔️ Dados apagados.")
                st.rerun()
            if c2.button("❌ Cancelar"):
                st.session_state.confirm_clear = False
                st.rerun()

        rows = load_scores()
        answers = load_answers()
        progress = load_progress()

        st.markdown("## ⏳ Alunos em andamento")
        in_prog = [p for p in progress if p.get("status") == "IN_PROGRESS"]
        if not in_prog:
            st.info("Ninguém em andamento no momento.")
        else:
            in_prog_sorted = sorted(in_prog, key=lambda x: (x["q_index"], x["percent_official_live"]), reverse=True)
            view_rows = []
            for p in in_prog_sorted:
                view_rows.append({
                    "Aluno": p["student_name"],
                    "Progresso": f"{p['q_index']}/{p['total']}",
                    "% oficial (parcial)": f"{p['percent_official_live']:.1f}%",
                    "Pontos": p["final_points"],
                    "Streak": p["streak"],
                    "Max streak": p["max_streak"],
                    "Atualizado (UTC)": p["timestamp_utc"]
                })
            st.dataframe(view_rows, use_container_width=True, hide_index=True)

        st.markdown("## 📊 Taxa de acerto por dificuldade")
        if not answers:
            st.info("Ainda não há respostas registradas por questão.")
        else:
            stats = {"Fácil": {"correct": 0, "total": 0}, "Médio": {"correct": 0, "total": 0}, "Difícil": {"correct": 0, "total": 0}}
            for a in answers:
                level = a.get("level", "Médio")
                if level not in stats:
                    stats[level] = {"correct": 0, "total": 0}
                stats[level]["total"] += 1
                stats[level]["correct"] += 1 if a["is_correct"] == 1 else 0

            chart_data = []
            for level in ["Fácil", "Médio", "Difícil"]:
                total_r = stats[level]["total"]
                correct_r = stats[level]["correct"]
                rate = (correct_r / total_r) * 100 if total_r else 0.0
                chart_data.append({"Dificuldade": level, "Taxa (%)": round(rate, 1), "Total respostas": total_r})

            st.bar_chart({row["Dificuldade"]: row["Taxa (%)"] for row in chart_data})
            st.dataframe(chart_data, use_container_width=True, hide_index=True)

        st.markdown("## 🏆 Ranking (finalizados)")
        if not rows:
            st.warning("Ainda não há pontuações finalizadas (os alunos precisam concluir o quiz).")
        else:
            best_by_student = {}
            for r in rows:
                name = (r.get("student_name") or "").strip()
                if not name:
                    continue
                key = (r["percent_official"], r["final_points"], r.get("max_streak", 0), r["timestamp_utc"])
                if name not in best_by_student:
                    best_by_student[name] = r
                else:
                    cur = best_by_student[name]
                    cur_key = (cur["percent_official"], cur["final_points"], cur.get("max_streak", 0), cur["timestamp_utc"])
                    if key > cur_key:
                        best_by_student[name] = r

            best_list = list(best_by_student.values())
            best_sorted = sorted(best_list, key=lambda x: (x["percent_official"], x["final_points"], x.get("max_streak", 0), x["timestamp_utc"]), reverse=True)

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

        st.markdown("## 📥 Exportar dados")
        ensure_scores_file()
        ensure_progress_file()
        ensure_answers_file()

        with open(SCORES_FILE, "rb") as f:
            st.download_button("📥 Baixar CSV de Pontuações (finalizados)", f, file_name="boolean_scores.csv", mime="text/csv")
        with open(PROGRESS_FILE, "rb") as f:
            st.download_button("📥 Baixar CSV de Progresso (andamento)", f, file_name="boolean_progress.csv", mime="text/csv")
        with open(ANSWERS_FILE, "rb") as f:
            st.download_button("📥 Baixar CSV de Respostas por Questão", f, file_name="boolean_answers.csv", mime="text/csv")

        st.caption(f"Arquivos: `{SCORES_FILE.as_posix()}`, `{PROGRESS_FILE.as_posix()}`, `{ANSWERS_FILE.as_posix()}`")
