from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

DATA_FILE = Path("data/football_matches_2024_2025.csv")


EXPECTED_COLUMNS = [
    "competition_code",
    "competition_name",
    "season",
    "match_id",
    "matchday",
    "stage",
    "status",
    "date_utc",
    "referee",
    "referee_id",
    "home_team_id",
    "home_team",
    "away_team_id",
    "away_team",
    "fulltime_home",
    "fulltime_away",
    "halftime_home",
    "halftime_away",
    "goal_difference",
    "total_goals",
    "match_outcome",
    "home_points",
    "away_points",
]


INT_COLUMNS = [
    "match_id",
    "matchday",
    "referee_id",
    "home_team_id",
    "away_team_id",
    "fulltime_home",
    "fulltime_away",
    "halftime_home",
    "halftime_away",
    "goal_difference",
    "total_goals",
    "home_points",
    "away_points",
]


@dataclass
class CheckResult:
    ok: bool
    message: str


def _fail(msg: str) -> CheckResult:
    return CheckResult(False, msg)


def _ok(msg: str) -> CheckResult:
    return CheckResult(True, msg)


def load() -> pd.DataFrame:
    if not DATA_FILE.exists():
        raise FileNotFoundError(f"Missing required file: {DATA_FILE.as_posix()}")
    return pd.read_csv(DATA_FILE)


def check_schema(df: pd.DataFrame) -> list[CheckResult]:
    res: list[CheckResult] = []
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    extra = [c for c in df.columns if c not in EXPECTED_COLUMNS]
    if missing:
        res.append(_fail(f"Missing columns: {missing}"))
    else:
        res.append(_ok("Schema: expected columns present"))

    if extra:
        res.append(_fail(f"Unexpected extra columns: {extra}"))
    else:
        res.append(_ok("Schema: no unexpected columns"))

    return res


def check_types(df: pd.DataFrame) -> list[CheckResult]:
    res: list[CheckResult] = []
    for c in INT_COLUMNS:
        if c not in df.columns:
            continue
        if not pd.api.types.is_integer_dtype(df[c]):
            res.append(_fail(f"Column '{c}' should be integer dtype (got {df[c].dtype})"))
    if not any(not r.ok for r in res):
        res.append(_ok("Types: integer columns are integer dtypes"))
    return res


def check_integrity(df: pd.DataFrame) -> list[CheckResult]:
    res: list[CheckResult] = []

    # Primary key
    if df["match_id"].isna().any():
        res.append(_fail("match_id contains nulls"))
    elif df["match_id"].duplicated().any():
        res.append(_fail(f"match_id has duplicates: {int(df['match_id'].duplicated().sum())}"))
    else:
        res.append(_ok("PK: match_id is unique"))

    # Derived columns
    gd = df["fulltime_home"] - df["fulltime_away"]
    if not (df["goal_difference"] == gd).all():
        bad = (df["goal_difference"] != gd).sum()
        res.append(_fail(f"goal_difference mismatch for {int(bad)} rows"))
    else:
        res.append(_ok("Derived: goal_difference matches FT scores"))

    tg = df["fulltime_home"] + df["fulltime_away"]
    if not (df["total_goals"] == tg).all():
        bad = (df["total_goals"] != tg).sum()
        res.append(_fail(f"total_goals mismatch for {int(bad)} rows"))
    else:
        res.append(_ok("Derived: total_goals matches FT scores"))

    # Outcome + points
    def outcome(h: int, a: int) -> str:
        if h > a:
            return "Home Win"
        if h < a:
            return "Away Win"
        return "Draw"

    computed_outcome = [outcome(h, a) for h, a in zip(df["fulltime_home"], df["fulltime_away"])]
    if not (df["match_outcome"].astype(str).tolist() == computed_outcome):
        res.append(_fail("match_outcome mismatch vs FT scores"))
    else:
        res.append(_ok("Derived: match_outcome matches FT scores"))

    def points(h: int, a: int) -> tuple[int, int]:
        if h > a:
            return 3, 0
        if h < a:
            return 0, 3
        return 1, 1

    hp, ap = zip(*(points(h, a) for h, a in zip(df["fulltime_home"], df["fulltime_away"])))
    if not (df["home_points"].tolist() == list(hp) and df["away_points"].tolist() == list(ap)):
        res.append(_fail("home_points/away_points mismatch vs FT scores"))
    else:
        res.append(_ok("Derived: points match FT scores"))

    # Date parse
    dt = pd.to_datetime(df["date_utc"], errors="coerce", utc=True)
    if dt.isna().any():
        bad = int(dt.isna().sum())
        res.append(_fail(f"date_utc has {bad} unparsable values"))
    else:
        res.append(_ok("date_utc is parseable (UTC)"))

    # Non-negative scores
    score_cols = ["fulltime_home", "fulltime_away", "halftime_home", "halftime_away", "total_goals"]
    for c in score_cols:
        if (df[c] < 0).any():
            res.append(_fail(f"{c} has negative values"))

    return res


def main() -> int:
    df = load()

    checks: list[CheckResult] = []
    checks += check_schema(df)
    checks += check_types(df)
    checks += check_integrity(df)

    failures = [c for c in checks if not c.ok]
    for c in checks:
        prefix = "✅" if c.ok else "❌"
        print(f"{prefix} {c.message}")

    if failures:
        print(f"Validation failed with {len(failures)} issue(s).")
        return 1

    print("✅ Dataset validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
