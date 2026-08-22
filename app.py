# -*- coding: utf-8 -*-
"""
شات بوت أراضي بيت الوطن - المرحلة الحادية عشر
============================================
كل البيانات في هذا الملف مأخوذة حرفيًا من "كراسة شروط طرح الأراضي للمصريين
بالخارج - المرحلة الحادية عشر (يونيو 2026)" الصادرة عن هيئة المجتمعات
العمرانية الجديدة - وزارة الإسكان المصرية:
https://lands.nuca.gov.eg/Files/Handbook.pdf

⚠️ ملاحظات مهمة قبل الاستخدام أو النشر:
- هذا المشروع غير رسمي وغير تابع لهيئة المجتمعات العمرانية أو وزارة الإسكان.
- بيانات القطع الفردية (رقم كل قطعة ومساحتها الدقيقة) غير متوفرة هنا حتى
  الآن لأنها غير قابلة للتأكد منها آليًا بثقة كافية من المصادر المتاحة.
  القسم المخصص لها (VERIFIED_PLOTS) فارغ عمدًا، ويُفترض ملؤه فقط ببيانات
  تم التأكد منها يدويًا من الكراسة الرسمية أو موقع الهيئة.
- راجع دائمًا الكراسة الرسمية ورقم الهيئة قبل اتخاذ أي قرار مالي.
"""

import streamlit as st
import re

st.set_page_config(
    page_title="مساعد بيت الوطن 11 (غير رسمي)",
    page_icon="🏡",
    layout="wide",
)

# ============================================================
# 1) بيانات المدن/المناطق - جدول الأسعار الرسمي (29 منطقة طرح)
#    المصدر: صفحة 11 من الكراسة الرسمية
# ============================================================
ZONES = [
    {"city": "القاهرة الجديدة", "sector": "الحي الرابع - الامتداد الشرقي",
     "price_egp": 25800, "price_usd": 490, "build_pct": 50, "floors": "بدروم + أرضي + 3 أدوار"},
    {"city": "6 أكتوبر", "sector": "الحزام الأخضر - حوض 21-22",
     "price_egp": 9475, "price_usd": 180, "build_pct": 40, "floors": "أرضي + دورين"},
    {"city": "الشيخ زايد", "sector": "توسعات المدينة - القرار 77",
     "price_egp": 21280, "price_usd": 405, "build_pct": 50, "floors": "أرضي + دورين"},
    {"city": "الشيخ زايد", "sector": "الحي 13 - المجاورة 6",
     "price_egp": 23620, "price_usd": 450, "build_pct": 40, "floors": "أرضي + أول"},
    {"city": "الشيخ زايد", "sector": "الحي 11 - المجاورة 2",
     "price_egp": 25005, "price_usd": 475, "build_pct": 50, "floors": "أرضي + دورين"},
    {"city": "العاشر من رمضان", "sector": "منطقة المال والأعمال - عمارات (CA-CB)",
     "price_egp": 12830, "price_usd": 245, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "العاشر من رمضان", "sector": "منطقة المال والأعمال - فيلات (CC-CD)",
     "price_egp": 9625, "price_usd": 185, "build_pct": 40, "floors": "أرضي + أول"},
    {"city": "دمياط الجديدة", "sector": "بيت الوطن بالساحل",
     "price_egp": 25705, "price_usd": 490, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "دمياط الجديدة", "sector": "بيت الوطن غرب المدينة",
     "price_egp": 25705, "price_usd": 490, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "المنصورة الجديدة", "sector": "المرحلة الثانية - المنطقة السادسة B",
     "price_egp": 11355, "price_usd": 215, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "15 مايو", "sector": "المركز الفرعي 3",
     "price_egp": 17330, "price_usd": 330, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "بدر", "sector": "الامتداد الشرقي - منطقة 8",
     "price_egp": 8650, "price_usd": 165, "build_pct": 50, "floors": "أرضي + 5 أدوار"},
    {"city": "بدر", "sector": "الحي المتميز 2",
     "price_egp": 10050, "price_usd": 195, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "العبور", "sector": "الحي الرابع - بلوك 19073",
     "price_egp": 12280, "price_usd": 235, "build_pct": 50, "floors": "أرضي + دورين"},
    {"city": "الشروق", "sector": "منطقة جنيفة (زهرة الشروق) - موقع 3",
     "price_egp": 29110, "price_usd": 555, "build_pct": 50, "floors": "أرضي + 6 أدوار"},
    {"city": "السادات", "sector": "المحور المركزي الثاني (B-C-D-E)",
     "price_egp": 10190, "price_usd": 195, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "العلمين الجديدة", "sector": "منطقة C - بالقرب من الأكاديمية",
     "price_egp": 13020, "price_usd": 250, "build_pct": 50, "floors": "أرضي + 5 أدوار"},
    {"city": "سفنكس الجديدة", "sector": "شمال السليمانية - منطقة 145 فدان",
     "price_egp": 8135, "price_usd": 155, "build_pct": 50, "floors": "أرضي + دورين"},
    {"city": "العبور الجديدة", "sector": "الحي الرابع والعشرون (24)",
     "price_egp": 9850, "price_usd": 190, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "أكتوبر الجديدة", "sector": "منطقة الأب تاون - مجاورة 9 - منطقة 2",
     "price_egp": 6940, "price_usd": 135, "build_pct": 45, "floors": "أرضي + دورين"},
    {"city": "أكتوبر الجديدة", "sector": "جنوب طريق الواحات",
     "price_egp": 7725, "price_usd": 150, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "برج العرب الجديدة", "sector": "جنوب الحي الرابع",
     "price_egp": 8420, "price_usd": 160, "build_pct": 50, "floors": "أرضي + 5 أدوار"},
    {"city": "برج العرب الجديدة", "sector": "المحور المركزي (منطقة A)",
     "price_egp": 9150, "price_usd": 175, "build_pct": 50, "floors": "أرضي + 5 أدوار"},
    {"city": "المنيا الجديدة", "sector": "منطقة 310 فدان السياحية 3",
     "price_egp": 15045, "price_usd": 285, "build_pct": 50, "floors": "أرضي + 4 أدوار"},
    {"city": "أسوان الجديدة", "sector": "جنوب الحي السياحي - منطقة 350 - منطقة 2",
     "price_egp": 5705, "price_usd": 110, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "سوهاج الجديدة", "sector": "التوسعات الجنوبية - الحي الثامن - منطقة C-B",
     "price_egp": 8060, "price_usd": 155, "build_pct": 50, "floors": "أرضي + 5 أدوار"},
    {"city": "الفيوم الجديدة", "sector": "الامتداد الجنوبي - منطقة A",
     "price_egp": 5070, "price_usd": 100, "build_pct": 50, "floors": "أرضي + دورين"},
    {"city": "أسيوط الجديدة", "sector": "التوسعات الشمالية الغربية - الحي الخامس - المجاورة الرابعة",
     "price_egp": 4545, "price_usd": 90, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
    {"city": "أخميم الجديدة", "sector": "وحدة الجوار العمراني السادسة عشر",
     "price_egp": 3245, "price_usd": 65, "build_pct": 50, "floors": "أرضي + 3 أدوار"},
]

CITY_NAMES = sorted(set(z["city"] for z in ZONES))

# ============================================================
# 2) بيانات القطع الفردية الموثقة - فارغة عمدًا
#    أضف هنا فقط أرقام قطع تم التأكد منها يدويًا من مصدر رسمي.
#    مثال (بعد التأكد فقط):
#    {"city": "القاهرة الجديدة", "number": 2, "area": 1433.60,
#     "verified_source": "اسم المصدر وتاريخ التحقق"}
# ============================================================
VERIFIED_PLOTS = []

# ============================================================
# 3) نسب التميز الرسمية (صفحة 4 من الكراسة)
# ============================================================
DISTINCTION_RULES = [
    ("قطعة ناصية (تطل على طريقين، أو طريق وممر جانبي، أو طريق وممر خلفي)", 5),
    ("قطعة مطلة على حدائق ومناطق مفتوحة", 5),
    ("قطعة مطلة مباشرة على النيل أو البحر", 15),
]

# ============================================================
# 4) خياري السداد الرسميين (صفحة 9 من الكراسة) - بديل واحد بس
#    ملحوظة: لا يوجد أي خصم نقدي "7.5%" في الكراسة الرسمية.
# ============================================================
PAYMENT_OPTIONS = {
    "الأول": {
        "desc": "تحديد ثمن الأرض بالجنيه المصري، سداد 25% مقدم بالدولار، "
                "والباقي على 3 أقساط سنوية متساوية محملة بفائدة البنك المركزي "
                "المصري + 0.5% مصاريف إدارية.",
        "down_pct": 25, "years": 3, "rate_note": "فائدة متغيرة (سعر البنك المركزي المصري وقت الاستحقاق) + 0.5% إداري",
    },
    "الثاني": {
        "desc": "تثبيت ثمن الأرض بالدولار الأمريكي، سداد 25% مقدم بالدولار، "
                "والباقي على 7 أقساط سنوية متساوية بفائدة ثابتة 4.75% + 0.5% مصاريف إدارية.",
        "down_pct": 25, "years": 7, "rate_note": "فائدة ثابتة 4.75% + 0.5% إداري",
    },
}

# ============================================================
# 5) بيانات التحويل البنكي الرسمية (صفحة 10 من الكراسة)
# ============================================================
BANK_INFO_ABROAD = {
    "correspondent_bank": "City Bank, New York",
    "correspondent_swift": "CITIUS33XXX",
    "correspondent_account": "36001304",
    "beneficiary_bank": "البنك المركزي المصري - القاهرة",
    "beneficiary_swift": "CBEGEGCXXXX",
    "beneficiary_account": "4082192000",
    "iban": "EG020001000100000004082192000",
    "beneficiary_name": "New Urban Communities Authority - Egyptians Abroad",
}
CONTACT_EMAIL = "bayt_waten11@mhud.gov.eg"

TOTAL_PLOTS_OFFICIAL = 3600
TOTAL_CITIES_OFFICIAL = 22  # عدد المدن؛ بعض المدن فيها أكثر من منطقة طرح واحدة

SOURCE_NOTE = (
    "المصدر: كراسة شروط طرح الأراضي للمصريين بالخارج - المرحلة الحادية عشر "
    "(يونيو 2026) - هيئة المجتمعات العمرانية الجديدة."
)

# ============================================================
# واجهة المستخدم
# ============================================================
st.markdown("""
    <style>
    .header-box {
        background-color: #0f2438; padding: 22px; border-radius: 10px;
        color: white; text-align: center; border-bottom: 5px solid #c5a059;
        margin-bottom: 20px;
    }
    .disclaimer {
        background-color: #fff8e6; border-right: 4px solid #c5a059;
        padding: 12px 16px; border-radius: 6px; font-size: 0.92rem; color: #5c4a1f;
        margin-bottom: 20px;
    }
    .chat-bubble-bot {
        background-color: #f0f4f8; padding: 12px 16px; border-radius: 12px 12px 12px 2px;
        margin-bottom: 10px; border-left: 4px solid #0f2438; color: #222;
    }
    .chat-bubble-user {
        background-color: #e2f0d9; padding: 12px 16px; border-radius: 12px 12px 2px 12px;
        margin-bottom: 10px; border-right: 4px solid #548235; text-align: right; color: #222;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header-box">
        <h1 style="margin:0;">🏡 مساعد أراضي بيت الوطن - المرحلة الحادية عشر</h1>
        <p style="color:#c5a059; margin:8px 0 0 0;">مشروع غير رسمي - بيانات مستخرجة من الكراسة الرسمية للهيئة</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(f"""
    <div class="disclaimer">
    ⚠️ <b>هذا المشروع غير رسمي وغير تابع لهيئة المجتمعات العمرانية الجديدة أو وزارة الإسكان.</b><br>
    البيانات هنا منقولة من الكراسة الرسمية المنشورة على موقع الهيئة، لكن الأسعار والشروط قابلة للتغيير.
    راجع دائمًا <a href="https://lands.nuca.gov.eg/Files/Handbook.pdf" target="_blank">الكراسة الرسمية</a>
    والقنوات الرسمية للهيئة قبل اتخاذ أي قرار مالي أو تحويل أي مبلغ.<br>
    بيانات أرقام القطع الفردية الدقيقة <b>غير متوفرة بعد</b> في هذا الإصدار.
    </div>
""", unsafe_allow_html=True)

tab = st.sidebar.radio(
    "اختر القسم:",
    ["💬 الشات بوت", "📊 حاسبة السداد", "🏙️ جدول المدن والأسعار"],
)
st.sidebar.markdown("---")
st.sidebar.caption(SOURCE_NOTE)
st.sidebar.caption(f"📧 البريد الرسمي للمشروع: {CONTACT_EMAIL}")

# ---------------- مساعدة: توليد رد نصي عن مدينة ----------------
def city_reply(city_name):
    zones = [z for z in ZONES if z["city"] == city_name]
    if not zones:
        return None
    lines = [f"🏙️ <b>{city_name}</b> — {len(zones)} منطقة طرح ضمن المرحلة الحادية عشر:<br>"]
    for z in zones:
        lines.append(
            f"📍 <b>{z['sector']}</b><br>"
            f"&nbsp;&nbsp;💰 السعر: {z['price_usd']}$ للمتر (يعادل {z['price_egp']:,} ج.م)<br>"
            f"&nbsp;&nbsp;🏗️ النسبة البنائية: {z['build_pct']}% | الارتفاع: {z['floors']}<br>"
        )
    lines.append(f"<br><i>{SOURCE_NOTE}</i>")
    return "<br>".join(lines)


def plot_reply(plot_num, city_hint=None):
    matches = [p for p in VERIFIED_PLOTS if p["number"] == plot_num
               and (city_hint is None or p["city"] == city_hint)]
    if matches:
        p = matches[0]
        return (f"🔍 القطعة رقم {plot_num} في {p['city']}: المساحة {p['area']} م² "
                f"(موثقة من: {p.get('verified_source', 'غير محدد')}).")
    return (f"للأسف بيانات القطعة رقم {plot_num} الدقيقة (المساحة الفعلية) "
            f"مش متاحة في قاعدة البيانات دي حتى الآن — القطع الفردية لسه محتاجة "
            f"تأكيد يدوي من الكراسة الرسمية أو موقع الهيئة قبل ما تتضاف.<br>"
            f"أقدر أقولك بس سعر المتر والاشتراطات العامة للمنطقة اللي القطعة فيها، "
            f"لو قلتلي اسم المدينة.")


# ---------------- التاب 1: الشات بوت ----------------
if tab == "💬 الشات بوت":
    st.subheader("💬 اسأل عن أراضي بيت الوطن - المرحلة الحادية عشر")
    st.caption("مثال: أسعار القاهرة الجديدة | قطعة رقم 15 في الشيخ زايد | إزاي أحسب التميز | بيانات التحويل البنكي")

    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content":
             "أهلاً بيك! اسألني عن أي مدينة من مدن الطرح، أو نسب التميز، أو طرق السداد، "
             "أو بيانات التحويل البنكي الرسمية. (بيانات القطع الفردية الدقيقة لسه مش متاحة)."}
        ]

    for msg in st.session_state.messages:
        cls = "chat-bubble-bot" if msg["role"] == "assistant" else "chat-bubble-user"
        st.markdown(f'<div class="{cls}">{msg["content"]}</div>', unsafe_allow_html=True)

    user_input = st.text_input("اكتب سؤالك هنا:", key="user_question")

    if st.button("إرسال") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        q = user_input.strip()
        ql = q.lower()
        response = None

        # سؤال عن قطعة برقم
        plot_match = re.search(r'\b(\d{1,4})\b', q)
        if any(k in q for k in ["قطعة", "رقم"]) and plot_match:
            city_hint = next((c for c in CITY_NAMES if c in q), None)
            response = plot_reply(int(plot_match.group(1)), city_hint)

        # سؤال عن مدينة
        if response is None:
            city_hit = next((c for c in CITY_NAMES if c in q), None)
            if city_hit:
                response = city_reply(city_hit)

        # سؤال عن التميز
        if response is None and any(k in q for k in ["تميز", "تمييز"]):
            response = "📐 <b>نسب التميز الرسمية:</b><br>" + "<br>".join(
                f"• {desc}: <b>{pct}%</b> إضافية على سعر المتر" for desc, pct in DISTINCTION_RULES
            ) + ("<br><br><i>يتم مراجعة وتدقيق نسب التميز على الطبيعة لكل قطعة قبل "
                 "التخصيص والتعاقد من جانب جهاز المدينة المختص.</i>")

        # سؤال عن السداد/التقسيط
        if response is None and any(k in q for k in ["سداد", "تقسيط", "دفع", "بديل"]):
            response = "💵 <b>بديلا السداد الرسميين:</b><br><br>"
            for name, opt in PAYMENT_OPTIONS.items():
                response += f"🔹 <b>البديل {name}:</b> {opt['desc']}<br><br>"

        # سؤال عن التحويل البنكي
        if response is None and any(k in q for k in ["بنك", "تحويل", "iban", "swift", "حوالة"]):
            b = BANK_INFO_ABROAD
            response = (
                "🏦 <b>بيانات التحويل البنكي الرسمية (من الخارج):</b><br>"
                f"• البنك المراسل: {b['correspondent_bank']} | SWIFT: {b['correspondent_swift']} | حساب: {b['correspondent_account']}<br>"
                f"• البنك المستفيد: {b['beneficiary_bank']} | SWIFT: {b['beneficiary_swift']}<br>"
                f"• رقم الحساب: {b['beneficiary_account']}<br>"
                f"• IBAN: {b['iban']}<br>"
                f"• اسم المستفيد: {b['beneficiary_name']}<br><br>"
                "⚠️ <b>تحقق دائمًا من هذه الأرقام على "
                "<a href='https://lands.nuca.gov.eg/Files/Handbook.pdf' target='_blank'>الكراسة الرسمية</a> "
                "مباشرة قبل أي تحويل — أي خطأ في رقم الحساب يعني تحويل فلوسك لجهة غلط.</b>"
            )

        # افتراضي
        if response is None:
            response = (
                "تقدر تسألني عن:<br>"
                "1️⃣ أسعار واشتراطات أي مدينة (مثال: \"أسعار الشروق\")<br>"
                "2️⃣ نسب التميز للقطع<br>"
                "3️⃣ طرق وبدائل السداد<br>"
                "4️⃣ بيانات التحويل البنكي الرسمية<br><br>"
                f"إجمالي الطرح: {TOTAL_PLOTS_OFFICIAL:,} قطعة في {TOTAL_CITIES_OFFICIAL} مدينة جديدة."
            )

        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# ---------------- التاب 2: حاسبة السداد ----------------
elif tab == "📊 حاسبة السداد":
    st.subheader("📊 حاسبة تقديرية لثمن القطعة وخطة السداد")
    st.caption(SOURCE_NOTE + " — الأرقام تقديرية وليست ملزمة.")

    col1, col2 = st.columns(2)
    with col1:
        city_sel = st.selectbox("المدينة:", CITY_NAMES)
        zones_here = [z for z in ZONES if z["city"] == city_sel]
        sector_sel = st.selectbox("المنطقة:", [z["sector"] for z in zones_here])
        zone = next(z for z in zones_here if z["sector"] == sector_sel)
        area = st.number_input("مساحة القطعة (م²):", min_value=100.0, max_value=5000.0, value=500.0, step=10.0)
        dist_label = st.selectbox(
            "نوع التميز:",
            ["بدون تميز"] + [f"{d} (+{p}%)" for d, p in DISTINCTION_RULES]
        )
        dist_pct = 0
        for d, p in DISTINCTION_RULES:
            if dist_label.startswith(d):
                dist_pct = p

    price_per_m = zone["price_usd"] * (1 + dist_pct / 100)
    total_usd = area * price_per_m

    with col2:
        st.markdown(f"""
        **📍 {city_sel} - {sector_sel}**
        - سعر المتر الأساسي: {zone['price_usd']}$ ({zone['price_egp']:,} ج.م)
        - سعر المتر شامل التميز: **{price_per_m:,.2f}$**
        - **إجمالي ثمن الأرض التقديري: {total_usd:,.2f}$**
        """)

    st.markdown("---")
    st.subheader("💡 خطط السداد الرسمية")
    t1, t2 = st.tabs(["🔵 البديل الأول (تقسيط 3 سنين بالجنيه)", "🟢 البديل الثاني (تقسيط 7 سنين ثابت 4.75%)"])

    with t1:
        opt = PAYMENT_OPTIONS["الأول"]
        down = total_usd * opt["down_pct"] / 100
        remaining = total_usd - down
        st.markdown(f"""
        {opt['desc']}

        - مقدم الحجز (25%): **{down:,.2f}$**
        - المتبقي للتقسيط على {opt['years']} سنوات: **{remaining:,.2f}$**
        - قسط سنوي (قبل الفائدة): **{remaining/opt['years']:,.2f}$**
        - ⚠️ {opt['rate_note']} — القيمة الفعلية للقسط تتحدد وقت الاستحقاق.
        """)

    with t2:
        opt = PAYMENT_OPTIONS["الثاني"]
        down = total_usd * opt["down_pct"] / 100
        remaining = total_usd - down
        annual = remaining / opt["years"]
        st.markdown(f"""
        {opt['desc']}

        - مقدم الحجز (25%): **{down:,.2f}$**
        - المتبقي للتقسيط على {opt['years']} سنوات: **{remaining:,.2f}$**
        - قسط سنوي أساسي (قبل الفائدة): **{annual:,.2f}$**
        - ⚠️ {opt['rate_note']}
        """)

# ---------------- التاب 3: جدول المدن ----------------
elif tab == "🏙️ جدول المدن والأسعار":
    st.subheader(f"🏙️ جدول أسعار المرحلة الحادية عشر ({len(ZONES)} منطقة طرح)")
    st.caption(SOURCE_NOTE)

    import pandas as pd
    df = pd.DataFrame(ZONES)
    df = df.rename(columns={
        "city": "المدينة", "sector": "المنطقة", "price_egp": "السعر (ج.م)",
        "price_usd": "السعر ($)", "build_pct": "نسبة البناء %", "floors": "الأدوار المسموحة"
    })
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown(f"**إجمالي الطرح المُعلَن رسميًا:** {TOTAL_PLOTS_OFFICIAL:,} قطعة في {TOTAL_CITIES_OFFICIAL} مدينة جديدة.")
