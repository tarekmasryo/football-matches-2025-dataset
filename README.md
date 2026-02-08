# ⚽ Football Matches 2024/2025 (Top Leagues + UCL)

Clean match-level dataset: **1,941 matches** across **6 competitions** (Top 5 leagues + Champions League), with FT/HT scores and derived features (goal difference, total goals, outcome, points).

- **Main file:** `data/football_matches_2024_2025.csv` (1 row per match)
- **Data dictionary:** `docs/data_dictionary.md`
- **Example notebook:** `examples/quick_analysis.ipynb`

---

## 📦 Columns (23)

Competition: `competition_code`, `competition_name`, `season`, `stage`, `matchday`  
Match: `match_id`, `date_utc`, `status`, `referee`, `referee_id`  
Teams: `home_team_id`, `home_team`, `away_team_id`, `away_team`  
Scores: `fulltime_home`, `fulltime_away`, `halftime_home`, `halftime_away`  
Derived: `goal_difference`, `total_goals`, `match_outcome`, `home_points`, `away_points`

---

## 🚀 Quick start (pandas)

```python
import pandas as pd

df = pd.read_csv("data/football_matches_2024_2025.csv")
print(df.shape)
print(df[["competition_name", "home_team", "away_team", "fulltime_home", "fulltime_away"]].head())
```

---

## ✅ Data quality (reproducible)

```bash
python scripts/validate_dataset.py
python scripts/make_checksums.py --check
```

Generate checksums (after any data update):

```bash
python scripts/make_checksums.py
```

---

## 🧾 Source & attribution

Data is collected via **football-data.org**.
Please include: **"Football data provided by the Football-Data.org API"**.  
See `football-data.org.txt` for notes.

---

## 📜 License

Repository license: **CC BY 4.0** (see `LICENSE`).
