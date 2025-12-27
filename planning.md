# 📘 README – Best Practice Penentuan EMA Terbaik

**Pair:** BTCUSDT
**Timeframe:** 1H
**Tujuan:** Menemukan kombinasi EMA Fast/Slow yang **stabil, konsisten, dan robust lintas kondisi market**, bukan sekadar optimal di satu periode.

---

## 1. Prinsip Dasar (Filosofi Metodologi)

1. **No Look-Ahead Bias**
   Seluruh tuning dilakukan hanya pada **data training**.
2. **Out-of-Sample is Sacred**
   Data OOS **tidak boleh disentuh** sampai seluruh parameter final ditetapkan.
3. **Stability > Profit Besar Sesaat**
   Parameter terbaik adalah yang **profit stabil lintas rezim market**, bukan yang PF tertinggi di satu fase.
4. **Regime-Aware Optimization**
   EMA harus diuji di:

   - Bull
   - Bear
   - Sideways
     dengan Low & High Volatility.

5. **Walk-Forward First, Production Later**
   Tidak ada strategi yang langsung production sebelum lolos WFV.

---

## 2. Struktur Dataset Splitting (Wajib)

### 2.1 Static Split

| Bagian        | Porsi | Fungsi                 |
| ------------- | ----- | ---------------------- |
| Training      | 60%   | Tuning EMA & parameter |
| Validation    | 20%   | Filter overfitting     |
| Out of Sample | 20%   | Uji performa final     |

> ⚠️ Validation **bukan** untuk tuning ulang besar-besaran, hanya untuk konfirmasi stabilitas.

---

### 2.2 Walk-Forward Validation (WFV – Final Gate)

| Window | Train | Test |
| ------ | ----- | ---- |
| W1     | 2019  | 2020 |
| W2     | 2020  | 2021 |
| W3     | 2021  | 2022 |

**Kriteria Lolos WFV:**

- Profit Factor > 1.2 di ≥ 2 window
- Max Drawdown tidak meningkat > 30% antar window
- Winrate tidak anjlok ekstrem (> 15% drop)

---

## 3. Definisi Strategi Dasar (EMA Crossover)

### 3.1 Entry Rules

- **BUY:** EMA_fast cross-up EMA_slow
- **SELL:** EMA_fast cross-down EMA_slow

### 3.2 Exit Rules

- Berdasarkan:

  - Opposite crossover, atau
  - Fixed ATR-based stop (opsional untuk versi lanjut)

---

## 4. Proses Tuning EMA (Core Process)

### 4.1 Ruang Pencarian (Search Space)

```text
EMA_fast : 1 – 99
EMA_slow : 2 – 100
Syarat   : EMA_fast < EMA_slow
```

Total kombinasi ≈ 4.851 pasangan.

---

### 4.2 Tuning Awal (Data Training 60%)

Untuk setiap pasangan EMA:
Hitung:

- total_trades
- win_rate
- avg_win
- avg_loss
- profit_factor
- max_drawdown
- final_equity
- pnl_percent

### 4.3 Seleksi Awal

Ambil **Top 5 Kombinasi EMA** berdasarkan:

- PF tertinggi
- PnL% tertinggi
- Drawdown terendah
  (dengan threshold minimal trade count agar tidak noise)

---

## 5. Pembentukan Subset Market Regime

### 5.1 Klasifikasi Trend

Gunakan:

- EMA 200
- Atau slope regression harga

| Kondisi  | Kriteria                  |
| -------- | ------------------------- |
| Bull     | Close > EMA 200           |
| Bear     | Close < EMA 200           |
| Sideways | Deviasi rendah & slope ~0 |

### 5.2 Klasifikasi Volatility

Gunakan:

- ATR
- Atau StdDev return

| Kondisi  | Kriteria     |
| -------- | ------------ |
| High Vol | ATR > median |
| Low Vol  | ATR < median |

### 5.3 Total Subset

1. Bull – High Vol
2. Bear – High Vol
3. Sideways – High Vol
4. Bull – Low Vol
5. Bear – Low Vol
6. Sideways – Low Vol

---

## 6. Retuning di Tiap Subset

Untuk **5 EMA terbaik awal**, lakukan backtest ulang di **setiap subset**:

Output per subset:

- profit_factor
- win_rate
- max_drawdown
- pnl_percent

---

## 7. Analisis Variance (Stability Check)

Hitung variance antar 6 subset untuk:

- profit_factor_variance
- win_rate_variance
- max_drawdown_variance
- pnl_percent_variance

### Interpretasi:

- **Variance kecil → EMA stabil**
- **Variance besar → EMA sensitif rezim**

---

## 8. Analisis Mean Performance

Hitung rata-rata:

- profit_factor_mean
- pnl_percent_mean

Makna:

- **Mean = performa jangka panjang**
- **Variance = kestabilan**

---

## 9. Normalisasi Data

| Kondisi Data       | Metode          |
| ------------------ | --------------- |
| Unextreme Variance | Min-Max Scaling |
| High Outlier       | Z-Score         |

Dilakukan untuk:

- Variance metrics
- Mean metrics

Agar semua metrik berada pada skala sebanding.

---

## 10. Entropy Weighting (Objective Weight)

Entropy digunakan untuk menentukan bobot **berdasarkan informasi aktual data**, bukan subjektif.

Bobot dihitung untuk:

- PF_variance
- WR_variance
- DD_variance
- PNL_variance

Makna:

- Semakin besar variasi data → semakin besar bobot informasinya.

---

## 11. Stability Score

```text
STABILITY_SCORE =
Σ (Metric_variance × Entropy_weight)
```

Komponen:

- PF_var × w1
- WR_var × w2
- DD_var × w3
- PNL_var × w4

Semakin kecil skor → semakin stabil.

---

## 12. Final Scoring & Ranking

```text
FINAL_SCORE =
(STABILITY_SCORE × α)
- (PF_mean × β)
- (PNL_mean × γ)
```

Contoh bobot:

- α = 0.5 (stability)
- β = 0.25 (profit factor)
- γ = 0.25 (profitability)

EMA terbaik = **Final Score Terendah**

---

## 13. Validation Set Check (20%)

Tujuan:

- Deteksi **overfitting tersembunyi**

Syarat lolos:

- PF tidak turun > 20%
- Max DD naik < 25%
- Trade count masih representatif

Jika gagal → buang parameter.

---

## 14. Out-of-Sample Test (20%)

Ini adalah **simulasi real market forward test historis**.

Output final yang dipakai:

- Equity curve
- Max drawdown aktual
- Real winrate
- Real profit factor
- PnL%

⚠️ **Tidak boleh ada retuning setelah melihat hasil OOS.**

---

## 15. Walk-Forward Validation (WFV)

EMA final diuji di:

- 2019 → 2020
- 2020 → 2021
- 2021 → 2022

Kriteria Produksi:

- ≥ 2 dari 3 window profit
- DD tidak eksplosif
- Tidak ada window yang PF < 1 secara ekstrem

---

## 16. Output Akhir yang Wajib Dilaporkan

Setiap EMA final WAJIB disertai:

- EMA_fast, EMA_slow
- PF_train, PF_val, PF_oos
- DD_train, DD_oos
- PnL_train, PnL_oos
- Equity Curve OOS
- Stability Score
- Final Score

---

## 17. Anti-Overfitting Checklist (WAJIB)

- [ ] Tidak tuning di Validation
- [ ] Tidak memilih EMA berdasarkan OOS
- [ ] Subset lengkap 6 kondisi
- [ ] Variance analysis dilakukan
- [ ] WFV minimal 3 window
- [ ] Trade count cukup (≥ 200 trade historis ideal)

---

## 18. Siap Production Jika dan Hanya Jika:

1. Lolos Validation
2. Lolos OOS
3. Lolos ≥ 2 Window WFV
4. Stability Score rendah
5. DD terkendali (< 35–40%)
