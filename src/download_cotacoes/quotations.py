from __future__ import annotations

import logging
import math
import time
from collections.abc import Iterable, Sequence
from datetime import date, datetime
from pathlib import Path

import pandas as pd

from download_cotacoes.config import Settings

LOGGER = logging.getLogger(__name__)


class Quotations:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings

    @staticmethod
    def validate_period(year: int | str, month: int | str) -> tuple[int, int]:
        try:
            parsed_year = int(year)
            parsed_month = int(month)
        except (TypeError, ValueError) as exc:
            raise ValueError("Ano e mês devem ser números inteiros.") from exc

        if parsed_year < 1900:
            raise ValueError("O ano deve ser igual ou posterior a 1900.")
        if parsed_month not in range(1, 13):
            raise ValueError("O mês deve estar entre 1 e 12.")

        today = date.today()
        if (parsed_year, parsed_month) > (today.year, today.month):
            raise ValueError("Não é possível baixar cotações de um mês futuro.")
        return parsed_year, parsed_month

    def business_dates(self, year: int | str, month: int | str) -> list[date]:
        import calendar

        import holidays

        parsed_year, parsed_month = self.validate_period(year, month)
        today = date.today()
        brazilian_holidays = holidays.BR(years=[parsed_year])
        result: list[date] = []

        for day in range(1, calendar.monthrange(parsed_year, parsed_month)[1] + 1):
            current = date(parsed_year, parsed_month, day)
            if (
                current < today
                and current.weekday() < 5
                and current not in brazilian_holidays
            ):
                result.append(current)
        return result

    # Compatibilidade com a interface original.
    def validatingDates(self, year: int | str, month: int | str) -> tuple[bool, str]:
        try:
            self.validate_period(year, month)
        except ValueError as exc:
            return True, f"Erro: {exc}"
        return False, ""

    def removeInvalidDates(
        self, year: int | str, month: int | str, error: bool = False
    ) -> list[date]:
        return [] if error else self.business_dates(year, month)

    def _settings(self) -> Settings:
        if self.settings is None:
            self.settings = Settings.from_env()
        return self.settings

    def download(self, quotation_date: date, directory: Path | None = None) -> Path:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.edge.options import Options
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.support.ui import WebDriverWait

        settings = self._settings()
        target_directory = (directory or settings.download_directory).resolve()
        target_directory.mkdir(parents=True, exist_ok=True)
        date_text = quotation_date.strftime("%d%m%Y")
        target = target_directory / f"{settings.csv_file_prefix}{date_text}.csv"

        if target.exists() and target.stat().st_size > 0:
            LOGGER.info("Arquivo já existente, download ignorado: %s", target.name)
            return target

        last_error: Exception | None = None
        for attempt in range(1, settings.download_retries + 2):
            driver = None
            try:
                options = Options()
                for argument in settings.edge_arguments:
                    options.add_argument(argument)
                options.add_experimental_option(
                    "prefs", {"download.default_directory": str(target_directory)}
                )
                driver = webdriver.Edge(options=options)
                wait = WebDriverWait(driver, 15)
                driver.get(
                    "https://www.bcb.gov.br/estabilidadefinanceira/historicocotacoes"
                )

                cookie_buttons = driver.find_elements(
                    By.XPATH, "//button[contains(., 'Aceitar')]"
                )
                if cookie_buttons:
                    cookie_buttons[-1].click()

                wait.until(
                    EC.frame_to_be_available_and_switch_to_it(
                        (By.CSS_SELECTOR, "iframe")
                    )
                )
                wait.until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//input[@type='radio'][@value='2']")
                    )
                ).click()
                date_input = wait.until(
                    EC.presence_of_element_located((By.ID, "DATAINI"))
                )
                date_input.clear()
                date_input.send_keys(date_text)
                wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='submit']"))
                ).click()
                wait.until(
                    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, "CSV"))
                ).click()

                deadline = time.monotonic() + settings.download_timeout
                while time.monotonic() < deadline:
                    partial_downloads = list(target_directory.glob("*.crdownload"))
                    download_finished = (
                        target.exists()
                        and target.stat().st_size > 0
                        and not partial_downloads
                    )
                    if download_finished:
                        LOGGER.info("Download concluído: %s", target.name)
                        return target
                    time.sleep(0.5)
                raise TimeoutError(
                    f"O arquivo {target.name} não foi concluído em "
                    f"{settings.download_timeout} segundos."
                )
            except Exception as exc:
                last_error = exc
                LOGGER.warning(
                    "Tentativa %s de download de %s falhou: %s",
                    attempt,
                    date_text,
                    exc,
                )
            finally:
                if driver is not None:
                    driver.quit()

        raise RuntimeError(
            f"Não foi possível baixar a cotação de {quotation_date:%d/%m/%Y}."
        ) from last_error

    def downloads(self, date_text: str, directory: str) -> tuple[bool, str]:
        try:
            quotation_date = datetime.strptime(date_text, "%d%m%Y").date()
            path = self.download(quotation_date, Path(directory))
        except Exception as exc:
            return True, f"Ocorreu um erro com a data {date_text}: {exc}"
        return False, f"Dados do dia {date_text} salvos com sucesso em {path}"

    def read_files(self, files: Sequence[Path]) -> pd.DataFrame:
        settings = self._settings()
        if not files:
            raise ValueError("Nenhum arquivo CSV foi informado.")

        frames = [
            pd.read_csv(
                file,
                sep=";",
                decimal=",",
                names=list(settings.csv_columns),
                dtype={"COT_DATA": "string", "COT_ID": "string"},
            )
            for file in sorted(files)
        ]
        data = pd.concat(frames, ignore_index=True)

        data["COT_DATA"] = pd.to_datetime(
            data["COT_DATA"], format="%d%m%Y", errors="raise"
        ).dt.strftime("%Y%m%d")
        data["COT_ID"] = data["COT_ID"].str.zfill(3)
        return data.loc[:, list(settings.final_columns)]

    def readFiles(self, directory: str) -> pd.DataFrame:
        return self.read_files(list(Path(directory).glob("*.csv")))

    @staticmethod
    def _sql_literal(value: object) -> str:
        if value is None or pd.isna(value):
            return "NULL"
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if isinstance(value, float) and not math.isfinite(value):
                return "NULL"
            return str(value)
        escaped = str(value).replace("'", "''")
        return f"'{escaped}'"

    def write_sql(
        self,
        data: pd.DataFrame,
        year: int | str,
        month: int | str,
        directory: Path | None = None,
    ) -> Path:
        settings = self._settings()
        parsed_year, parsed_month = self.validate_period(year, month)
        if data.empty:
            raise ValueError("Não há registros para gerar o arquivo SQL.")

        target_directory = (directory or settings.download_directory).resolve()
        target_directory.mkdir(parents=True, exist_ok=True)
        target = target_directory / (
            f"{settings.sql_file_prefix}{parsed_year}{parsed_month:02d}.sql"
        )
        columns = ", ".join(data.columns)
        statements = []
        for row in data.itertuples(index=False, name=None):
            values = ", ".join(self._sql_literal(value) for value in row)
            statements.append(
                f"INSERT INTO {settings.table} ({columns}) VALUES ({values});"
            )

        content = "BEGIN;\n\n" + "\n".join(statements) + "\n\nCOMMIT;\n"
        target.write_text(content, encoding="utf-8")
        LOGGER.info("%s registros gravados em %s", len(data), target)
        return target

    def writeSQL(
        self,
        data: pd.DataFrame,
        year: int | str,
        month: int | str,
        directory: str | None = None,
    ) -> Path:
        return self.write_sql(
            data, year, month, Path(directory) if directory is not None else None
        )

    @staticmethod
    def clear_files(files: Iterable[Path]) -> None:
        for file in files:
            path = Path(file)
            if path.is_file() and path.suffix.lower() == ".csv":
                path.unlink()
                LOGGER.info("Arquivo temporário removido: %s", path)

    def clearFiles(self, directory: str, files: Iterable[Path] | None = None) -> None:
        selected = (
            files
            if files is not None
            else Path(directory).glob(f"{self._settings().csv_file_prefix}*.csv")
        )
        self.clear_files(selected)


cotacoes = Quotations()
