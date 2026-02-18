import re
from pathlib import Path
from typing import Generator, Literal


def iter_sources(
    source_path: str | Path,
    format: Literal["*", "wav", "mp3", "flac", "ogg", "m4a"] = "*",
) -> Generator[Path, None, None]:

    if not Path(source_path).exists():
        raise ValueError(f"'{source_path}' does not exist")

    if Path(source_path).is_file():
        yield Path(source_path)
    else:
        for source in Path(source_path).glob("*.*"):

            if format == "*":
                format_pattern = r".*\.(wav|mp3|flac|ogg|m4a)$"
            else:
                format_pattern = rf".*\.{format}$"

            if source.is_dir() or source.stem.startswith("."):
                print(f"Skipping directory or hidden file: {source}")
                continue

            if not re.match(format_pattern, source.name, re.IGNORECASE):
                print(f"Skipping file with unsupported format: {source}")
                continue

            yield source
