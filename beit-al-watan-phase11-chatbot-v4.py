import streamlit as st
import pandas as pd
import json
import re
import os

# 1. Custom CSS for Real Estate Theming (Dark Gold, Navy, and Cream)
st.set_page_config(
    page_title="Kemet للاستشارات العقارية - بيت الوطن المرحله 11",
    page_icon="🏢",
    layout="wide",
)

st.markdown("""
    <style>
    .main {
        background-color: #fbfbfb;
    }
    div[data-testid="stSidebar"] {
        background-color: #0f1c30;
        color: white;
    }
    div[data-testid="stSidebar"] * {
        color: white;
    }
    .stButton>button {
        background-color: #c5a059;
        color: white;
        border-radius: 6px;
        border: none;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0f1c30;
        color: #c5a059;
    }
    .header-box {
        background-color: #0f1c30;
        padding: 25px;
        border-radius: 10px;
        color: white;
        text-align: center;
        border-bottom: 5px solid #c5a059;
        margin-bottom: 25px;
    }
    .city-card {
        background-color: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 5px solid #c5a059;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .plot-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        border-top: 4px solid #c5a059;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 15px;
    }
    .chat-bubble-bot {
        background-color: #f0f4f8;
        padding: 15px 18px;
        border-radius: 12px 12px 12px 2px;
        margin-bottom: 10px;
        border-left: 4px solid #0f1c30;
        color: #333333;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .chat-bubble-user {
        background-color: #e2f0d9;
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin-bottom: 10px;
        border-right: 4px solid #548235;
        text-align: right;
        color: #333333;
    }
    .excel-status-box {
        background-color: #e8f5e9;
        border: 1px solid #2e7d32;
        padding: 10px;
        border-radius: 6px;
        color: #2e7d32;
        margin-bottom: 15px;
        font-weight: bold;
    }
    .excel-fallback-box {
        background-color: #fff3e0;
        border: 1px solid #ef6c00;
        padding: 10px;
        border-radius: 6px;
        color: #e65100;
        margin-bottom: 15px;
        font-size: 0.9rem;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Database Definition (Cities and Plots Grounded in Sources)
CITIES_DB = {
    "القاهرة الجديدة": {
        "sector": "الحي الرابع - الامتداد الشرقي",
        "price_usd": 490,
        "price_egp": 25800,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 351,
        "recommendation": "الأكثر طلباً والأعلى قيمة في إعادة البيع. ينصح بالبديل الثاني للاستفادة من تثبيت سعر الصرف بالجنيه المصري.",
        "distinguished": [67, 68, 69, 120, 149]
    },
    "الشروق": {
        "sector": "جنوب منطقة جنيفة (زهرة الشروق) - موقع 3",
        "price_usd": 555,
        "price_egp": 29110,
        "build_pct": 50,
        "height": "بدروم + أرضي + 6 أدوار متكررة (استثنائي)",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 74,
        "recommendation": "ممتازة جداً للمطورين العقاريين لارتفاع الأدوار المسموح بها (أرضي و6 أدوار) مما يضاعف عدد الشقق السكنية القابلة للبيع.",
        "distinguished": [1, 2, 19]
    },
    "الشيخ زايد": {
        "sector": "توسعات المدينة القرار 77 والحي 11 والحي 13",
        "price_usd": 405, 
        "price_egp": 21280,
        "build_pct": 50,
        "height": "بدروم + أرضي + دورين متكررين",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 29,
        "recommendation": "طرح نادر جداً (29 قطعة فقط) مما يمنحها ميزة ندرة هائلة. الحي 11 يبلغ سعر المتر فيه 475$ والحي 13 يبلغ 450$.",
        "distinguished": [28, 89]
    },
    "دمياط الجديدة": {
        "sector": "بيت الوطن بالساحل / غرب المدينة",
        "price_usd": 490,
        "price_egp": 25705,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 6م | جانبي: 3م",
        "total_plots": 21,
        "recommendation": "قطع الساحل (الصف الأول للبحر) توفر فرصاً نادرة جداً للفيلات المصيفية الفاخرة ذات العائد الإيجاري المرتفع.",
        "distinguished": [31, 42, 84, 85]
    },
    "6 أكتوبر": {
        "sector": "منطقة الحزام الأخضر - حوض 21-22",
        "price_usd": 180,
        "price_egp": 9475,
        "build_pct": 40,
        "height": "بدروم + أرضي + دورين متكررين",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 3م",
        "total_plots": 236,
        "recommendation": "مثالي لمحبي الهدوء والمساحات الخضراء المفتوحة، بنسبة بناء 40% فقط وفيلات راقية.",
        "distinguished": [1, 2, 29, 63, 121]
    },
    "العاشر من رمضان": {
        "sector": "منطقة المال والأعمال (عمارات CA-CB وفيلا CC-CD)",
        "price_usd": 245, 
        "price_egp": 12830,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار (عمارات) / أرضي وأول (فيلات)",
        "setbacks": "عمارات (3م-5م-3م) | فيلات (4م-6م-3م)",
        "total_plots": 282,
        "recommendation": "سعر متر منافس جداً للفيلات (185$ للمتر). فرصة استثمارية واعدة للتطوير العقاري الصناعي والإسكاني الفاخر.",
        "distinguished": [1, 2, 3]
    },
    "المنصورة الجديدة": {
        "sector": "المرحلة الثانية - المنطقة السادسة B",
        "price_usd": 215,
        "price_egp": 11355,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 3م",
        "total_plots": 92,
        "recommendation": "تطل مباشرة على البحر الأبيض المتوسط، وتعتبر عاصمة الدلتا المستقبلية ومركزاً واعداً للاستثمار الساحلي السكني.",
        "distinguished": [1, 2, 3]
    },
    "15 مايو": {
        "sector": "المركز الفرعي 3",
        "price_usd": 330,
        "price_egp": 17330,
        "build_pct": 50,
        "height": "بدروم + أرضي + 4 أدوار متكررة",
        "setbacks": "أمامي: 4م | خلفي: 4م | جانبي: 3م",
        "total_plots": 3,
        "recommendation": "طرح محدود للغاية بمركز المدينة الفرعي 3، بمساحات كبيرة، مثالي للاستخدام السكني العائلي الخاص.",
        "distinguished": [41, 42, 43]
    },
    "بدر": {
        "sector": "الامتداد الشرقي منطقة 8 / الحي المتميز 2",
        "price_usd": 165, 
        "price_egp": 8650,
        "build_pct": 50,
        "height": "بدروم + أرضي + 5 أدوار (امتداد) / 3 أدوار (متميز)",
        "setbacks": "أمامي: 3م | خلفي: 4.5م | جانبي: 3م",
        "total_plots": 115,
        "recommendation": "منفذ ممتاز بأسعار منخفضة جداً قريبة من العاصمة الإدارية الجديدة، بمستقبل نمو رأسمالي مرتفع للغاية.",
        "distinguished": [141, 142, 143]
    },
    "العبور": {
        "sector": "الحي الرابع - بلوك 19073",
        "price_usd": 235,
        "price_egp": 12280,
        "build_pct": 50,
        "height": "بدروم + أرضي + دورين متكررين",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 2.5م",
        "total_plots": 10,
        "recommendation": "القطع بمساحة موحدة تقريبية (600 متر)، في بلوك متميز وهادئ بالحي الرابع.",
        "distinguished": [13, 19]
    },
    "السادات": {
        "sector": "المحور المركزي الثاني (مناطق B, C, D, E)",
        "price_usd": 195,
        "price_egp": 10190,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 468,
        "recommendation": "طرح ضخم يوفر خيارات واسعة ومساحات متنوعة تبدأ من 445م وتصل لـ 1260م في موقع حيوي بقلب السادات.",
        "distinguished": [1, 2]
    },
    "العلمين الجديدة": {
        "sector": "المنطقة C بالقرب من الأكاديمية البحرية",
        "price_usd": 250,
        "price_egp": 13020,
        "build_pct": 50,
        "height": "بدروم + أرضي + 5 أدوار متكررة",
        "setbacks": "أمامي: 4م | خلفي: 4م | جانبي: 3م",
        "total_plots": 268,
        "recommendation": "أقوى مدينة ساحلية صاعدة في مصر، تتيح بناء حتى 5 أدوار متكررة مما يوفر جدوى اقتصادية هائلة للبناء والشقق السكنية.",
        "distinguished": [1, 2, 3]
    },
    "سفنكس الجديدة": {
        "sector": "منطقة 145 فدان شمال السليمانية",
        "price_usd": 155,
        "price_egp": 8135,
        "build_pct": 50,
        "height": "بدروم + أرضي + دورين متكررين",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 462,
        "recommendation": "تقع مباشرة أمام مطار سفنكس الدولي وتحيط بها أفخم الكومباوندات الفاخرة، ومستقبلها واعد للغاية كمنطقة فيلات هادئة.",
        "distinguished": [1, 2]
    },
    "العبور الجديدة": {
        "sector": "الحي 24 على طريق R2",
        "price_usd": 190,
        "price_egp": 9850,
        "build_pct": 50,
        "height": "بدروم + أرضي + 5 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 495,
        "recommendation": "طرح كبير جداً ومستقبل ممتاز بالتزامن مع إزالة التعديات والبدء الفوري في مد الطرق والمرافق الرئيسية بالحي 24.",
        "distinguished": [12, 13, 14, 15]
    },
    "أكتوبر الجديدة": {
        "sector": "الأب تاون مجاورة 9 / جنوب طريق الواحات",
        "price_usd": 135, 
        "price_egp": 6940,
        "build_pct": 45,
        "height": "بدروم + أرضي + دورين (أب تاون) / 3 أدوار (الواحات)",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 3م",
        "total_plots": 772,
        "recommendation": "الخيار الاقتصادي الأقوى للتملك العقاري بغرب الجيزة بمساحات ذكية وأسعار ممتازة تبدأ من 135$ للمتر.",
        "distinguished": [1, 2, 33, 34]
    },
    "برج العرب الجديدة": {
        "sector": "جنوب الحي الرابع / المحور المركزي منطقة A",
        "price_usd": 160, 
        "price_egp": 8420,
        "build_pct": 50,
        "height": "بدروم + أرضي + 5 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 3م | جانبي: 3م",
        "total_plots": 183,
        "recommendation": "مستقبل سكني مميز قبالة الساحل الشمالي، يتيح بناء 5 أدوار متكررة بالكامل.",
        "distinguished": [1, 2, 3]
    },
    "المنيا الجديدة": {
        "sector": "310 فدان السياحية الثالثة بلوك D",
        "price_usd": 285,
        "price_egp": 15045,
        "build_pct": 50,
        "height": "بدروم + أرضي + 4 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 34,
        "recommendation": "تقع فوق هضبة مطلة ومتميزة شرق النيل بقلب المنيا الجديدة وترتبط بكوبري مباشر مع المدينة القديمة.",
        "distinguished": [1, 2, 3, 8]
    },
    "أسوان الجديدة": {
        "sector": "350 فدان جنوب الحي السياحي منطقة 2",
        "price_usd": 110,
        "price_egp": 5705,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 3م",
        "total_plots": 84,
        "recommendation": "طرح سياحي فاخر بأسوان الجديدة على الضفة الغربية لنهر النيل وبقرب شديد من الممشى السياحي.",
        "distinguished": [1, 2, 6, 12]
    },
    "سوهاج الجديدة": {
        "sector": "التوسعات الجنوبية للحي الثامن منطقتي B, C",
        "price_usd": 155,
        "price_egp": 8060,
        "build_pct": 50,
        "height": "بدروم + أرضي + 5 أدوار متكررة",
        "setbacks": "أمامي: 3م | خلفي: 5م | جانبي: 3م",
        "total_plots": 212,
        "recommendation": "توسعات واعدة جداً للحي الثامن وتتميز بالقرب من مطار سوهاج الدولي وبنية تحتية متطورة.",
        "distinguished": [1, 2, 46, 67, 82]
    },
    "الفيوم الجديدة": {
        "sector": "الامتداد الجنوبي منطقة A",
        "price_usd": 100,
        "price_egp": 5070,
        "build_pct": 50,
        "height": "بدروم + أرضي + دورين متكررين",
        "setbacks": "أمامي: 3م | خلفي: 4م | جانبي: 3م",
        "total_plots": 63,
        "recommendation": "طرح اقتصادي هادئ ومميز بالامتداد الجنوبي للمدينة بمساحات تبدأ من 416م مربع.",
        "distinguished": [1, 2, 6, 7]
    },
    "أسيوط الجديدة": {
        "sector": "التوسعات الشمالية الغربية للحي الخامس مجاورة 4",
        "price_usd": 90,
        "price_egp": 4545,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 2م | خلفي: 3م | جانبي: 3م",
        "total_plots": 237,
        "recommendation": "أقل سعر متر على الإطلاق بالمرحلة 11 (90$ فقط) مع مستقبل نمو رأسمالي واعد للتوسعات الشمالية الغربية.",
        "distinguished": [15, 45, 63, 66]
    },
    "أخميم الجديدة": {
        "sector": "وحدة الجوار العمراني الـ 16",
        "price_usd": 65,
        "price_egp": 3245,
        "build_pct": 50,
        "height": "بدروم + أرضي + 3 أدوار متكررة",
        "setbacks": "أمامي: 2.5م | خلفي: 4م | جانبي: 2.5م",
        "total_plots": 52,
        "recommendation": "فرصة للمحافظ الصغيرة بأقل قيمة إجمالية للأرض على طريـق الصعيد البحر الأحمر.",
        "distinguished": [1, 2, 32]
    }
}

# Default Hardcoded Featured Plots (Fallback if Excel is not provided)
FALLBACK_PLOTS_DB = [
    # القاهرة الجديدة
    {"city": "القاهرة الجديدة", "number": 67, "area": 841.90, "price_usd": 540, "total_usd": 113656.50, "zone": "المنطقة E", "features": "ناصية متميزة جداً، مساحة كبيرة، مطلة على حدائق الحي الرابع."},
    {"city": "القاهرة الجديدة", "number": 68, "area": 720.00, "price_usd": 540, "total_usd": 97200.00, "zone": "المنطقة E", "features": "خصوصية عالية جداً، حديقة خلفية، تطل على ممر متميز."},
    {"city": "القاهرة الجديدة", "number": 69, "area": 877.40, "price_usd": 540, "total_usd": 118449.00, "zone": "المنطقة E", "features": "من أكبر القطع في الحي الرابع، ناصية صريحة، إطلالة مفتوحة."},
    {"city": "القاهرة الجديدة", "number": 120, "area": 674.40, "price_usd": 515, "total_usd": 86829.00, "zone": "المنطقة E", "features": "تطل مباشرة على منطقة النوادي، واجهة بحري صريحة."},
    {"city": "القاهرة الجديدة", "number": 149, "area": 651.30, "price_usd": 515, "total_usd": 83854.88, "zone": "المنطقة E", "features": "إطلالة ممتازة، قريبة من الخدمات، واجهة بحري صريحة."},
    {"city": "القاهرة الجديدة", "number": 2, "area": 1433.60, "price_usd": 540, "total_usd": 193536.00, "zone": "المنطقة G", "features": "أكبر قطعة أرض معروضة بالتجمع الخامس، ناصية عملاقة، تصلح لقصر عائلي."},
    {"city": "القاهرة الجديدة", "number": 7, "area": 1423.90, "price_usd": 540, "total_usd": 192226.50, "zone": "المنطقة G", "features": "مساحة عملاقة، ناصية، إطلالة بانورامية مفتوحة."},
    
    # الشيخ زايد
    {"city": "الشيخ زايد", "number": 89, "area": 1069.87, "price_usd": 496, "total_usd": 132663.88, "zone": "الحي 13 المجاورة 6", "features": "القطعة الوحيدة المعروضة بالحي 13، مساحة ضخمة لبناء فيلا فخمة."},
    {"city": "الشيخ زايد", "number": 28, "area": 442.00, "price_usd": 499, "total_usd": 55139.50, "zone": "الحي 11 المجاورة 2", "features": "القطعة الوحيدة المعروضة بالحي 11، واجهة بحري صريحة، ناصية."},
    
    # دمياط الجديدة
    {"city": "دمياط الجديدة", "number": 31, "area": 1026.10, "price_usd": 614, "total_usd": 157506.35, "zone": "الساحل منطقة A", "features": "الصف الأول على البحر مباشرة، ناصية، إطلالة بحرية كاملة."},
    {"city": "دمياط الجديدة", "number": 42, "area": 803.90, "price_usd": 614, "total_usd": 123398.65, "zone": "الساحل منطقة A", "features": "مطلة على البحر مباشرة، موقع ممتاز بالقرب من الخدمات الساحلية."},
    {"city": "دمياط الجديدة", "number": 84, "area": 1085.10, "price_usd": 614, "total_usd": 166562.85, "zone": "الساحل منطقة A", "features": "أكبر قطع الساحل مساحة، واجهة بحرية، ناصية فسيحة."},
    {"city": "دمياط الجديدة", "number": 85, "area": 1026.10, "price_usd": 614, "total_usd": 157506.35, "zone": "الساحل منطقة A", "features": "مطلة على البحر مباشرة، ناصية، واجهة بحري متميزة."}
]

# 3. Dynamic Excel Loader Block
# This block attempts to load from 'kemet_plots.xlsx' in the same folder.
# If found, it loads all 4,543 plots instantly! If not, it uses the fallback database.
EXCEL_FILENAME = "kemet_plots.xlsx"
excel_loaded = False
load_error_msg = ""

if os.path.exists(EXCEL_FILENAME):
    try:
        df_plots = pd.read_excel(EXCEL_FILENAME)
        # Strip string columns to prevent formatting issues
        for col in df_plots.columns:
            if df_plots[col].dtype == 'object':
                df_plots[col] = df_plots[col].astype(str).str.strip()
        excel_loaded = True
    except Exception as e:
        load_error_msg = str(e)
        df_plots = pd.DataFrame(FALLBACK_PLOTS_DB)
else:
    df_plots = pd.DataFrame(FALLBACK_PLOTS_DB)


# 4. App Title/Header Layout with Kemet Brand
st.markdown("""
    <div class="header-box">
        <h1 style='color: white; margin:0;'>🏢 Kemet للاستشارات العقارية</h1>
        <p style='color: #c5a059; font-size: 1.3rem; margin:10px 0 0 0;'>المساعد الاستشاري الذكي لأراضي بيت الوطن - المرحلة الحادية عشرة 2026</p>
    </div>
""", unsafe_allow_html=True)


# Show database status widget in main page
if excel_loaded:
    st.markdown(f"""
        <div class="excel-status-box">
            ✅ تم ربط البوت بنجاح بملف البيانات الخارجي '{EXCEL_FILENAME}'! عدد قطع الأراضي النشطة والمحملة بالكامل الآن: {len(df_plots)} قطعة أرض.
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
        <div class="excel-fallback-box">
            💡 <b>ملاحظة تقنية لشركة Kemet:</b> البوت يعمل الآن بنظام "القطع الذهبية الافتراضية" (مدمج {len(df_plots)} قطعة متميزة). <br/>
            لربط التطبيق بكامل الـ 4543 قطعة أرض، يرجى وضع ملف إكسل باسم <b>kemet_plots.xlsx</b> في نفس المجلد الذي يحتوي على هذا الكود، وسيقوم البوت بتحميل البيانات ديناميكياً فوراً دون تعديل الكود!
        </div>
    """, unsafe_allow_html=True)


# 5. Sidebar Layout
with st.sidebar:
    st.markdown("<h2 style='text-align: center; color:#c5a059;'>🌐 بوابة المستشار الذكي</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    # App Navigation Tabs
    tab_selection = st.radio(
        "اختر القسم المطلوب:",
        ["💬 الشات بوت الذكي", "📊 الحاسبة المالية التفاعلية", "🏙️ دليل مواصفات المدن الـ 22", "🗺️ قاعدة بيانات قطع الأراضي المتميزة"]
    )
    
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: #c5a059; font-size:0.9rem;'>
            <b>شركة Kemet للاستشارات العقارية</b><br/>
            <i>شريككم الموثوق في الاستثمار العقاري الدولي المصري</i><br/>
            <br/>
            <small>المرحلة الحادية عشرة - يونيو 2026</small>
        </div>
    """, unsafe_allow_html=True)

# 6. Core Application Tab Functions
# ====================================

# TAB 1: SMART CHATBOT
# --------------------
if tab_selection == "💬 الشات بوت الذكي":
    st.subheader("💬 اسأل المساعد العقاري لشركة Kemet")
    st.markdown("""
        أهلاً بك في شركة **Kemet للاستشارات العقارية**! يمكنك هنا كتابة أي سؤال يتعلق بأراضي بيت الوطن المرحلة 11 للاستعلام الفوري عن أرقام القطع والأسعار والشروط البنائية والبيانات البنكية [6، 8].
    """)
    
    # Initialize Chat Messages
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "assistant", "content": "أهلاً بك في شركة Kemet للاستشارات العقارية! أنا مستشارك العقاري الذكي لأراضي بيت الوطن المرحلة 11. كيف يمكنني مساعدتك اليوم؟"}
        ]
        
    for msg in st.session_state.messages:
        if msg["role"] == "assistant":
            st.markdown(f'<div class="chat-bubble-bot">{msg["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-bubble-user">{msg["content"]}</div>', unsafe_allow_html=True)
            
    # Input box
    user_input = st.text_input("اكتب سؤالك هنا باللغة العربية واضغط Enter:", key="user_question")
    
    if st.button("إرسال السؤال") and user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Rule-based matching for grounding and high quality
        response = ""
        user_input_clean = user_input.strip().lower()
        
        # Plot query parsing (e.g. piece 67, 67, قطعة 67)
        plot_matches = re.findall(r'\b\d+\b', user_input_clean)
        
        if plot_matches:
            plot_num = int(plot_matches[0])
            
            # Search dynamically in loaded df_plots (which could be the 4543 plots from Excel!)
            matching_plots = pd.DataFrame()
            if "number" in df_plots.columns:
                matching_plots = df_plots[df_plots["number"].astype(str).str.contains(str(plot_num))]
            elif "رقم القطعة" in df_plots.columns:
                matching_plots = df_plots[df_plots["رقم القطعة"].astype(str).str.contains(str(plot_num))]
                
            if not matching_plots.empty:
                plot_data = matching_plots.iloc[0]
                
                # Check column mapping
                city_val = plot_data.get("city", plot_data.get("المدينة", "غير محدد"))
                area_val = plot_data.get("area", plot_data.get("المساحة", 0))
                price_val = plot_data.get("price_usd", plot_data.get("سعر المتر بالدولار", 0))
                total_val = plot_data.get("total_usd", plot_data.get("إجمالي السعر بالدولار", 0))
                zone_val = plot_data.get("zone", plot_data.get("المنطقة", "غير محدد"))
                features_val = plot_data.get("features", plot_data.get("المميزات", "قطعة أرض سكنية متميزة"))
                
                response = f"🔍 <b>تفاصيل القطعة رقم {plot_num} التي تم العثور عليها في قاعدة بيانات Kemet:</b><br/><br/>"
                response += f"📍 <b>المدينة:</b> {city_val} ({zone_val})<br/>"
                response += f"📐 <b>المساحة الكلية:</b> {area_val} متر مربع<br/>"
                response += f"💰 <b>سعر المتر الأساسي:</b> {price_val}$ للمتر<br/>"
                response += f"💵 <b>السعر الإجمالي الأساسي:</b> {total_val:,.2f}$ دولار أمريكي<br/>"
                response += f"✨ <b>الخصوصية والمزايا:</b> {features_val}<br/><br/>"
                
                # Link with city specifications if available
                if city_val in CITIES_DB:
                    response += f"🚧 <b>الاشتراطات الهندسية لـ {city_val}:</b> تبنى على نسبة <b>{CITIES_DB[city_val]['build_pct']}%</b> " \
                                f"بارتفاع <b>{CITIES_DB[city_val]['height']}</b> والارتدادات الرسمية هي: <b>{CITIES_DB[city_val]['setbacks']}</b>."
            else:
                response = f"لقد استعلمت عن الرقم <b>{plot_num}</b>. على الرغم من أن هذا الرقم قد يكون متاحاً في الطرح، إلا أنه غير مضاف في قاعدة البيانات المحدودة حالياً.<br/>" \
                           f"<b>لربط البوت بكافة تفاصيل الـ 4543 قطعة أرض</b>، يرجى تزويد البوت بملف Excel يحمل اسم <b>kemet_plots.xlsx</b> وسيتمكن عملاؤك فوراً من الاستعلام عن أي قطعة أرض بالتفصيل والمساحة والسعر الدقيق!"
        
        # City queries
        elif any(city in user_input_clean for city in ["قاهرة", "تجمع", "cairo"]):
            c = CITIES_DB["القاهرة الجديدة"]
            response = f"🏙️ <b>تفاصيل الطرح في القاهرة الجديدة (الحي الرابع):</b><br/><br/>" \
                       f"• <b>سعر المتر الأساسي:</b> {c['price_usd']}$ للمتر يعادل {c['price_egp']:,} جنيه مصري.<br/>" \
                       f"• <b>الاشتراطات البنائية:</b> النسبة البنائية {c['build_pct']}%، بارتفاع {c['height']}، والارتدادات هي {c['setbacks']}.<br/>" \
                       f"• <b>إجمالي القطع المطروحة:</b> {c['total_plots']} قطعة أرض.<br/>" \
                       f"• <b>توصية Kemet العقارية:</b> {c['recommendation']}"
        elif any(city in user_input_clean for city in ["زايد", "zayed"]):
            c = CITIES_DB["الشيخ زايد"]
            response = f"🏙️ <b>تفاصيل الطرح النادر في الشيخ زايد:</b><br/><br/>" \
                       f"• <b>المناطق والأسعار:</b> القرار 77 بسعر {c['price_usd']}$ للمتر. الحي 11 بسعر 475$ والحي 13 بسعر 450$.<br/>" \
                       f"• <b>القطع المطروحة:</b> 29 قطعة أرض فقط في الشيخ زايد بأكملها مما يجعل التنافس عليها قياسياً.<br/>" \
                       f"• <b>الاشتراطات البنائية:</b> النسبة البنائية {c['build_pct']}%، بارتفاع {c['height']}.<br/>" \
                       f"• <b>توصية Kemet العقارية:</b> {c['recommendation']}"
        elif any(city in user_input_clean for city in ["دمياط", "damietta"]):
            c = CITIES_DB["دمياط الجديدة"]
            response = f"🏙️ <b>تفاصيل الطرح في دمياط الجديدة (بيت الوطن بالساحل وغرب المدينة):</b><br/><br/>" \
                       f"• <b>سعر المتر الأساسي:</b> {c['price_usd']}$ للمتر يعادل {c['price_egp']:,} جنيه مصري.<br/>" \
                       f"• <b>الاشتراطات البنائية:</b> النسبة البنائية {c['build_pct']}%، الارتفاع {c['height']}، والارتدادات لقطع غرب المدينة هي {c['setbacks']}.<br/>" \
                       f"• <b>أفضل القطع بالساحل:</b> قطع الصف الأول على البحر مباشرة (مثل 31، 42، 84، 85) بمساحات تصل لـ 1085م مربع.<br/>" \
                       f"• <b>توصية Kemet العقارية:</b> {c['recommendation']}"
        elif any(city in user_input_clean for city in ["شروق", "shorouk"]):
            c = CITIES_DB["الشروق"]
            response = f"🏙️ <b>تفاصيل الطرح في الشروق (زهرة الشروق موقع 3):</b><br/><br/>" \
                       f"• <b>سعر المتر الأساسي:</b> {c['price_usd']}$ للمتر يعادل {c['price_egp']:,} جنيه مصري.<br/>" \
                       f"• <b>الاشتراطات البنائية الاستثنائية:</b> النسبة البنائية {c['build_pct']}%، الارتفاع <b>بدروم + أرضي + 6 أدوار متكررة</b>، الارتدادات {c['setbacks']}.<br/>" \
                       f"• <b>توصية Kemet العقارية:</b> {c['recommendation']}"
        elif any(kw in user_input_clean for kw in ["شروط", "قانون", "قوانين", "سحب", "الغاء"]):
            response = f"🚨 <b>أهم القوانين والاشتراطات العقارية الحاكمة وسحب الأراضي:</b><br/><br/>" \
                       f"• <b>مهلة البناء:</b> يلتزم الحاجز باستخراج تراخيص البناء والانتهاء من تشييد كامل المبنى السكني في غضون <b>5 سنوات</b> من تاريخ استلام الأرض بشكل رسمي. في حال عدم الالتزام بالمهلة، تسحب الأرض تلقائياً.<br/>" \
                       f"• <b>إلغاء التخصيص للسداد:</b> يتم إلغاء تخصيص قطعة الأرض وسحبها فوراً وبدون إنذار في حال التخلف عن سداد <b>قسطين سنويين متتاليين</b>.<br/>" \
                       f"• <b>تغيير النشاط:</b> الأراضي مخصصة للاستخدام السكني فقط. يمنع تماماً تغيير النشاط للBasement (البدروم) لغير الخدمات السكنية المسموح بها، وييحظر التقسيم أو التجزئة للأرض.<br/>" \
                       f"• <b>التنازل للغير:</b> يحظر التنازل أو التصرف للغير إلا بموافقة كتابية مسبقة من جهاز المدينة ودفع الرسوم المقررة وسداد كامل الالتزامات المالية."
        elif any(kw in user_input_clean for kw in ["تحويل", "بنك", "حوالة", "swift", "iban", "دولار"]):
            response = f"🏦 <b>بيانات التحويل البنكي الرسمي البنك المركزي المصري (للمصريين بالخارج):</b><br/><br/>" \
                       f"• <b>البنك المراسل بالخارج:</b> Citi Bank, New York (سويفت: CITIUS33XXX) | حساب رقم: 36001304<br/>" \
                       f"• <b>البنك المستفيد بمصر:</b> البنك المركزي المصري - القاهرة (سويفت: CBEGEGCXXXX)<br/>" \
                       f"• <b>رقم الأيبان (IBAN):</b> EG020001000100000004082192000 | حساب رقم: 4082192000<br/>" \
                       f"• <b>اسم المستفيد:</b> New Urban Communities Authority - Egyptians Abroad (هيئة المجتمعات العمرانية الجديدة - المصريين بالخارج)<br/><br/>" \
                       f"⚠️ <b>تنبيه هام جداً من شركة Kemet:</b> الحد الأدنى للتحويل التنشيطي للحصول على أولوية حجز قطعة جديدة هو <b>3,050 دولار</b> (تتضمن 50$ رسوم دراسة غير مستردة). يجب كتابة كود حجز قطعة واحدة فقط بشكل صحيح بالتحويل."
        elif any(kw in user_input_clean for kw in ["تقسيط", "دفع", "بديل", "طريقة"]):
            response = f"💵 <b>البدائل الرسمية لسداد ثمن أراضي بيت الوطن المرحلة 11:</b><br/><br/>" \
                       f"• <b>البديل الأول (الكاش والسداد السريع):</b> سداد كامل المبلغ دفعة واحدة والحصول على <b>خصم فوري يصل إلى 7.5%</b> من إجمالي ثمن القطعة بالدولار.<br/>" \
                       f"• <b>البديل الثاني (التقسيط الممتد لـ 7 سنوات):</b> سداد مقدم الحجز 25% بالدولار، وتقسيط المبلغ المتبقي (75%) على أقساط سنوية متساوية لمدة تصل لـ <b>7 سنوات</b> بـ <b>سعر فائدة سنوي ثابت 4.75%</b> + 0.5% مصاريف إدارية. تتميز هذه الطريقة بتثبيت ثمن الأرض بالجنيه المصري طوال فترة السداد كحماية ممتازة من التضخم وصعود الدولار."
        else:
            response = f"مرحباً بك مجدداً في شركة Kemet للاستشارات العقارية. لتقديم الإجابة الاستشارية الأدق، يمكنك الاستفسار عن تفاصيل أي مدينة بالكامل (مثال: القاهرة الجديدة، دمياط الجديدة، الشيخ زايد، برج العرب، سوهاج الجديدة، الفيوم الجديدة)، أو الاستعلام عن الشروط البنائية والبيانات البنكية وطرق السداد المعتمدة."
        
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

# TAB 2: FINANCIAL CALCULATOR
# ---------------------------
elif tab_selection == "📊 الحاسبة المالية التفاعلية":
    st.subheader("📊 حاسبة التكاليف والأقساط التفاعلية لشركة Kemet")
    st.markdown("احسب الموازنة المالية التقديرية بدقة لأي قطعة أرض بناءً على مدينتها ومساحتها المحددة وطريقة السداد المفضلة.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        city_sel = st.selectbox("اختر المدينة المراد تقييمها مالياً:", list(CITIES_DB.keys()))
        area_input = st.number_input("أدخل مساحة قطعة الأرض بالمتر المربع (SQM):", min_value=100.0, max_value=5000.0, value=500.0, step=10.0)
        distinction_pct = st.selectbox("نوع ونسبة التميز لقطعة الأرض:", [("عادية - بدون تميز", 0.0), ("ناصية (تميز 5%)", 5.0), ("مطلة على حدائق (تميز 5%)", 5.0), ("مطلة على الساحل/البحر مباشرة (تميز 15%)", 15.0)])
    
    city_data = CITIES_DB[city_sel]
    base_price_usd = city_data["price_usd"]
    dist_pct = distinction_pct[1]
    
    # Cost calculations
    price_per_meter_usd = base_price_usd * (1 + (dist_pct / 100))
    total_cost_usd = area_input * price_per_meter_usd
    total_cost_egp = total_cost_usd * (city_data["price_egp"] / city_data["price_usd"])
    
    down_payment_usd = total_cost_usd * 0.25
    remaining_balance_usd = total_cost_usd * 0.75
    
    with col2:
        st.markdown(f"""
            <div style='background-color: white; padding: 20px; border-radius: 8px; border-top: 4px solid #0f1c30; box-shadow: 0 4px 6px rgba(0,0,0,0.05);'>
                <h3 style='color: #0f1c30; margin-top:0;'>💰 ملخص التكلفة التقديرية بالدولار:</h3>
                <p style='font-size: 1.1rem; margin:5px 0;'>📍 <b>المدينة:</b> {city_sel} - {city_data['sector']}</p>\n                <p style='font-size: 1.1rem; margin:5px 0;'>📏 <b>المساحة:</b> {area_input:,.2f} م²</p>\n                <p style='font-size: 1.1rem; margin:5px 0;'>💵 <b>سعر المتر بالدولار (شامل التميز):</b> {price_per_meter_usd:,.2f} $ للمتر</p>\n                <p style='font-size: 1.3rem; color: #c5a059; margin: 10px 0;'><b>إجمالي ثمن الأرض: {total_cost_usd:,.2f} $ دولـار أمريكي</b></p>\n                <p style='font-size: 1.0rem; color: #777;'>يعادل تقريباً بالليدجر المصري: {total_cost_egp:,.2f} جنيه مصري</p>\n            </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")
    st.subheader("💡 قارن خيارات السداد المعتمدة لقطعة الأرض:")
    
    tab_alt1, tab_alt2 = st.tabs(["🟢 البديل الأول: السداد السريع (خصم 7.5%)", "🔵 البديل الثاني: التقسيط الممتد لـ 7 سنوات"])
    
    with tab_alt1:
        discount_amount = total_cost_usd * 0.075
        final_fast_pay = total_cost_usd - discount_amount
        st.markdown(f"""
            <div style='background-color: #e2f0d9; padding: 20px; border-radius: 8px; border-left: 5px solid #548235;'>
                <h4 style='color: #385723; margin-top:0;'>✨ تفاصيل البديل المالي للسداد الفوري الكاش:</h4>
                <p>• سداد كامل ثمن الأرض دفعة واحدة يمنحك خصماً مباشراً بنسبة <b>7.5%</b> من إجمالي ثمن القطعة بالدولار.</p>\n                <p>• <b>مبلغ الخصم الفوري الممنوح لك:</b> {discount_amount:,.2f} $ دولار أمريكي</p>\n                <p style='font-size:1.25rem; color: #385723;'><b>💵 المبلغ الإجمالي المطلوب سداده كاملاً: {final_fast_pay:,.2f} $ دولار أمريكي</b></p>\n            </div>
        """, unsafe_allow_html=True)
        
    with tab_alt2:
        annual_installment_usd = remaining_balance_usd / 7
        st.markdown(f"""
            <div style='background-color: #f0f4f8; padding: 20px; border-radius: 8px; border-left: 5px solid #0f1c30;'>
                <h4 style='color: #0f1c30; margin-top:0;'>📅 تفاصيل التقسيط المريح (7 سنوات - سعر فائدة 4.75% ثابت):</h4>
                <p>• <b>مقدم حجز السكن الأساسي (25% بالدولار):</b> {down_payment_usd:,.2f} $ دولار أمريكي</p>\n                <p>• <b>المبلغ المتبقي للتقسيط (75% بالدولار):</b> {remaining_balance_usd:,.2f} $ دولار أمريكي</p>\n                <p>• <b>تقسيم الأقساط:</b> يتم السداد على 7 أقساط سنوية متساوية بفائدة سنوية ثابتة تبلغ <b>4.75%</b> + 0.5% مصاريف إدارية.</p>\n                <p style='font-size:1.2rem; color: #0f1c30;'><b>💵 قيمة القسط السنوي الأساسي بالدولار (قبل الفوائد): {annual_installment_usd:,.2f} $ دولار أمريكي/سنوياً</b></p>\n                <p style='font-size:0.95rem; color: #555;'><i>* ملاحظة: يتم سداد القسط الأول بعد مرور سنة كاملة من تاريخ استلام الأرض.</i></p>\n            </div>
        """, unsafe_allow_html=True)

# TAB 3: CITY SPECIFICATIONS
# -------------------------
elif tab_selection == "🏙️ دليل مواصفات المدن الـ 22":
    st.subheader("🏙️ تصفح مواصفات وجداول المدن الـ 22 المطروحة")
    st.markdown("اختر المدينة لاستعراض سعر المتر، النسبة البنائية المحددة، الارتدادات الهندسية الرسمية، ومستويات الارتفاع المسموح بها.")
    
    selected_city_details = st.selectbox("اختر مدينة لرؤية مواصفاتها التفصيلية:", list(CITIES_DB.keys()))
    c_info = CITIES_DB[selected_city_details]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
            <div class="city-card">
                <h3 style='color: #0f1c30; margin-top:0;'>📍 {selected_city_details}</h3>
                <p style='font-size:1.1rem;'><b>🏙️ النطاق والموقع الجغرافي بالطرح:</b> {c_info['sector']}</p>\n                <p style='font-size:1.1rem;'><b>💰 سعر المتر الأساسي بالدولار:</b> {c_info['price_usd']}$ للمتر</p>\n                <p style='font-size:1.1rem;'><b>💵 سعر المتر الدفتري بالجنيه:</b> {c_info['price_egp']:,} ج</p>\n                <p style='font-size:1.1rem;'><b>🔢 إجمالي الأراضي المتاحة بالطرح:</b> {c_info['total_plots']} قطعة</p>\n            </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown(f"""
            <div class="city-card" style='border-left-color: #0f1c30;'>
                <h3 style='color: #0f1c30; margin-top:0;'>🚧 الاشتراطات الفنية والهندسية للبناء:</h3>
                <p style='font-size:1.1rem;'><b>📐 نسبة البناء القصوى من مساحة الأرض:</b> {c_info['build_pct']}%</p>\n                <p style='font-size:1.1rem;'><b>🏢 الارتفاع المسموح به:</b> {c_info['height']}</p>\n                <p style='font-size:1.1rem;'><b>📏 الارتدادات المعتمدة من جهاز المدينة:</b> {c_info['setbacks']}</p>\n                <p style='font-size:1.1rem; color: #c5a059;'><b>🎯 التوصية الاستشارية لـ Kemet:</b> {c_info['recommendation']}</p>\n            </div>
        """, unsafe_allow_html=True)

# TAB 4: DISTINGUISHED PLOTS
# --------------------------
elif tab_selection == "🗺️ قاعدة بيانات قطع الأراضي المتميزة":
    st.subheader("🗺️ قطع أراضي متميزة وفرص استثمارية استثنائية")
    st.markdown("تصفح قاعدة بيانات الأراضي التي تقع في أرقى الأحياء وتوفر مساحات كبيرة أو إطلالات ناصية أو مطلة على البحر مباشرة.")
    
    search_query = st.text_input("ابحث بالمدينة أو رقم القطعة (مثال: القاهرة الجديدة أو 67):", "")
    
    if not df_plots.empty:
        # Search dynamically based on Excel column structure
        city_col = "city" if "city" in df_plots.columns else ("المدينة" if "المدينة" in df_plots.columns else "")
        num_col = "number" if "number" in df_plots.columns else ("رقم القطعة" if "رقم القطعة" in df_plots.columns else "")
        features_col = "features" if "features" in df_plots.columns else ("المميزات" if "المميزات" in df_plots.columns else "")
        area_col = "area" if "area" in df_plots.columns else ("المساحة" if "المساحة" in df_plots.columns else "")
        price_col = "price_usd" if "price_usd" in df_plots.columns else ("سعر المتر" if "سعر المتر" in df_plots.columns else "")
        total_col = "total_usd" if "total_usd" in df_plots.columns else ("الإجمالي" if "إجمالي السعر" in df_plots.columns else "")
        zone_col = "zone" if "zone" in df_plots.columns else ("المنطقة" if "المنطقة" in df_plots.columns else "")
        
        if search_query:
            try:
                num_query = int(search_query)
                if num_col:
                    filtered_df = df_plots[df_plots[num_col].astype(str).str.contains(str(num_query))]
                else:
                    filtered_df = df_plots
            except ValueError:
                cond = pd.Series([False] * len(df_plots))
                if city_col:
                    cond = cond | df_plots[city_col].astype(str).str.contains(search_query)
                if zone_col:
                    cond = cond | df_plots[zone_col].astype(str).str.contains(search_query)
                if features_col:
                    cond = cond | df_plots[features_col].astype(str).str.contains(search_query)
                filtered_df = df_plots[cond]
        else:
            filtered_df = df_plots
            
        st.markdown(f"**عدد القطع المكتشفة بالقائمة المتميزة:** {len(filtered_df)}")
        
        # Render Plot Cards
        for idx, row in filtered_df.iterrows():
            r_num = row.get(num_col, "غير محدد")
            r_city = row.get(city_col, "غير محدد")
            r_zone = row.get(zone_col, "غير محدد")
            r_area = row.get(area_col, 0)
            r_price = row.get(price_col, 0)
            r_total = row.get(total_col, 0)
            r_features = row.get(features_col, "مواصفات قياسية متميزة للبناء.")
            
            st.markdown(f"""
                <div class="plot-card">
                    <div style='display: flex; justify-content: space-between; align-items: center;'>
                        <span style='font-size:1.25rem; font-weight:bold; color: #0f1c30;'>📍 قطعة رقم {r_num} - {r_city} ({r_zone})</span>\n                        <span style='background-color:#c5a059; color:white; padding:4px 10px; border-radius:15px; font-size:0.85rem; font-weight:bold;'>كود نشط</span>\n                    </div>
                    <hr style='margin:10px 0; border: 0.5px solid #eee;'/>
                    <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px;'>
                        <div><b>📐 المساحة الكلية:</b> {r_area} م²</div>\n                        <div><b>💰 سعر المتر بالدولار:</b> {r_price}$</div>\n                        <div><b>💵 إجمالي ثمن القطعة:</b> {r_total:,.2f}$</div>\n                    </div>
                    <p style='margin:10px 0 0 0; color: #555;'><b>✨ المزايا والخصوصية:</b> {r_features}</p>\n                </div>
            """, unsafe_allow_html=True)
    else:
        st.info("قاعدة البيانات فارغة حالياً. يرجى توفير ملف Excel الخارجي لتغذية البوت بالبيانات.")
