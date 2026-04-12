import logging
from datetime import datetime
from pathlib import Path
from typing import Annotated

import duckdb
import typer


# command for typer app
def shrink_duckdb_command(
    input_file: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to the input DuckDB file",
            exists=True,
            file_okay=True,
            dir_okay=False,
            readable=True,
        ),
    ],
    output_file: Annotated[
        Path | None,
        typer.Option(
            "--output",
            "-o",
            help="Path to the output DuckDB file "
            "(default: next to input with '_small' suffix)",
            file_okay=True,
            dir_okay=False,
        ),
    ] = None,
    schemas: Annotated[
        list[str],
        typer.Option(
            "--schema",
            "-s",
            help="Schema(s) to include in the minimized database "
            "(can be specified multiple times)",
        ),
    ] = [],
):
    """Shrink a DuckDB file by keeping only tables from specified schemas."""
    shrink_duckdb(input_file, output_file, schemas)

# function that can be used in orchestration workflows
def shrink_duckdb(
    input_file: Path,
    output_file: Path | None,
    schemas: list[str],
    log: logging.Logger | None = None,
):
    """Shrink a DuckDB file by keeping only tables from specified schemas."""

    if log is None:
        log = logging.getLogger("lf_py_stack.duckdb")

    # Determine output file path
    if output_file is None:
        output_file = input_file.parent / f"{input_file.stem}_small{input_file.suffix}"

    log.info(f"Minimizing DuckDB file: {input_file}")
    log.info(f"Output file: {output_file}")
    log.info(f"Schemas to copy: {', '.join(schemas)}")

    # Check if output file already exists
    if output_file.exists():
        log.warning(
            f"Output file {output_file} already exists and will be overwritten."
        )
        output_file.unlink()

    try:
        _copy_tables_to_new_db(input_file, output_file, schemas, log=log)

        # Report file sizes
        input_size = input_file.stat().st_size / (1024 * 1024)  # MB
        output_size = output_file.stat().st_size / (1024 * 1024)  # MB
        reduction = ((input_size - output_size) / input_size) * 100

        log.info(f"Input size: {input_size:.1f} MB")
        log.info(f"Output size: {output_size:.1f} MB")
        log.info(f"Size reduction: {reduction:.1f}%")

    except Exception as e:
        # Clean up partial output file
        if output_file.exists():
            output_file.unlink()
        raise e


def _copy_tables_to_new_db(
    source_path: Path,
    target_path: Path,
    schemas_to_copy: list[str],
    log: logging.Logger,
) -> None:
    """
    Copy tables from specified schemas to a new DuckDB file.

    Args:
        source_path: Path to source DuckDB file
        target_path: Path to target DuckDB file
        schemas_to_copy: List of schema names to copy
    """

    start_time = datetime.now()
    log.debug(f"Opening source database: {source_path}")

    with duckdb.connect(str(source_path), read_only=True) as source_conn:
        # Get available schemas
        available_schemas = [
            row[0]
            for row in source_conn.execute(
                "SELECT schema_name FROM information_schema.schemata"
            ).fetchall()
        ]
        log.debug(f"Available schemas: {', '.join(available_schemas)}")

        # Filter schemas that actually exist
        valid_schemas = [s for s in schemas_to_copy if s in available_schemas]
        invalid_schemas = [s for s in schemas_to_copy if s not in available_schemas]

        if invalid_schemas:
            log.warning(
                f"Schemas not found in source database: {', '.join(invalid_schemas)}"
            )

        if not valid_schemas:
            log.error(
                f"No valid schemas found to copy! Candidates:"
                f"{', '.join(available_schemas)}"
            )
            log.info("Try the --schema option with one of the available schemas!")
            raise typer.Exit(code=1)

        log.debug(f"Creating target database: {target_path}")
        with duckdb.connect(str(target_path)) as target_conn:
            total_tables_copied = 0

            for schema in valid_schemas:
                tables = [
                    row[0]
                    for row in source_conn.execute(
                        "SELECT table_name FROM information_schema.tables "
                        "WHERE table_schema = ?",
                        [schema],
                    ).fetchall()
                ]

                if len(tables) == 0:
                    log.info(f"No tables found in schema '{schema}'")
                    continue
                else:
                    log.debug(
                        f"Found {len(tables)} tables in schema '{schema}': "
                        f"{', '.join(tables)}"
                    )

                target_conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                for table in tables:
                    log.info(f"Copying table: {schema}.{table}")
                    target_conn.execute(
                        f"ATTACH '{source_path}' AS source_db (READ_ONLY)"
                    )
                    target_conn.execute(
                        f"CREATE TABLE {schema}.{table} AS SELECT * "
                        f"FROM source_db.{schema}.{table}"
                    )
                    target_conn.execute("DETACH source_db")
                    total_tables_copied += 1

            # target_conn.close()
        # source_conn.close()
    dt = datetime.now() - start_time
    log.info(
        f"Copied {total_tables_copied} tables from "
        f"{len(valid_schemas)} schemas in {dt.total_seconds():.1f} seconds"
    )

