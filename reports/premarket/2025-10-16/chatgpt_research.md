# Nightly Trading Research Report — For Trading Day **2025‑10‑14**

**Order Type:** **LIMIT (DAY)**  |  **Data Anchor:** After‑hours (Oct 13; fallback = 4:00 PM close)  |  **Mode:** Deep Research

> **Assumptions:** After‑hours anchors are used where live quotes are unavailable in this environment. Please verify levels at the open; auto‑trim logic applies if any name gaps **>10%**.

---

## 📧 Email‑Style Summary
- **Shorgan‑Bot:** **GKOS** (Epioxa PDUFA **Oct 20**) and **SNDX** (Revumenib PDUFA **Oct 25**) are top event longs; **ARQT** is a post‑event, reduced‑size follow‑through trade.  
- **Dee‑Bot:** **WMT / COST / MRK / JNJ / PG** provide low‑beta ballast; a **light SPY overlay** targets **β ≈ 1.0**.  
- **AH movers flagged (>5%):** *None* at the generation snapshot.

---

## 🧾 Position Sizing Adjustments Log (AH >10% → auto‑trim 50%)
| Ticker | Original Size | Adjusted Size | Reason |
|---|---:|---:|---|
| *None* | — | — | No >10% AH gaps at generation snapshot |

---

## 📊 Summary Trade Table (LIMIT DAY; ≤15% ADV; spreads <5%)
| Strategy | Ticker | Direction | Entry (anchor) | Stop | Target | Sizing | Catalyst / Rationale |
|---|---|---|---:|---:|---:|---:|---|
| Shorgan‑Bot | **ARQT** | Long (post‑event) | 19.80 | 17.50 | 23.00 | **2%** | **PDUFA Oct 13** approved (Zoryve pediatric); manage post‑gap risk with smaller size. |
| Shorgan‑Bot | **GKOS** | Long | 83.00 | 75.00 | 100.00 | **5%** | **PDUFA Oct 20** (Epioxa; epi‑on CXL) + **Q3 10/29 (AMC)**; adoption tailwind. |
| Shorgan‑Bot | **SNDX** | Long | 15.50 | 13.50 | 20.00 | **5%** | **PDUFA Oct 25** (Revumenib; menin inhibitor); NCCN visibility; asymmetric event RR. |
| Shorgan‑Bot | **RKLB** | Long | 48.00 | 43.00 | 56.00 | **4%** | **Launch window opens Oct 14 (UTC)**; backlog/missions cadence supportive. |
| Shorgan‑Bot | **ACAD** | Long | 16.40 | 14.75 | 20.50 | **4%** | **Q3 11/05 (AMC)**; Nuplazid+Daybue ramps; sentiment improving. |
| Dee‑Bot | **WMT** | Long | 160.00 | 150.00 | 175.00 | **8%** | Grocery share + e‑comm growth; resilient comps; low beta ballast. |
| Dee‑Bot | **COST** | Long | 915.00 | 850.00 | 1000.00 | **8%** | Membership annuity; fee‑hike optionality; steady FCF. |
| Dee‑Bot | **MRK** | Long | 90.00 | 82.00 | 100.00 | **8%** | Keytruda engine + diversified pipeline; low beta stabilizer. |
| Dee‑Bot | **JNJ** | Long | 190.00 | 178.00 | 200.00 | **7%** | Med‑tech/pharma mix; AAA balance sheet; dividend anchor. |
| Dee‑Bot | **PG** | Long | 147.00 | 140.00 | 155.00 | **7%** | Staples pricing power; margin resilience. |
| Dee‑Bot | **SPY (overlay)** | **Long Index** | mkt | n/a | n/a | **15–25%** | Dial portfolio **β → ≈1.0** if drift ≥0.15; scale dynamically. |

---

## 🔍 Deep Research Snapshot (Concise)

### Shorgan‑Bot (Catalyst 1–30d; defined‑risk options if liquid)
- **ARQT (post‑event):** Pediatric eczema label cleared at FDA (Oct 13). Early formulary & prescriber uptake are next milestones; keep risk small until post‑gap price stabilizes.  
- **GKOS:** FDA **PDUFA Oct 20** for **Epioxa™** (epi‑on CXL). Epi‑on convenience vs. epi‑off may drive faster adoption; **Q3 10/29 (AMC)** adds read‑through. *Alt‑data:* job postings/commercial build‑out.  
- **SNDX:** **Revumenib** sNDA **PDUFA Oct 25** (R/R mNPM1 AML). NCCN AML references observed; review under RTOR. *Alt‑data:* field MSL postings hint launch prep.  
- **RKLB:** **Launch window opens 10/14 (UTC)** (Synspective mission); next ER est. mid‑Nov; watch mission status / customer backlog updates.  
- **ACAD:** **Q3 11/05 (AMC)**; Nuplazid plus Daybue ramps; search interest steady; watch script data proxies.

### Dee‑Bot (Defensive S&P 100; β ≈ 1.0)
- **WMT:** U.S. comps ahead of peers; e‑comm + grocery mix cushion; **β ~0.55–0.70**.  
- **COST:** Membership renewal >90%; fee‑hike optionality; steady unit expansion; **β ~0.75–0.95**.  
- **MRK:** Oncology/vaccines cash flows; value vs. market multiple; **β ~0.35–0.45**.  
- **JNJ:** Med‑tech+pharma; litigation overhang easing; **β ~0.35–0.45**.  
- **PG:** Branded staples with pricing power; **β ~0.35–0.45**.  
- **SPY overlay:** add **15–25%** notional to bring aggregate **β** ~1.0; adjust only if drift ≥0.15.

---

## 🧪 Scenario Sketches (per name)
- **Event‑Upbeat:** Approval/beat/launch success → take partials at first target; trail stops to prior day low.  
- **Base:** No surprise → keep stops; hold through second‑day confirmation; reassess target if volume confirms.  
- **Event‑Adverse:** CRL/miss/launch failure → exit on stop; **do not** average down around binary events.

---

## 🧠 Risk & Liquidity Controls
- **Each order ≤ 15% ADV**, **spreads < 5%** at time of entry.  
- **Stops mandatory** on all longs; for any Shorgan shorts, set **buy‑stops** above swing highs.  
- **Gap rule:** if **>10% AH** before open → **auto‑trim 50%**, log in Adjustments.  
- **Execution:** **LIMIT (DAY)**; stagger entries; never chase.

---

*Prepared in Deep Research Mode; data anchored to after‑hours (Oct 13) or prior close where necessary.*
