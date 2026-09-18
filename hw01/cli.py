import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

PROG = "my-wc"
FIELDS = ("lines", "words", "chars", "bytes")
DEFAULT_FIELDS = ("lines", "words", "bytes")


@dataclass
class Counts:
    lines: int = 0
    words: int = 0
    chars: int = 0
    bytes: int = 0

    def __add__(self, other: "Counts") -> "Counts":
        return Counts(
            self.lines + other.lines,
            self.words + other.words,
            self.chars + other.chars,
            self.bytes + other.bytes,
        )


def count(data: bytes) -> Counts:
    text = data.decode("utf-8", errors="replace")
    return Counts(
        lines=data.count(b"\n"),
        words=len(text.split()),
        chars=len(text),
        bytes=len(data),
    )


def read(path: str) -> bytes:
    if path == "-":
        return sys.stdin.buffer.read()
    return Path(path).read_bytes()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog=PROG,
        description="Вывести число строк, слов и байт для каждого файла.",
    )
    parser.add_argument("files", nargs="*", help="файлы; '-' или пусто - stdin")
    parser.add_argument("-l", "--lines", action="store_true", help="число строк")
    parser.add_argument("-w", "--words", action="store_true", help="число слов")
    parser.add_argument("-m", "--chars", action="store_true", help="число символов")
    parser.add_argument("-c", "--bytes", action="store_true", help="число байт")
    return parser


def selected_fields(args: argparse.Namespace) -> tuple[str, ...]:
    chosen = tuple(name for name in FIELDS if getattr(args, name))
    return chosen or DEFAULT_FIELDS


def format_row(counts: Counts, fields: tuple[str, ...], label: str) -> str:
    columns = " ".join(f"{getattr(counts, name):>7}" for name in fields)
    return f"{columns} {label}".rstrip()


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    fields = selected_fields(args)
    paths = args.files or ["-"]
    total = Counts()
    exit_code = 0

    for path in paths:
        try:
            data = read(path)
        except OSError as error:
            print(f"{PROG}: {path}: {error.strerror}", file=sys.stderr)
            exit_code = 1
            continue
        counts = count(data)
        total += counts
        print(format_row(counts, fields, "" if path == "-" else path))

    if len(paths) > 1:
        print(format_row(total, fields, "total"))

    return exit_code
