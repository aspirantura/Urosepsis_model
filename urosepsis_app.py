"""
Калькулятор прогнозирования гестационного уросепсиса
=====================================================
Модель бинарной логистической регрессии для оценки вероятности
перехода острого гестационного пиелонефрита в уросепсис.

Диссертация: «Особенности беременности и родов при гестационном уросепсисе»
Специальность: 3.1.4. Акушерство и гинекология
"""

import streamlit as st
import math

# ============================================================
# КОНФИГУРАЦИЯ СТРАНИЦЫ
# ============================================================
st.set_page_config(
    page_title="Прогноз гестационного уросепсиса",
    page_icon="🏥",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ============================================================
# ФУНКЦИЯ РАСЧЁТА
# ============================================================
def calc_urosepsis_risk(temp: float, crp: float, leukocytosis: int, ht: float) -> dict:
    """
    Расчёт вероятности гестационного уросепсиса по модели логистической регрессии.

    Параметры
    ---------
    temp : float
        Температура тела при поступлении, °C
    crp : float
        С-реактивный белок при поступлении, мг/л
    leukocytosis : int
        Лейкоцитоз > 10×10⁹/л (0 = нет, 1 = да)
    ht : float
        Гематокрит, %

    Возвращает
    ----------
    dict с ключами: z, probability, risk_category, color, recommendation
    """
    z = (
        -15.928
        + 0.550 * temp
        + 0.017 * crp
        + 0.995 * leukocytosis
        - 0.202 * ht
    )

    probability = 1 / (1 + math.exp(-z)) * 100  # в процентах

    threshold = 57.2  # оптимальный порог по индексу Юдена

    if probability >= threshold:
        risk_category = "⚠ ВЫСОКИЙ РИСК"
        color = "#FF4B4B"
        recommendation = (
            "Пациентка относится к группе **высокого риска** развития "
            "гестационного уросепсиса. Рекомендована немедленная госпитализация, "
            "консультация уролога, посев крови, мониторинг витальных функций, "
            "раннее назначение антибактериальной терапии."
        )
    else:
        risk_category = "✓ НИЗКИЙ РИСК"
        color = "#00C851"
        recommendation = (
            "Риск генерализации инфекции **низкий**. Рекомендован стандартный "
            "протокол ведения острого гестационного пиелонефрита, контроль "
            "лабораторных показателей в динамике."
        )

    return {
        "z": round(z, 3),
        "probability": round(probability, 1),
        "threshold": threshold,
        "risk_category": risk_category,
        "color": color,
        "recommendation": recommendation,
    }


# ============================================================
# ИНТЕРФЕЙС
# ============================================================
st.title("Прогноз гестационного уросепсиса")

st.markdown(
    """
    **Модель оценки риска перехода острого гестационного пиелонефрита в уросепсис**
    на основании лабораторных и клинических параметров при поступлении в стационар.
    """
)

st.divider()

# ---------- ВВОД ДАННЫХ ----------
st.subheader("Параметры пациентки при поступлении")

col1, col2 = st.columns(2)

with col1:
    temp = st.number_input(
        "Температура тела, °C",
        min_value=35.0,
        max_value=42.0,
        value=36.6,
        step=0.1,
        format="%.1f",
        help="Температура тела при поступлении по поводу о. пиелонефрита / уросепсиса",
    )

    crp = st.number_input(
        "С-реактивный белок (СРБ), мг/л",
        min_value=0.0,
        max_value=500.0,
        value=10.0,
        step=1.0,
        format="%.1f",
        help="СРБ при поступлении (пиелонефрит / уросепсис)",
    )

with col2:
    leukocytosis = st.selectbox(
        "Лейкоцитоз > 10×10⁹/л",
        options=[("Нет", 0), ("Да", 1)],
        format_func=lambda x: x[0],
        index=0,
        help="Наличие лейкоцитоза при поступлении",
    )
    leukocytosis_val = leukocytosis[1]

    ht = st.number_input(
        "Гематокрит, %",
        min_value=15.0,
        max_value=55.0,
        value=34.0,
        step=0.1,
        format="%.1f",
        help="Гематокрит (норма 35–47%)",
    )

st.divider()

# ---------- КНОПКА РАСЧЁТА ----------
if st.button("🔍 Рассчитать риск уросепсиса", type="primary", use_container_width=True):
    result = calc_urosepsis_risk(temp, crp, leukocytosis_val, ht)

    # ---------- РЕЗУЛЬТАТЫ ----------
    st.divider()
    st.subheader("Результат расчёта")

    # Метрика риска
    col_risk, col_prob = st.columns(2)

    with col_risk:
        st.metric(
            label="Категория риска",
            value=result["risk_category"],
        )

    with col_prob:
        st.metric(
            label="Вероятность уросепсиса",
            value=f"{result['probability']}%",
            delta=f"Порог: {result['threshold']}%",
        )

    # Визуальная шкала
    prob_val = result["probability"]
    st.markdown(
        f"""
        <div style="
            background: #f0f0f0;
            border-radius: 12px;
            height: 36px;
            position: relative;
            margin: 16px 0;
        ">
            <div style="
                background: linear-gradient(90deg, #00C851, #FFD700, #FF4B4B);
                border-radius: 12px;
                height: 100%;
                width: {min(prob_val, 100)}%;
                position: relative;
            "></div>
            <div style="
                position: absolute;
                left: {result['threshold']}%;
                top: -4px;
                width: 3px;
                height: 44px;
                background: #333;
                border-radius: 2px;
            "></div>
        </div>
        <div style="display: flex; justify-content: space-between; font-size: 0.8rem; color: #666;">
            <span>0%</span>
            <span style="color: #333; font-weight: bold;">Порог {result['threshold']}%</span>
            <span>100%</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
