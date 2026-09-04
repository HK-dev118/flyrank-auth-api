import json
import re
from pathlib import Path

from pydantic import ValidationError

from models import BookRecord


BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "output" / "raw_books.json"
OUTPUT_FILE = BASE_DIR / "output" / "books.json"
ERROR_FILE = BASE_DIR / "output" / "validation_errors.json"


def normalize_price(price_text: str) -> float:
    """
    Convert values such as '£51.77' or 'Â£51.77' to 51.77.
    """

    match = re.search(r"(\d+(?:\.\d{1,2})?)", price_text)

    if not match:
        raise ValueError(f"Could not parse price: {price_text}")

    return float(match.group(1))


def normalize_record(raw_record: dict) -> dict:
    record = dict(raw_record)
    record["price_gbp"] = normalize_price(record["price_text"])
    return record


def main() -> None:
    raw_records = json.loads(
        INPUT_FILE.read_text(encoding="utf-8")
    )

    valid_records = []
    validation_errors = []

    for index, raw_record in enumerate(raw_records, start=1):
        try:
            normalized = normalize_record(raw_record)
            validated = BookRecord.model_validate(normalized)
            valid_records.append(
                validated.model_dump(mode="json")
            )

        except (ValueError, ValidationError) as exc:
            validation_errors.append(
                {
                    "record_index": index,
                    "error": str(exc),
                    "record": raw_record,
                }
            )

    OUTPUT_FILE.write_text(
        json.dumps(
            valid_records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    ERROR_FILE.write_text(
        json.dumps(
            validation_errors,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(f"raw_records={len(raw_records)}")
    print(f"valid_records={len(valid_records)}")
    print(f"validation_errors={len(validation_errors)}")
    print(f"saved={OUTPUT_FILE}")
    print(f"errors_saved={ERROR_FILE}")


if __name__ == "__main__":
    main()