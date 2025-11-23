# 🧩 Backtest Strategy – Trading Bot Binance

## 📚 Strategy 1 — EMA Cross

Strategi ini menggunakan sinyal persilangan dua Exponential Moving Average (EMA) untuk menentukan arah entry dan exit.

### 📌 Aturan Strategi

1. **BUY** → ketika **EMA 13 cross ke atas EMA 21**  
   _Artinya momentum harga mulai bullish._

2. **SELL** → ketika **EMA 13 cross ke bawah EMA 21**  
   _Artinya momentum harga mulai bearish._

## 📚 Strategy 2 — Multi Timeframe EMA Filter

Konsep:

1. Menggunakan EMA 13/21 di timeframe rendah (1h) untuk entry.
2. Menggunakan EMA 50/100 di timeframe menengah (4h) dan tinggi (1d) untuk trend filter.
3. Hanya entry jika sinyal 1h searah dengan trend 4h/1d.
4. Strategi ini bertujuan mengurangi false signal dan mengikuti tren utama.

### 📌 Aturan Strategi

1. **Trend Filter - Higher Timeframe (1d, 4h, 1w)**

- Daily (1d)

  - Trend Bullish → EMA50 > EMA100
  - Trend Bearish → EMA50 < EMA100

- 4H (optional)

  - Trend Bullish → EMA50 > EMA100
  - Trend Bearish → EMA50 < EMA100

2. **Entry – Lower Timeframe (1h)**

- BUY → EMA13_1h cross EMA21_1h ke atas dan trend di 1d/4h bullish
- SELL → EMA13_1h cross EMA21_1h ke bawah dan trend di 1d/4h bearish

## 📚 Strategy 3 — RSI

Strategi ini menggunakan Relative Strength Index (RSI) untuk menentukan kondisi overbought atau oversold dan mengatur entry/exit.

### 📌 Aturan Strategi

- BUY → ketika RSI berada di bawah level oversold (default: 30)
- SELL → ketika RSI berada di atas level overbought (default: 70)

## 📚 Strategy 4 — Bollinger Bands

Strategi ini menggunakan Bollinger Bands untuk menentukan area overbought dan oversold sebagai dasar entry dan exit.

### 📌 Aturan Strategi

- BUY close sebelumnya > BB_lower dan close sekarang < BB_lower
- SELL close sebelumnya < BB_upper dan close sekarang > BB_upper

## 📚 Strategy 5 — Stochastic Oscillator

Strategi ini menggunakan **Stochastic Oscillator** untuk mengidentifikasi kondisi **overbought** dan **oversold** sebagai sinyal entry dan exit.

### 📌 Aturan Strategi

- **BUY** → ketika **%K cross ke atas %D** di area oversold (biasanya < 20)
  - `%K` sebelumnya < `%D` sebelumnya & `%K` sekarang > `%D` sekarang, `%K` < 20
- **SELL** → ketika **%K cross ke bawah %D** di area overbought (biasanya > 80)
  - `%K` sebelumnya > `%D` sebelumnya & `%K` sekarang < `%D` sekarang, `%K` > 80

# 📚 Strategy 6 — MACD

Strategi ini menggunakan **MACD (Moving Average Convergence Divergence)** untuk menentukan sinyal entry dan exit.

---

## 📌 Indikator

- **MACD Line** → selisih antara EMA cepat dan EMA lambat
- **Signal Line** → EMA dari MACD Line

Default parameter:

- EMA cepat: 12 periode
- EMA lambat: 26 periode
- Signal EMA: 9 periode

---

## 📌 Aturan Strategi

1. **BUY** → ketika **MACD Line cross ke atas Signal Line**
2. **SELL** → ketika **MACD Line cross ke bawah Signal Line**

---

## 📌 Langkah Implementasi

1. Hitung **EMA cepat** dan **EMA lambat** dari harga penutupan.
2. Hitung **MACD Line** = EMA cepat − EMA lambat.
3. Hitung **Signal Line** = EMA dari MACD Line.
4. Tentukan sinyal:
   - Buy → MACD Line baru > Signal Line dan sebelumnya < Signal Line
   - Sell → MACD Line baru < Signal Line dan sebelumnya > Signal Line

---

## 📌 Catatan

- Pastikan data sudah **urut berdasarkan waktu**.
- Gunakan `.shift(1)` untuk mengecek cross dari bar sebelumnya.
- Bisa digabung dengan **filter trend timeframe lebih tinggi** untuk mengurangi sinyal palsu.

# 📚 Strategy 7 — Scalping 1H

## Grid Opportunistic + MACD Confirmation + Swing Context

Scalping 1H berbasis grid opportunistic yang aktif hanya setelah kecenderungan rally–retracement, menggunakan MACD histogram sebagai konfirmasi momentum untuk entry dan exit dengan target profit kecil berulang.

---

## 📌 Indikator

- MACD (12, 26, 9)

  - Fokus pada Histogram dan perubahan slope (Histogram.diff()).

- Swing Structure

  - Deteksi HL/HH untuk memastikan harga berada di fase post-rally retracement.

- ATR (Average True Range)

  - Filter volatilitas (hindari entry ketika ATR terlalu rendah atau terlalu tinggi).

- Dynamic Grid

---

## 📌 Aturan Strategi

**1. Kondisi Aktif (Menyalakan Grid)**

- BTC baru selesai rally → mulai masuk retracement kecil.

- Struktur membentuk Higher Low (HL) 1H yang valid.

- Histogram MACD mengecil tapi tidak negatif (momentum melemah namun belum bearish).

- ATR berada pada rentang normal (tidak terlalu sempit/ekstrem).

**2. Aturan Entry (Buy)**

- Entry terjadi saat Histogram.diff() > 0 (histogram kembali menguat).

- Buy menggunakan grid:

- Level 1: -0.25%

- Level 2: -0.50%

- Level 3: -0.75%

- Level 4: -1.00% (opsional)

- Tiap buy: 18–25% dari modal 70 USDT.

- Entry hanya saat harga berada di zona HL (post-rally compression).

---

**3. EXIT RULE — INITIATOR (Kapan exit pertama kali terpikirkan)**

Exit segera berlaku bila salah satu terjadi:

- (1) HL break (hard exit utama)

  - Close 1H di bawah swing low terakhir
  - Bukan wick, tapi close
  - Ini artinya swing structure invalid.
  - Wajib exit.

- (2) MACD momentum failure

  - Histogram < 0 ATAU Histogram.diff() < 0 selama 3 candle berturut-turut
  - Ini artinya momentum bull gagal.

- (3) ATR meledak keluar rentang normal
  - ATR saat ini > 1.5 × ATR median 14
  - → volatilitas abnormal, optimisasi grid gagal → exit

**4. EXIT RULE — EXECUTION (Cara keluar yang benar)**

- ✔ Jika grid belum lengkap (misal baru terisi level 1–2)

  - → Jual semua posisi di candle yang trigger exit.

- ✔ Jika grid penuh

  - → Jual seluruh posisi sekaligus (market sell).

- ✔ Jika Anda ingin lebih halus (opsional):
  - Gunakan limit pada harga current candle low (untuk slippage minimal)
  - Kalau tidak kena → market sell.
