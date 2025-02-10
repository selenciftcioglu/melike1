<!DOCTYPE html>
<html>
<head>
<title>Fiyat Hesaplama</title>
</head>
<body>
<h1>Fiyat Hesaplama</h1>

<!-- Yüzdelik oran girişleri -->
<label for="akrilik">20/1 Akrilik (%):</label>
<input type="number" id="akrilik" min="0" max="100" />

<label for="polyester">20/1 Polyester (%):</label>
<input type="number" id="polyester" min="0" max="100" />

<button onclick="calculateTotal()">Hesapla</button>

<p id="result">Toplam Fiyat: </p>

<script>
function calculateTotal() {
    const akrilik = parseInt(document.getElementById('akrilik').value) || 0;
const polyester = parseInt(document.getElementById('polyester').value) || 0;

// API'ye JSON gönderme
fetch('http://127.0.0.1:5000/calculate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        percentages: {
            "20/1 Akrilik": akrilik,
            "20/1 Polyester": polyester
        }
    })
})
.then(response => response.json())
.then(data => {
    document.getElementById('result').innerText =
`Toplam Fiyat: ${data.total_price} USD + KDV`;
});
}
</script>
</body>
</html>