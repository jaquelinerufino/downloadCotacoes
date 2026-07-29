from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from environs import Env

DEFAULT_COLUMNS = (
    "COT_DATA",
    "COT_ID",
    "TIPO",
    "MOEDA",
    "COT_COMPRA",
    "COT_VENDA",
    "COT_COMPRA_USD",
    "COT_VENDA_USD",
)
DEFAULT_FINAL_COLUMNS = (
    "COT_ID",
    "COT_DATA",
    "COT_COMPRA",
    "COT_VENDA",
    "COT_COMPRA_USD",
    "COT_VENDA_USD",
)


@dataclass(frozen=True)
class Settings:
    download_directory: Path
    table: str = "tp_master.dbo.I_COTACOES"
    sql_file_prefix: str = "cotacoes_"
    csv_file_prefix: str = "cotacaoTodasAsMoedas_"
    edge_arguments: tuple[str, ...] = ("--headless=new",)
    csv_columns: tuple[str, ...] = DEFAULT_COLUMNS
    final_columns: tuple[str, ...] = DEFAULT_FINAL_COLUMNS
    download_timeout: int = 60
    download_retries: int = 2

    @classmethod
    def from_env(cls) -> Settings:
        env = Env()
        env.read_env()

        directory = Path(env.str("DEF_DIRECTORY", "./downloads")).expanduser().resolve()
        edge_arguments = tuple(
            argument.strip()
            for argument in env.list("EDGE_ARGUMENTS", ["--headless=new"])
            if argument.strip()
        )

        settings = cls(
            download_directory=directory,
            table=env.str("TABLE", "tp_master.dbo.I_COTACOES"),
            sql_file_prefix=env.str("FILE_NAME", "cotacoes_"),
            csv_file_prefix=env.str("CSV_FILE_NAME", "cotacaoTodasAsMoedas_"),
            edge_arguments=edge_arguments,
            csv_columns=tuple(env.list("DF_COLUMNS", list(DEFAULT_COLUMNS))),
            final_columns=tuple(env.list("FINAL_COLUMNS", list(DEFAULT_FINAL_COLUMNS))),
            download_timeout=env.int("DOWNLOAD_TIMEOUT", 60),
            download_retries=env.int("DOWNLOAD_RETRIES", 2),
        )
        settings.validate()
        settings.download_directory.mkdir(parents=True, exist_ok=True)
        return settings

    def validate(self) -> None:
        if self.download_timeout <= 0:
            raise ValueError("DOWNLOAD_TIMEOUT deve ser maior que zero.")
        if self.download_retries < 0:
            raise ValueError("DOWNLOAD_RETRIES não pode ser negativo.")
        if not self.csv_columns:
            raise ValueError("DF_COLUMNS não pode ficar vazio.")
        missing = set(self.final_columns) - set(self.csv_columns)
        if missing:
            raise ValueError(
                "FINAL_COLUMNS contém colunas ausentes em DF_COLUMNS: "
                + ", ".join(sorted(missing))
            )
        if not self.table.strip():
            raise ValueError("TABLE não pode ficar vazio.")
