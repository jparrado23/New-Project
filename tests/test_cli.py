from typer.testing import CliRunner

from app.main import cli


def test_cli_init_db(tmp_path):
    config_path = tmp_path / "config.yaml"
    db_path = tmp_path / "pipeline.db"
    config_path.write_text(
        "\n".join(
            [
                "subreddits: [stocks]",
                "include_comments: true",
                "database_path: " + str(db_path),
                "report_output_dir: " + str(tmp_path / "reports"),
                "stock_universe_path: data/us_stock_universe.csv",
            ]
        ),
        encoding="utf-8",
    )
    result = CliRunner().invoke(cli, ["init-db", "--config", str(config_path)])
    assert result.exit_code == 0
    assert "Initialized database" in result.stdout
