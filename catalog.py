"""Static options shown in the profile panel, per product category."""

CATEGORIES = {
    "smartphone": {
        "label": "Smartphone",
        "short": "HP",
        "icon": ":material/smartphone:",
        "purposes": [
            "Pemakaian harian",
            "Fotografi",
            "Gaming",
            "Konten & video",
            "Kerja / bisnis",
        ],
        "priorities": [
            "Baterai awet",
            "Kamera bagus",
            "Performa",
            "Layar bagus",
            "Ukuran ringkas",
            "Update software lama",
        ],
        "budgets": [2_000_000, 4_000_000, 7_000_000, 12_000_000],
        "notes_placeholder": "mis. butuh NFC, HP sekarang Redmi Note 10",
        "suggestions": [
            "HP dengan kamera terbaik di bawah Rp5 juta",
            "HP gaming yang baterainya awet, budget Rp4 juta",
            "Bandingkan HP flagship yang sedang populer",
            "HP simpel dan awet untuk orang tua",
        ],
    },
    "laptop": {
        "label": "Laptop",
        "short": "Laptop",
        "icon": ":material/laptop:",
        "purposes": [
            "Kuliah / kantor",
            "Programming",
            "Desain grafis",
            "Editing video",
            "Gaming",
        ],
        "priorities": [
            "Ringan & portabel",
            "Baterai awet",
            "Performa",
            "Layar akurat warna",
            "Build quality",
            "Bisa di-upgrade",
        ],
        "budgets": [7_000_000, 12_000_000, 18_000_000, 25_000_000],
        "notes_placeholder": "mis. sering dibawa ke kampus, butuh port HDMI",
        "suggestions": [
            "Laptop kuliah yang ringan, budget Rp8 juta",
            "Laptop programming yang awet dipakai 5 tahun",
            "Laptop untuk editing video, budget Rp20 juta",
            "MacBook atau Windows untuk desain grafis?",
        ],
    },
    "pc": {
        "label": "Komponen PC",
        "short": "PC",
        "icon": ":material/memory:",
        "purposes": [
            "Gaming",
            "Editing / rendering",
            "Streaming",
            "Programming / AI",
            "Kantor",
        ],
        "priorities": [
            "Value for money",
            "Performa maksimal",
            "Hemat daya",
            "Senyap",
            "Siap upgrade",
        ],
        "components": ["CPU", "RAM", "Kartu grafis (GPU)"],
        "budgets": [3_000_000, 6_000_000, 10_000_000, 20_000_000],
        "notes_placeholder": "mis. motherboard B550, PSU 550W, main di 1440p",
        "suggestions": [
            "GPU untuk gaming 1440p, budget Rp7 juta",
            "Upgrade RAM: DDR4 atau DDR5?",
            "Pasangan CPU + GPU tanpa bottleneck, Rp10 juta",
            "CPU terbaik untuk editing dan streaming",
        ],
    },
}


def format_rupiah(value: int) -> str:
    return "Rp" + f"{int(value):,}".replace(",", ".")


def format_budget_short(value: int) -> str:
    return f"≤ {value // 1_000_000} jt"
