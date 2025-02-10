from flask import Flask, request, render_template_string
import pandas as pd

app = Flask(__name__)

#İşletmeler
df = pd.DataFrame({'İşletme': ['Pamuk', 'Polip', 'Şönil', 'Akrilik', 'Openend', 'Ring', 'Triko'], 'Alt Seçenek': ['İplik Numarası', 'Kat', 'İplik Cinsi', 'Flament', 'Büküm', 'Boya', 'Renk']})

# İplik verilerini Excel'den okuma
def load_data_from_csv(file_path):
    return pd.read_csv(file_path, encoding='latin1')

# DataFrame'i dosyadan yükle
df = load_data_from_csv('crmx.csv')


# Fiyat hesaplama fonksiyonu
def calculate_price(selected_yarns):
    total_price = 0
    for yarn in selected_yarns:
        if yarn in df['İplik Türü'].values:
            price = df.loc[df['İplik Türü'] == yarn, 'Fiyat'].values[0]
            total_price += price
        else:
            return f"{yarn} türü bulunamadı."
    return total_price


# Ana sayfa ve form işlemleri
@app.route('/', methods=['GET', 'POST'])
def index():
    total_price = None
    if request.method == 'POST':
        selected_yarns = request.form['yarns'].split(',')
        total_price = calculate_price([yarn.strip() for yarn in selected_yarns])

    # Basit HTML şablonu
    page = """
    <html>
    <body>
        <h1>İplik Fiyat Hesaplayıcı</h1>
        <form method="post">
            <label for="yarns">İplik Türü Seçiniz:</label>
            <input type="text" name="yarns" size="50">
            <input type="submit" value="Hesapla">
        </form>
        {% if total_price != None %}
            <h2>Toplam fiyat: {{ total_price }} TL</h2>
        {% endif %}
    </body>
    </html>
    """

    return render_template_string(page, total_price=total_price)


if __name__ == '__main__':
    app.run(debug=True, port=5001)