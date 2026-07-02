import logging
from pathlib import Path

import duckdb
import pytest

from lf_py_stack.orchestration.duckdb import shrink_duckdb


def _init_source_db(path: Path) -> None:
    with duckdb.connect(str(path)) as con:
        con.execute("CREATE SCHEMA IF NOT EXISTS keep")
        con.execute("CREATE TABLE keep.t1 AS SELECT 1 AS id, 'x' AS val")
        con.execute("CREATE TABLE keep.t2_backup AS SELECT 2 AS id, 'y' AS val")
        con.execute("CREATE SCHEMA IF NOT EXISTS dropme")
        con.execute("CREATE TABLE dropme.t3 AS SELECT 3 AS id, 'z' AS val")


def test_shrink_duckdb_copies_only_selected_schema(tmp_path: Path) -> None:
    src = tmp_path / "source.duckdb"
    dst = tmp_path / "small.duckdb"
    _init_source_db(src)

    shrink_duckdb(src, dst, ["keep"], log=logging.getLogger("test"))

    assert dst.exists()
    with duckdb.connect(str(dst), read_only=True) as con:
        schemas = {
            row[0]
            for row in con.execute(
                "SELECT schema_name FROM information_schema.schemata"
            ).fetchall()
        }
        assert "keep" in schemas

        keep_tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='keep'"
        ).fetchall()
        assert ("t1",) in keep_tables

        drop_tables = con.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='dropme'"
        ).fetchall()
        assert drop_tables == []


def test_shrink_duckdb_raises_for_missing_schemas(tmp_path: Path) -> None:
    src = tmp_path / "source.duckdb"
    dst = tmp_path / "small.duckdb"
    _init_source_db(src)

    with pytest.raises(ValueError, match="No valid schemas found to copy"):
        shrink_duckdb(src, dst, ["does_not_exist"], log=logging.getLogger("test"))

    assert not dst.exists()


def test_shrink_duckdb_excludes_tables_matching_pattern(tmp_path: Path) -> None:
    src = tmp_path / "source.duckdb"
    dst = tmp_path / "small.duckdb"
    _init_source_db(src)

    shrink_duckdb(
        src,
        dst,
        ["keep"],
        exclude_table_name_pattern=r".*_backup",
        log=logging.getLogger("test"),
    )

    assert dst.exists()
    with duckdb.connect(str(dst), read_only=True) as con:
        keep_tables = {
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='keep'"
            ).fetchall()
        }
        assert "t1" in keep_tables
        assert "t2_backup" not in keep_tables

    # dropme should still be absent
    with duckdb.connect(str(dst), read_only=True) as con:
        drop_tables = {
            row[0]
            for row in con.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema='dropme'"
            ).fetchall()
        }
        assert len(drop_tables) == 0
