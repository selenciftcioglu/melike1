from flask import Flask, request, render_template_string, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey' # Gizli anahtar, oturum verilerini güvenli hale getirir.

# İşletmeler ve birim fiyatları
business_data = {
    "Polip": {
        "unit_price": 2.10,
        "alt_sekmeler": {
            "İplik Numarası": {"1200-1299 Dtex ": 0.25, "1300-1399 Dtex": 0.20, "1400-1599 Dtex": 0.10, "1600-1799 Dtex": 0.05, "1800-2199 Dtex": 0.00, "2200-2600 Dtex": 0.00, "2600-4800 Dtex": 0.00},
            "Flament": {"60-200": 0, "210-280": 0.05, "280-360": 0.1, "360-420": 0.15},
            "Kat": {"10": 0, "20": 0, "30": 0, "40": 0, "50": 0, "60": 0, "70": 0},
            "İplik Cinsi": {"HEATSET": 0, "FRIZE": 0, "PUNTO": 0, "CPC": 0.05, "TRICOLOR": 0.05, "BCF": -0.2},
            "Büküm": {"60-150": 0, "150-200": 0.05, "200-250": 0.1, "250-300": 0.15},
            "UV Yumuşatıcı": {"%1": 0.075, "%2": 0.15},
            "Renk": {"BORDO": 0.3, "KIRMIZI": 0.3, "KIREMIT": 0.3, "LACIVERT": 0.25, "YESIL": 0.25, "KAHVE": 0.25},
        },
    },
    "Şönil": {
        "unit_price": 0,
        "alt_sekmeler": {
            "NM": {"Var": 3.50, "Yok": 0},
            "20/1 Polyester": {"Var": 2.70, "Yok": 0},
            "20/1 Viskon": {"Var": 3.10, "Yok": 0},
            "20/1 Bambu": {"Var": 3.50, "Yok": 0},
        },
    },
    "Akrilik": {
        "unit_price": 4.00,
        "alt_sekmeler": {
            "Elyaf Cinsi": {"2,75 DNY": 0.10, "6 DNY": 0, "1,7 DNY": 0.10},
            "İplik Numarası": {"6": -0.20, "10": -0.15, "15": 0, "18": 0.10, "21": 0.20, "24":0.30, "27": 0.40, "30": 0.50, "32": 0.60, "34": 0.70, "36": 0.80, "38": 0.90, "40": 1, "42": 1.10, "44": 1.20, "46": 1.30, "48": 1.40, "50": 1.50 },
            "Kat": {"3": 0, "2": 0.15, "4": 0.05},
            "İplik Cinsi": {"RX": 0, "HB": 0.10, "HB NE": 0.15, "TAFT": 0.20},
            "Zincir Büküm": {"Var": 0.50, "Yok": 0},
        },
    },
    "Pamuk": {
        "unit_price": 3.10,
        "alt_sekmeler": {
            "NM": {"16/1 Penye Compak Penye Triko": -0.15, "20/1 Penye Compak Penye Triko": -0.10, "24/1 Penye Compak Penye Triko": -0.05, "28/1 Penye Compak Penye Triko": 0, "30/1 Penye Compak Penye Triko": 0, "36/1 Penye Compak Penye Triko": 0.30, "40/1 Penye Compak Penye Triko": 0.50, "50/1 Penye Compak Penye Triko": 1.50, "60/1 Penye Compak Penye Triko": 2.50},
            "Hammadde": {"Yöre": 0, "USA": 0.15},
            "Torsiyon": {"Dokuma": 0.05, "Triko": 0},
            "Karde": {"Var": -0.15, "Yok": 0},
            "Sertifika Türü": {"BCI": 0.10, "Organik": 0.50},
            "Şantuk": {"Var": 0.25, "Yok": 0},
            "Boya Bobini": {"Var": 0.10, "Yok": 0},
            "Büküm": {"20/2 Katlama Büküm": 0.55, "30/2 Katlama Büküm": 0.80, "40/2 Katlama Büküm": 1.20, "Krep": 0.10},
        },
    },
    "Openend": {
        "unit_price": 2.40,
        "alt_sekmeler": {
            "Telef": {"Var": 0, "Yok": -0.80},
        },
    },
    "Ring": {
        "unit_price": 0,
        "alt_sekmeler": {
            "20/1 Akrilik": {"Var": 3.50, "Yok": 0},
            "20/1 Polyester": {"Var": 2.70, "Yok": 0},
            "20/1 Viskon": {"Var": 3.10, "Yok": 0},
            "20/1 Bambu": {"Var": 3.50, "Yok": 0},
            "20/1 Tensel": {"Var": 3.40, "Yok": 0},
            "20/1 Modal": {"Var": 4.20, "Yok": 0},
            "Boya": {"Var": 0.05, "Yok": 0},
            "İplik Numarası": {"1": 0, "2": 0, "3": 0},
            "Kat Maliyeti": {"6": 0, "9": 0, "12": 0},
        },
    },
     "Triko Akrilik": {
            "unit_price": 4.60,
            "alt_sekmeler": {
                "LP Tüylenme Engelleyici": {"Var": 0.20, "Yok": 0},
                "İplik Türü": {"1/9.5*7.5 Nm HB Akr 2.75 Dtex": -0.50, "1/18*15 Nm HB Akr 2.75 Dtex": -0.30, "1/23*19 Nm HB Akr 2.75 Dtex": -0.20, "2/35*28 Nm HB Akr 2.75 Dtex": 0, "1/40*32 Nm HB Akr 2,75 Dtex": 0.30, "2/40*32 Nm HB Akr 2,75 Dtex": 0.50},
            },
        },
}

# Kullanıcı adı ve şifre
users = {
    "admin": "password123"
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return "Kullanıcı adı veya şifre yanlış", 401

    login_page = """
     <html>
    <head>
        <title>Giriş Yap</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
    </head>
    <body>
        <div class="container mt-4">
        <img src="{{url_for('static', filename='logo.png')}}" alt="logo" class="img-fluid mb-4" style="max-width: 2000px;">
            <h1 class="text-primary">Giriş Yap</h1>
            <form method="post">
                <div class="form-group">
                    <label for="username">Kullanıcı Adı:</label>
                    <input type="text" class="form-control" id="username" name="username" required>
                </div>
                <div class="form-group mt-3">
                    <label for="password">Şifre:</label>
                    <input type="password" class="form-control" id="password" name="password" required>
                </div>
                <button type="submit" class="btn btn-primary mt-3">Giriş Yap</button>
            </form>
        </div>
    </body>
    </html>
    """
    return render_template_string(login_page)

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))

    # İşletme listesi için HTML sayfası
    page = """
    <html>
    <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha3/dist/css/bootstrap.min.css" rel="stylesheet">
    <div class="container mt-4">
     <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" class="img-fluid mb-4" style="max-width: 200px;">
     
    <h1 class="text-primary">Fiyat Hesaplama Sistemi</h1>

    <div class="form-group mt-3">
        <label for="business">İşletme Seçiniz:</label>
        <select class="form-select" id="business" onchange="loadSubSections()">
            <option value="">Bir işletme seçin</option>
            {% for business in businesses %}
                <option value="{{ business }}">{{ business }}</option>
            {% endfor %}
        </select>
    </div>

    <div id="sectionsContainer" class="mt-4">
        <p class="text-muted">İşletme seçin</p>
    </div>

    <h2 class="mt-3">Toplam Fiyat: <span id="totalPrice" class="text-success">0</span> </h2>
</div>
        <style>
              body {
                font-family: Arial, sans-serif;
                margin: 30px;
                line-height: 1.6;
            }

            h1 {
                color: #333;
            }

            select {
                padding: 8px;
                font-size: 14px;
            }

            .alt-section {
                margin-top: 10px;
                padding: 10px;
                border-radius: 4px;
                border: 1px solid #ddd;
                background: #fafafa;
                box-shadow: 0 1px 2px rgba(0,0,0,0.1);
            }

            #totalPrice {
                color: #007BFF;
                font-weight: bold;
                font-size: 1.3em;
            }
        </style>
    </head>
    <body>
        <script>
            // İşletmelerle ilişkili alt sekmeleri getirme
            function loadSubSections() {
                const business = document.getElementById('business').value;
                const sectionsContainer = document.getElementById('sectionsContainer');

                if (!business) {
                    sectionsContainer.innerHTML = '<p>İşletme Seçin.</p>';
                    document.getElementById('totalPrice').innerText = 0;
                    return;
                }

                // Backend'den işletmeyle ilgili alt sekme ve fiyat verilerini çek
                fetch(`/get_sections?business=${business}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data) {
                            let html = `<p>Baz Fiyat: <strong>${data.unit_price} USD</strong></p>`;
                            // Alt sekmeleri oluştur
                            data.alt_sekmeler.forEach((section, index) => {
                                html += `
                                    <div class="alt-section">
                                        <h3>${section.name}</h3>
                                        <label for="input-${index}">Seçenekler:</label>
                                        <select id="input-${index}" onchange="updateTotal(${data.unit_price})">
                                            <option value="0">Seçim</option>
                                            ${section.options.map(opt => `<option value="${opt.price}">${opt.name} (+${opt.price} USD)</option>`).join('')}
                                        </select>
                                    </div>
                                `;
                            });
                            sectionsContainer.innerHTML = html;
                            updateTotal(data.unit_price);
                        } else {
                            sectionsContainer.innerHTML = '<p>Bu işletme için veri bulunamadı.</p>';
                        }
                    });
            }

            // Toplam fiyatı güncelleme
            function updateTotal(basePrice) {
                let total = basePrice;

                const dropdowns = document.querySelectorAll('select[id^="input-"]');
                    dropdowns.forEach(dropdown => {
                     const selectedValue = parseFloat(dropdown.value) || 0;
                     total += selectedValue;
                });

                document.getElementById("totalPrice").innerText = total.toFixed(2) + " USD + KDV";
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(page, businesses=business_data.keys())

@app.route('/calculate', methods=['POST'])
def calculate_price():
    data = request.json
    percentages = data.get('percentages', {})
    business_name = data.get('business', '')

    if not business_name or business_name not in business_data:
        return jsonify({"error": "Geçersiz işletme"}), 400

    business_info = business_data[business_name]

    total_price = business_info["unit_price"]
    for feature, selected_value in percentages.items():
        if feature in business_info["alt_sekmeler"]:
            options = business_info["alt_sekmeler"][feature]
            price_add = options.get(selected_value, 0)
            total_price += price_add

    return jsonify({"total_price": round(total_price, 2)})

@app.route('/get_sections')
def get_sections():
    # İşletme adı al
    business = request.args.get('business')

    if not business or business not in business_data:
        return jsonify({"unit_price": 0, "alt_sekmeler": []})

    business_info = business_data[business]
    alt_sekmeler_list = [
        {"name": sekme, "options": [{"name": option, "price": price} for option, price in options.items()]}
        for sekme, options in business_info["alt_sekmeler"].items()
    ]

    return jsonify({"unit_price": business_info["unit_price"], "alt_sekmeler": alt_sekmeler_list})


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5007)
