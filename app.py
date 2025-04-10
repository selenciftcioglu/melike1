import pandas as pd
from flask import Flask, request, render_template_string, jsonify, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Gizli anahtar, oturum verilerini güvenli hale getirmek için kullanılır

def load_business_data_from_excel(file_path):
    df = pd.read_excel(file_path, sheet_name=None)
    business_info = {}
    for sheet_name, sheet_data in df.items():
        unit_price_row = sheet_data[sheet_data['sekme'] == 'unit_price']
        if unit_price_row.empty:
            raise ValueError(f"'unit_price' satırı bulunamadı: {sheet_name}")
        unit_price = unit_price_row['price'].values[0]
        alt_sekmeler = {}
        for index, row in sheet_data.iterrows():
            if row['sekme'] == 'unit_price':
                continue  # Skip the unit_price row
            sekme = row['sekme']
            option = row['option']
            price = row['price']
            if sekme not in alt_sekmeler:
                alt_sekmeler[sekme] = {}
            alt_sekmeler[sekme][option] = price
        business_info[sheet_name] = {
            "unit_price": unit_price,
            "alt_sekmeler": alt_sekmeler
        }
    return business_info

# İşletmeler ve birim fiyatları
business_data = load_business_data_from_excel('c:\\Users\\batuu\\OneDrive\\Masaüstü\\DOSYALAR\\melike1\\business_data.xlsx')

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
            <img src="{{ url_for('static', filename='logo.png') }}" alt="Logo" class="img-fluid mb-4" style="max-width: 200px;">
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
                        if (data.unit_price !== undefined) {
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