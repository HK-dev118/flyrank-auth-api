import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
ERROR_FILE = BASE_DIR / "output" / "validation_errors.json"
REPORT_FILE = BASE_DIR / "output" / "failure_report.json"


def main() -> None:
    validation_errors = json.loads(
        ERROR_FILE.read_text(encoding="utf-8")
    )

    report = {
        "validation_failures": len(validation_errors),
        "fetch_failures": 0,
        "total_failures": len(validation_errors),
    }

    REPORT_FILE.write_text(
        json.dumps(
            report,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"validation_failures="
        f"{report['validation_failures']}"
    )
    print(
        f"fetch_failures="
        f"{report['fetch_failures']}"
    )
    print(
        f"total_failures="
        f"{report['total_failures']}"
    )
    print(f"saved={REPORT_FILE}")


if __name__ == "__main__":
    main()