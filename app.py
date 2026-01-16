from flask import Flask, render_template_string, request, redirect, jsonify
import uuid
import json

app = Flask(__name__)

# データを永続化するためのファイル
DATA_FILE = 'data.json'

def save_data():
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(DATA, f, ensure_ascii=False, indent=2)

def load_data():
    global DATA
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            DATA = json.load(f)
    except FileNotFoundError:
        DATA = []

# 初期データ読み込み
load_data()

SELL_FEES = {
    "ラクマ": 0.10,
    "ヤフーフリマ": 0.05,
    "メルカリ": 0.10
}

# カテゴリカラー設定
CATEGORY_COLORS = {
    "ガチャ": "#ff6b6b",
    "ステッカー": "#4ecdc4",
    "服": "#45b7d1",
    "文房具": "#96ceb4",
    "雑貨": "#feca57"
}

# プラットフォームカラー設定
PLATFORM_COLORS = {
    "お店": "#a55eea",
    "SHEIN": "#fd79a8",
    "TEMU": "#fdcb6e",
    "アリエク": "#e17055",
    "百均": "#00b894"
}

HTML = """
<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>フリマ損益管理</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<link rel="apple-touch-icon" href="/static/apple-touch-icon.png">
<style>
* {
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", sans-serif;
    background: #fff0f6;
    margin: 0;
    padding: 16px;
    line-height: 1.4;
}

.container {
    display: flex;
    gap: 20px;
    max-width: 1400px;
    margin: 0 auto;
}

.sidebar {
    width: 320px;
    flex-shrink: 0;
}

.main {
    flex: 1;
    min-width: 0;
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
    font-size: 18px;
}

select, input, button {
    width: 100%;
    border-radius: 16px;
    padding: 12px;
    border: 1px solid #f3c1d9;
    margin-bottom: 10px;
    font-size: 16px;
}

select:focus, input:focus {
    outline: none;
    border-color: #ff6fae;
    box-shadow: 0 0 0 2px rgba(255, 111, 174, 0.2);
}

button {
    background: #ff6fae;
    color: white;
    border: none;
    cursor: pointer;
    font-weight: bold;
}

button:hover {
    background: #e65a9c;
}

button.secondary {
    background: #6c757d;
}

button.secondary:hover {
    background: #5a6268;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
}

th, td {
    border-bottom: 1px solid #f8d7e8;
    padding: 8px 4px;
    text-align: center;
    vertical-align: middle;
}

th {
    background: #fff5f9;
    color: #c2255c;
    font-weight: bold;
    position: sticky;
    top: 0;
    z-index: 10;
}

tbody tr:hover {
    background: #fff9fc;
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
    font-weight: bold;
}

.delete {
    cursor: pointer;
    font-size: 20px;
    color: #dc3545;
}

.delete:hover {
    color: #c82333;
}

.edit {
    cursor: pointer;
    font-size: 16px;
    color: #007bff;
    margin-right: 5px;
}

.edit:hover {
    color: #0056b3;
}

canvas {
    width: 100% !important;
    max-height: 400px;
}

/* タグのスタイル */
.tag-group {
    display: flex;
    gap: 4px;
    flex-wrap: wrap;
    justify-content: center;
}

.tag {
    padding: 2px 6px;
    border-radius: 12px;
    font-size: 11px;
    color: white;
    font-weight: bold;
    white-space: nowrap;
}

.platform-tag {
    background: var(--platform-color, #6c757d);
}

.category-tag {
    background: var(--category-color, #28a745);
}

.sell-site-tag {
    background: #17a2b8;
}

.status-tag {
    font-size: 10px;
    padding: 1px 4px;
    border-radius: 8px;
}

.status-sold {
    background: #28a745;
}

.status-unsold {
    background: #ffc107;
    color: #212529;
}

.status-reserved {
    background: #fd7e14;
}

/* 商品名のスタイル */
.product-name {
    max-width: 120px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    cursor: pointer;
    position: relative;
    font-weight: bold;
}

.product-name:hover {
    background: #fff5f9;
    border-radius: 4px;
    padding: 2px;
    margin: -2px;
}

.product-name.expanded {
    white-space: normal;
    overflow: visible;
    text-overflow: clip;
    background: white;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-radius: 4px;
    padding: 4px;
    z-index: 100;
    max-width: 200px;
}

/* 日付のスタイル */
.date-cell {
    font-size: 12px;
    color: #6c757d;
}

/* 金額のスタイル */
.price-cell {
    font-weight: bold;
}

.profit-positive {
    color: #28a745;
}

.profit-negative {
    color: #dc3545;
}

/* レスポンシブ対応 */
@media (max-width: 1200px) {
    .container {
        flex-direction: column;
    }
    
    .sidebar {
        width: 100%;
        max-width: 500px;
        margin: 0 auto;
    }
    
    .main {
        width: 100%;
    }
    
    table {
        font-size: 12px;
    }
    
    th, td {
        padding: 6px 2px;
    }
    
    .product-name {
        max-width: 80px;
    }
}

@media (max-width: 768px) {
    body {
        padding: 8px;
    }
    
    .container {
        gap: 12px;
    }
    
    form, table, .card {
        padding: 12px;
        border-radius: 16px;
    }
    
    h2 {
        font-size: 16px;
    }
    
    select, input, button {
        font-size: 14px;
        padding: 10px;
    }
    
    /* 横スクロール対応 */
    .table-wrapper {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin: 0 -8px;
        padding: 0 8px;
    }
    
    table {
        min-width: 900px;
        margin: 0;
    }
    
    .summary {
        font-size: 16px;
    }
    
    .product-name {
        max-width: 100px;
    }
    
    .tag {
        font-size: 10px;
        padding: 1px 4px;
    }
}

@media (max-width: 480px) {
    .product-name {
        max-width: 80px;
    }
    
    .date-cell {
        font-size: 11px;
    }
}

/* グラフのレスポンシブ対応 */
.card {
    margin-bottom: 16px;
}

@media (max-width: 768px) {
    .card canvas {
        max-height: 300px;
    }
}

/* プレースホルダーのスタイル */
::placeholder {
    color: #adb5bd;
    opacity: 1;
}

:-ms-input-placeholder {
    color: #adb5bd;
}

::-ms-input-placeholder {
    color: #adb5bd;
}

/* 編集フォームのスタイル */
.edit-form {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 15px;
    margin: 10px 0;
}

.edit-form h3 {
    margin-top: 0;
    color: #495057;
}

.edit-form .form-row {
    display: flex;
    gap: 10px;
    margin-bottom: 10px;
}

.edit-form .form-row > * {
    flex: 1;
    margin-bottom: 0;
}

@media (max-width: 768px) {
    .edit-form .form-row {
        flex-direction: column;
        gap: 5px;
    }
}
</style>
</head>
<body>

<div class="container">

<div class="sidebar">
<h2>商品登録</h2>
<form method="post" action="/add">
<select name="buy_platform" required>
<option value="">購入先を選択</option>
<option>お店</option><option>SHEIN</option><option>TEMU</option>
<option>アリエク</option><option>百均</option>
</select>

<select name="category" required>
<option value="">分類を選択</option>
<option>ガチャ</option><option>ステッカー</option><option>服</option>
<option>文房具</option><option>雑貨</option>
</select>

<input name="name" placeholder="商品名（例：アニメステッカーセット）" required>
<input type="date" name="buy_date" placeholder="購入日">
<input type="date" name="sell_date" placeholder="販売日">

<input name="buy_price" type="number" step="0.01" placeholder="仕入価格（例：400）" required>
<input name="sell_price" type="number" step="0.01" placeholder="販売価格（例：500）">
<input name="shipping" type="number" step="0.01" placeholder="送料（例：80）">

<select name="sell_site">
<option value="">販売状況</option>
<option>ラクマ</option><option>ヤフーフリマ</option><option>メルカリ</option>
</select>

<button type="submit">商品を追加</button>
</form>
</div>

<div class="main">
<h2>商品一覧</h2>
<div class="table-wrapper">
<table>
<thead>
<tr>
<th>購入先</th>
<th>分類</th>
<th>商品名</th>
<th>販売状況</th>
<th>購入日</th>
<th>売却日</th>
<th>仕入価格</th>
<th>販売価格</th>
<th>送料</th>
<th>手数料</th>
<th>利益</th>
<th>利益率</th>
<th></th>
</tr>
</thead>
<tbody>
{% for d in data %}
<tr>
<td>
<span class="tag platform-tag" style="--platform-color: {{ platform_colors.get(d.buy_platform, '#6c757d') }}">
{{ d.buy_platform }}
</span>
</td>
<td>
<span class="tag category-tag" style="--category-color: {{ category_colors.get(d.category, '#28a745') }}">
{{ d.category }}
</span>
</td>
<td>
<div class="product-name" onclick="toggleProductName(this)" title="{{ d.name }}">
{{ d.name }}
</div>
</td>
<td>
{% if d.sell_site %}
<span class="tag status-tag status-sold">売却済</span>
{% else %}
<span class="tag status-tag status-unsold">未売</span>
{% endif %}
</td>
<td class="date-cell">{{ d.buy_date or '-' }}</td>
<td class="date-cell">{{ d.sell_date or '-' }}</td>
<td class="price-cell">¥{{ "{:,.0f}".format(d.buy_price) }}</td>
<td class="price-cell">{{ "¥{:,.0f}".format(d.sell_price) if d.sell_price else '-' }}</td>
<td class="price-cell">{{ "¥{:,.0f}".format(d.shipping) if d.shipping else '-' }}</td>
<td class="price-cell">{{ "¥{:,.0f}".format(d.fee) if d.fee else '-' }}</td>
<td class="price-cell {{ 'profit-positive' if d.profit >= 0 else 'profit-negative' }}">
¥{{ "{:,.0f}".format(d.profit) }}
</td>
<td class="{{ 'profit-positive' if d.profit >= 0 else 'profit-negative' }}">
{{ d.rate }}%
</td>
<td>
<span class="edit" onclick="editItem('{{ d.id }}')" title="編集">✏️</span>
<span class="delete" onclick="if(confirm('削除してもよろしいですか？')) location.href='/delete/{{ d.id }}'" title="削除">🗑</span>
</td>
</tr>
{% endfor %}
</tbody>
<tfoot>
<tr>
<td colspan="6">合計</td>
<td class="price-cell">¥{{ "{:,.0f}".format(total_buy) }}</td>
<td class="price-cell">¥{{ "{:,.0f}".format(total_sell) }}</td>
<td class="price-cell">¥{{ "{:,.0f}".format(total_shipping) }}</td>
<td class="price-cell">¥{{ "{:,.0f}".format(total_fee) }}</td>
<td class="price-cell {{ 'profit-positive' if total_profit >= 0 else 'profit-negative' }}">
¥{{ "{:,.0f}".format(total_profit) }}
</td>
<td colspan="2"></td>
</tr>
</tfoot>
</table>
</div>

<div class="summary">
総利益: ¥{{ "{:,.0f}".format(total_profit) }}
</div>

<!-- 編集フォーム（非表示） -->
<div id="editForm" class="edit-form" style="display: none;">
<h3>商品情報編集</h3>
<form id="editFormContent" method="post" action="/edit">
<input type="hidden" id="edit_id" name="id">

<div class="form-row">
<select id="edit_sell_site" name="sell_site" required>
<option value="">販売状況</option>
<option value="">未売却</option>
<option>ラクマ</option><option>ヤフーフリマ</option><option>メルカリ</option>
</select>

<input type="date" id="edit_sell_date" name="sell_date">

<input type="number" id="edit_sell_price" name="sell_price" step="0.01" placeholder="販売価格">
</div>

<div class="form-row">
<input type="number" id="edit_shipping" name="shipping" step="0.01" placeholder="送料">

<button type="submit">更新</button>
<button type="button" onclick="cancelEdit()" class="secondary">キャンセル</button>
</div>
</form>
</div>

<div class="card">
<h2>購入元別 平均利益率</h2>
<canvas id="bar"></canvas>
</div>

<div class="card">
<h2>販売サイト別 商品分類</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;">
{% for site, pdata in sell_pies.items() %}
<div style="text-align: center;">
<h4>{{ site }}</h4>
<canvas id="sell_{{ loop.index }}" style="max-width: 300px; margin: 0 auto;"></canvas>
</div>
{% endfor %}
</div>
</div>

</div>
</div>

<script>
// 商品名の展開/収縮
function toggleProductName(element) {
    element.classList.toggle('expanded');
}

// 編集フォーム表示
function editItem(id) {
    // 該当するデータを見つける
    const row = event.target.closest('tr');
    const cells = row.getElementsByTagName('td');
    
    // フォームに値を設定
    document.getElementById('edit_id').value = id;
    
    // 販売状況を取得して設定
    const sellSiteElement = cells[0].querySelector('.sell-site-tag');
    if (sellSiteElement) {
        document.getElementById('edit_sell_site').value = sellSiteElement.textContent;
    } else {
        document.getElementById('edit_sell_site').value = '';
    }
    
    // フォームを表示
    document.getElementById('editForm').style.display = 'block';
    document.getElementById('edit_sell_site').focus();
}

// 編集キャンセル
function cancelEdit() {
    document.getElementById('editForm').style.display = 'none';
    document.getElementById('editFormContent').reset();
}

// グラフの描画
new Chart(document.getElementById("bar"),{
    type:"bar",
    data:{
        labels: {{ platforms|safe }},
        datasets:[{
            label:"平均利益率（％）",
            data: {{ rates|safe }},
            backgroundColor:["#ff6fae","#ffb3d9","#ffc0cb","#f783ac","#faa2c1"]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    callback: function(value) {
                        return value + '%';
                    }
                }
            }
        }
    }
});

{% for site, pdata in sell_pies.items() %}
new Chart(document.getElementById("sell_{{ loop.index }}"),{
    type:"pie",
    data:{
        labels: {{ pdata.labels|safe }},
        datasets:[{
            data: {{ pdata.ratios|safe }},
            backgroundColor:["#ff6fae","#ffb3d9","#ffc0cb","#f783ac","#faa2c1"]
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'bottom',
                labels: {
                    fontSize: 12
                }
            }
        }
    }
});
{% endfor %}
</script>

</body>
</html>
"""

@app.route("/", methods=["GET"])
def index():
    total_buy = sum(d["buy_price"] for d in DATA)
    total_sell = sum(d["sell_price"] for d in DATA)
    total_shipping = sum(d["shipping"] for d in DATA)
    total_fee = sum(d["fee"] for d in DATA)
    total_profit = sum(d["profit"] for d in DATA)

    platforms = list(set(d["buy_platform"] for d in DATA))
    rates = []
    for p in platforms:
        platform_data = [x for x in DATA if x["buy_platform"] == p]
        if platform_data:
            avg_rate = sum(x["rate"] for x in platform_data) / len(platform_data)
            rates.append(round(avg_rate, 1))
        else:
            rates.append(0)

    sell_pies = {}
    for d in DATA:
        if d["sell_site"]:
            sell_pies.setdefault(d["sell_site"], {}).setdefault(d["category"], []).append(d["rate"])

    formatted = {}
    for s, cats in sell_pies.items():
        total = sum(len(v) for v in cats.values())
        if total > 0:
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
        total_buy=total_buy,
        total_sell=total_sell,
        total_shipping=total_shipping,
        total_fee=total_fee,
        total_profit=total_profit,
        platform_colors=PLATFORM_COLORS,
        category_colors=CATEGORY_COLORS
    )

@app.route("/add", methods=["POST"])
def add():
    bp = request.form["buy_platform"]
    cat = request.form["category"]
    name = request.form["name"]
    buy = float(request.form["buy_price"] or 0)
    sell = float(request.form["sell_price"] or 0)
    ship = float(request.form["shipping"] or 0)
    site = request.form["sell_site"]

    # 手数料計算
    fee = sell * SELL_FEES.get(site, 0) if sell > 0 else 0
    # 利益計算（販売価格 - 仕入価格 - 送料 - 手数料）
    profit = sell - buy - ship - fee
    # 利益率計算（利益 / 仕入価格 × 100）
    rate = round((profit / buy) * 100, 1) if buy > 0 else 0

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
        "fee": round(fee, 1),
        "profit": round(profit, 1),
        "rate": rate,
        "sell_site": site
    })
    
    save_data()
    return redirect("/")

@app.route("/edit", methods=["POST"])
def edit():
    item_id = request.form["id"]
    
    # 該当アイテムを見つける
    for item in DATA:
        if item["id"] == item_id:
            # 販売情報を更新
            sell_site = request.form["sell_site"]
            sell_date = request.form["sell_date"]
            sell_price = float(request.form["sell_price"] or 0)
            shipping = float(request.form["shipping"] or 0)
            
            # 手数料再計算
            fee = sell_price * SELL_FEES.get(sell_site, 0) if sell_price > 0 else 0
            
            # 利益再計算
            profit = sell_price - item["buy_price"] - shipping - fee
            rate = round((profit / item["buy_price"]) * 100, 1) if item["buy_price"] > 0 else 0
            
            # データ更新
            item["sell_site"] = sell_site
            item["sell_date"] = sell_date
            item["sell_price"] = sell_price
            item["shipping"] = shipping
            item["fee"] = round(fee, 1)
            item["profit"] = round(profit, 1)
            item["rate"] = rate
            
            break
    
    save_data()
    return redirect("/")

@app.route("/delete/<id>")
def delete(id):
    global DATA
    DATA = [d for d in DATA if d["id"] != id]
    save_data()
    return redirect("/")

# iOSアイコン用のルート
@app.route("/apple-touch-icon.png")
def ios_icon():
    try:
        return app.send_static_file("apple-touch-icon.png")
    except:
        return "", 404

if __name__ == "__main__":
    # staticフォルダの作成
    import os
    if not os.path.exists('static'):
        os.makedirs('static')
    
    app.run(debug=True, host='0.0.0.0', port=5000)