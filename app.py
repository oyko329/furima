from flask import Flask, render_template_string, request, redirect
import uuid

app = Flask(__name__)

DATA = []

SELL_FEES = {
    "ラクマ": 0.10,
    "ヤフーフリマ": 0.05,
    "メルカリ": 0.10
}

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<title>うんちぶりぶり💩</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    background: #fff0f6;
    margin: 0;
    padding: 16px;
}
.container {
    display: flex;
    gap: 20px;
}
.sidebar {
    width: 320px;
}
.main {
    flex: 1;
}
form, table, .card {
    background: white;
    border-radius: 24px;
    box-shadow: 0 12px 32px rgba(255,105,180,0.15);
    padding: 16px;
    margin-bottom: 20px;
}
h2 {
    margin-top: 0;
    color: #d63384;
}
select, input, button {
    width: 100%;
    border-radius: 16px;
    padding: 12px;
    border: 1px solid #f3c1d9;
    margin-bottom: 10px;
    font-size: 16px;
}
button {
    background: #ff6fae;
    color: white;
    border: none;
}
table {
    width: 100%;
    border-collapse: collapse;
}
th, td {
    border-bottom: 1px solid #f8d7e8;
    padding: 10px;
    font-size: 15px;
    text-align: center;
}
th {
    color: #c2255c;
}
tfoot td {
    font-weight: bold;
    background: #fff5f9;
}
.summary {
    font-size: 18px;
    text-align: right;
    color: #c2255c;
    margin-top: 8px;
}
.delete {
    cursor: pointer;
    font-size: 20px;
}
canvas {
    width: 100% !important;
}
@media (max-width: 900px) {
    .container {
        flex-direction: column;
    }
    .sidebar {
        width: 100%;
    }
}
</style>
</head>
<body>

<div class="container">

<div class="sidebar">
<h2>入力</h2>
<form method="post">
<select name="buy_platform">
<option>お店</option><option>SHEIN</option><option>TEMU</option>
<option>アリエク</option><option>百均</option>
</select>

<select name="category">
<option>ガチャ</option><option>ステッカー</option><option>服</option>
<option>文房具</option><option>雑貨</option>
</select>

<input name="name" placeholder="商品名">
<input type="date" name="buy_date">
<input type="date" name="sell_date">

<input name="buy_price" placeholder="仕入">
<input name="sell_price" placeholder="販売">
<input name="shipping" placeholder="送料">

<select name="sell_site">
<option value="">未売却</option>
<option>ラクマ</option><option>ヤフーフリマ</option><option>メルカリ</option>
</select>

<button>追加</button>
</form>
</div>

<div class="main">
<h2>データ</h2>
<table>
<thead>
<tr>
<th>タグ</th><th>商品名</th><th>購入日</th><th>売却日</th>
<th>仕入</th><th>販売</th><th>送料</th>
<th>利益</th><th>利益率</th><th></th>
</tr>
</thead>
<tbody>
{% for d in data %}
<tr>
<td>{{ d.buy_platform }} / {{ d.category }} / {{ d.sell_site }}</td>
<td>{{ d.name }}</td>
<td>{{ d.buy_date }}</td>
<td>{{ d.sell_date }}</td>
<td>{{ d.buy_price }}</td>
<td>{{ d.sell_price }}</td>
<td>{{ d.shipping }}</td>
<td>{{ d.profit }}</td>
<td>{{ d.rate }}%</td>
<td class="delete" onclick="location.href='/delete/{{ d.id }}'">🗑</td>
</tr>
{% endfor %}
</tbody>
<tfoot>
<tr>
<td colspan="4">合計</td>
<td>{{ total_buy }}</td>
<td></td>
<td></td>
<td>{{ total_profit }}</td>
<td colspan="2"></td>
</tr>
</tfoot>
</table>

<div class="summary">
現在の儲け： {{ total_profit - total_buy }}
</div>

<div class="card">
<h2>購入元 × 平均利益率</h2>
<canvas id="bar"></canvas>
</div>

<div class="card">
<h2>売れたサイト別 × 分類</h2>
{% for site, pdata in sell_pies.items() %}
<h4>{{ site }}</h4>
<canvas id="sell_{{ loop.index }}"></canvas>
<script>
new Chart(document.getElementById("sell_{{ loop.index }}"),{
    type:"pie",
    data:{
        labels: {{ pdata.labels|safe }},
        datasets:[{
            data: {{ pdata.ratios|safe }},
            backgroundColor:["#ff6fae","#ffb3d9","#ffc0cb","#f783ac","#faa2c1"]
        }]
    }
});
</script>
{% endfor %}
</div>

</div>
</div>

<script>
new Chart(document.getElementById("bar"),{
    type:"bar",
    data:{
        labels: {{ platforms|safe }},
        datasets:[{
            label:"利益率",
            data: {{ rates|safe }},
            backgroundColor:"#ff6fae"
        }]
    }
});
</script>

</body>
</html>
"""

@app.route("/", methods=["GET","POST"])
def index():
    if request.method == "POST":
        bp = request.form["buy_platform"]
        cat = request.form["category"]
        name = request.form["name"]
        buy = float(request.form["buy_price"] or 0)
        sell = float(request.form["sell_price"] or 0)
        ship = float(request.form["shipping"] or 0)
        site = request.form["sell_site"]

        fee = sell * SELL_FEES.get(site, 0)
        profit = sell - buy - ship - fee
        rate = round(((sell - fee - ship) / buy) * 100, 1) if buy else 0

        DATA.append({
            "id": str(uuid.uuid4()),
            "buy_platform": bp,
            "category": cat,
            "name": name,
            "buy_date": request.form["buy_date"],
            "sell_date": request.form["sell_date"],
            "buy_price": buy,
            "sell_price": sell,
            "shipping": ship,
            "profit": round(profit,1),
            "rate": rate,
            "sell_site": site
        })
        return redirect("/")

    total_buy = sum(d["buy_price"] for d in DATA)
    total_profit = sum(d["profit"] for d in DATA)

    platforms = list(set(d["buy_platform"] for d in DATA))
    rates = [
        round(
            sum(x["rate"] for x in DATA if x["buy_platform"]==p) /
            max(1,len([x for x in DATA if x["buy_platform"]==p])),1
        )
        for p in platforms
    ]

    sell_pies = {}
    for d in DATA:
        if d["sell_site"]:
            sell_pies.setdefault(d["sell_site"], {}).setdefault(d["category"], []).append(d["rate"])

    formatted = {}
    for s, cats in sell_pies.items():
        total = sum(len(v) for v in cats.values())
        formatted[s] = {
            "labels": list(cats.keys()),
            "ratios": [round(len(v)/total*100,1) for v in cats.values()]
        }

    return render_template_string(
        HTML,
        data=DATA,
        platforms=platforms,
        rates=rates,
        sell_pies=formatted,
        total_buy=round(total_buy,1),
        total_profit=round(total_profit,1)
    )

@app.route("/delete/<id>")
def delete(id):
    global DATA
    DATA = [d for d in DATA if d["id"] != id]
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
