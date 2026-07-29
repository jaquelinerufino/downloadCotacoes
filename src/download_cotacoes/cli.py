from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from download_cotacoes.config import Settings
from download_cotacoes.quotations import Quotations


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Baixa cotações diárias do Banco Central e gera um arquivo SQL."
    )
    parser.add_argument("--ano", type=int, help="Ano que será processado.")
    parser.add_argument("--mes", type=int, help="Mês que será processado (1 a 12).")
    parser.add_argument(
        "--manter-csv",
        action="store_true",
        help="Não remove os CSVs depois da geração do SQL.",
    )
    parser.add_argument("--verbose", action="store_true", help="Exibe logs detalhados.")
    return parser


def run(
    year: int,
    month: int,
    keep_csv: bool = False,
    settings: Settings | None = None,
) -> Path:
    active_settings = settings or Settings.from_env()
    quotations = Quotations(active_settings)
    dates = quotations.business_dates(year, month)
    if not dates:
        raise ValueError(
            "O período informado não possui dias disponíveis para download."
        )

    downloaded: list[Path] = []
    failures: list[str] = []
    for current_date in dates:
        try:
            downloaded.append(quotations.download(current_date))
        except Exception as exc:
            logging.error("%s", exc)
            failures.append(current_date.strftime("%d/%m/%Y"))

    if failures:
        raise RuntimeError(
            "A execução foi interrompida; os CSVs foram preservados. "
            "Datas com falha: " + ", ".join(failures)
        )

    data = quotations.read_files(downloaded)
    sql_path = quotations.write_sql(data, year, month)
    if not keep_csv:
        quotations.clear_files(downloaded)
    return sql_path


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    year = args.ano if args.ano is not None else input("Insira o ano: ").strip()
    month = args.mes if args.mes is not None else input("Insira o mês: ").strip()

    try:
        sql_path = run(year, month, args.manter_csv)
    except (ValueError, RuntimeError) as exc:
        logging.error("%s", exc)
        return 1
    except Exception:
        logging.exception("Falha inesperada durante a execução.")
        return 1

    logging.info("Processamento concluído. SQL gerado em: %s", sql_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
