from pathlib import Path

import pytest

from download_cotacoes.config import Settings


def test_rejects_final_column_not_present_in_csv_columns(tmp_path: Path) -> None:
    settings = Settings(
        download_directory=tmp_path,
        csv_columns=("COT_ID",),
        final_columns=("COT_DATA",),
    )

    with pytest.raises(ValueError, match="COT_DATA"):
        settings.validate()


def test_rejects_invalid_timeout(tmp_path: Path) -> None:
    settings = Settings(download_directory=tmp_path, download_timeout=0)

    with pytest.raises(ValueError, match="DOWNLOAD_TIMEOUT"):
        settings.validate()
