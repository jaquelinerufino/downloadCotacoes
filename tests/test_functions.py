from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from download_cotacoes.config import Settings
from download_cotacoes.quotations import Quotations


@pytest.fixture
def settings(tmp_path: Path) -> Settings:
    return Settings(download_directory=tmp_path)


def test_validate_period_rejects_invalid_values() -> None:
    quotations = Quotations()

    with pytest.raises(ValueError, match="números inteiros"):
        quotations.validate_period("abc", "1")
    with pytest.raises(ValueError, match="entre 1 e 12"):
        quotations.validate_period(2024, 13)


def test_business_dates_excludes_weekends_and_holiday(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FixedDate(date):
        @classmethod
        def today(cls) -> "FixedDate":
            return cls(2024, 1, 10)

    monkeypatch.setattr("download_cotacoes.quotations.date", FixedDate)
    dates = Quotations().business_dates(2024, 1)

    assert date(2024, 1, 1) not in dates
    assert date(2024, 1, 6) not in dates
    assert date(2024, 1, 8) in dates
    assert all(item < date(2024, 1, 10) for item in dates)


def test_read_files_formats_date_and_currency_id(
    settings: Settings, tmp_path: Path
) -> None:
    first = tmp_path / "cotacaoTodasAsMoedas_02012024.csv"
    second = tmp_path / "cotacaoTodasAsMoedas_03012024.csv"
    first.write_text("02012024;1;A;USD;4,80;4,81;1,00;1,00\n", encoding="utf-8")
    second.write_text("03012024;978;B;EUR;5,20;5,21;1,10;1,11\n", encoding="utf-8")

    data = Quotations(settings).read_files([second, first])

    assert list(data["COT_ID"]) == ["001", "978"]
    assert list(data["COT_DATA"]) == ["20240102", "20240103"]
    assert data.loc[0, "COT_COMPRA"] == pytest.approx(4.8)


def test_write_sql_escapes_text_and_converts_missing_values(
    settings: Settings, tmp_path: Path
) -> None:
    data = pd.DataFrame(
        [
            {
                "COT_ID": "001",
                "COT_DATA": "20240102",
                "COT_COMPRA": 4.8,
                "COT_VENDA": float("nan"),
                "COT_COMPRA_USD": 1.0,
                "COT_VENDA_USD": "d'água",
            }
        ]
    )

    target = Quotations(settings).write_sql(data, 2024, 1, tmp_path)
    content = target.read_text(encoding="utf-8")

    assert target.name == "cotacoes_202401.sql"
    assert content.startswith("BEGIN;")
    assert "NULL" in content
    assert "'d''água'" in content
    assert content.endswith("COMMIT;\n")


def test_clear_files_only_removes_selected_csv(tmp_path: Path) -> None:
    selected = tmp_path / "selected.csv"
    unrelated = tmp_path / "unrelated.csv"
    text = tmp_path / "notes.txt"
    selected.touch()
    unrelated.touch()
    text.touch()

    Quotations.clear_files([selected, text])

    assert not selected.exists()
    assert unrelated.exists()
    assert text.exists()
