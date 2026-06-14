#!/usr/bin/env python3
import re
import unicodedata
from pathlib import Path


VIDEO_EXTS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".m4v", ".webm"}


_TRANSLITERATE = str.maketrans('äüõö', 'auoo')

def normalize(text: str) -> str:
    """Keep only [a-z0-9] and spaces; dots become spaces; äüõö transliterated."""
    text = unicodedata.normalize("NFC", text).lower().translate(_TRANSLITERATE)
    out = []
    for c in text:
        if c == '.':
            out.append(' ')
        elif c.isdigit() or ('a' <= c <= 'z'):
            out.append(c)
        else:
            out.append(' ')
    return ' '.join(''.join(out).split())


def parse_truth_line(line: str):
    """
    Expected:
    Estonian title (Year) [English title] {tmdb-12345}
    Estonian title: Subtitle (Year)
    Estonian title
    """
    line = line.strip()
    if not line:
        return None

    m = re.match(r"^(.*?)(?:\s*\((\d{4})\))?(?:\s*\[([^\]]*)\])?(?:\s*\{tmdb-(\d+)\})?\s*$", line)
    if not m:
        raise ValueError(f"Could not parse truth line: {line}")

    estonian = m.group(1).strip()
    english = (m.group(3) or "").strip()
    estonian_match_text = estonian.replace(":", " ")
    return {
        "raw": line,
        "estonian": estonian,
        "english": english,
        "year": m.group(2),
        "tmdb_id": m.group(4),
        "_net": normalize(estonian_match_text),
        "_nen": normalize(english),
    }


def parse_file(path: Path):
    name = path.stem
    years = re.findall(r"(19\d{2}|20\d{2})", name)
    return {
        "path": path,
        "year": years[-1] if years else None,
        "_ntitle": normalize(name),
    }


def _title_match(ntitle, norm_t):
    """True if either string contains the other as a complete word sequence."""
    if not norm_t or not ntitle:
        return False
    if ntitle == norm_t:
        return True
    padded_t = ' ' + norm_t + ' '
    padded_f = ' ' + ntitle + ' '
    return padded_t in padded_f or padded_f in padded_t


def match_file_to_truth(file_info, truth_items):
    """Pick the best-scoring truth item, not just the first one that matches.

    A file's title may be a substring of several truth titles (e.g. "Suur
    Seiklus" inside "Väikese kukepoisi suur seiklus"). An exact title match
    must win over such partial/substring matches regardless of list order,
    with year proximity and length closeness as tie-breakers.
    """
    ntitle = file_info["_ntitle"]
    file_year = int(file_info["year"]) if file_info["year"] else None

    def year_score(truth_year_str):
        if file_year is None or truth_year_str is None:
            return 0
        diff = abs(file_year - int(truth_year_str))
        if diff == 0:
            return 2
        if diff <= 1:
            return 1
        return -1

    best = None
    best_score = None

    for item in truth_items:
        for norm_t in (item["_nen"], item["_net"]):
            if not norm_t or not ntitle:
                continue

            if ntitle == norm_t:
                title_score = 2
            elif _title_match(ntitle, norm_t):
                title_score = 1
            else:
                continue

            score = (title_score, year_score(item["year"]), -abs(len(ntitle) - len(norm_t)))

            if best_score is None or score > best_score:
                best_score = score
                best = item

    if best is None:
        return None

    return {"item": best, "score": best_score[0] / 2.0, "title_score": best_score[0]}


def safe_filename(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', " - ", name).strip()


def truth_filename(item, extension: str) -> str:
    name = item["estonian"]
    if item["year"]:
        name += f" ({item['year']})"
    if item["english"]:
        name += f" [{item['english']}]"
    if item["tmdb_id"]:
        name += f" {{tmdb-{item['tmdb_id']}}}"
    return safe_filename(name) + extension


def load_truth_list(truth_file):
    truth_items = []

    with open(truth_file, "r", encoding="utf-8") as f:
        for line in f:
            parsed = parse_truth_line(line)
            if parsed:
                truth_items.append(parsed)

    return truth_items


def scan_movies(folder, recursive=False):
    folder = Path(folder)

    files = folder.rglob("*") if recursive else folder.iterdir()

    return [
        parse_file(p)
        for p in files
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS
    ]


def build_matches(movie_files, truth_items):
    matched_truth_ids = set()
    matched_files = set()
    matches = []

    for file_info in movie_files:
        match = match_file_to_truth(file_info, truth_items)

        if match:
            truth_index = truth_items.index(match["item"])

            matched_truth_ids.add(truth_index)
            matched_files.add(file_info["path"])

            matches.append((file_info, match))

    missing_truth = [
        item for i, item in enumerate(truth_items)
        if i not in matched_truth_ids
    ]

    extra_files = [
        file_info for file_info in movie_files
        if file_info["path"] not in matched_files
    ]

    return matches, missing_truth, extra_files


def show_status(matches, missing_truth, extra_files):
    print(f"\n{len(matches)} FILE MATCHES")
    print("=" * 80)

    for file_info, match in matches:
        print(
            f"{file_info['path'].name}  ->  "
            f"{match['item']['raw']} "
            f"(score: {match['score']:.2f})"
        )

    print(f"\n{len(missing_truth)} MOVIES MISSING")
    print("=" * 80)

    for item in missing_truth:
        print(item["raw"])

    print(f"\n{len(extra_files)} EXTRA MOVIES")
    print("=" * 80)

    for file_info in extra_files:
        print(file_info["path"].name)


def truth_line_from_file(file_info) -> str:
    return unicodedata.normalize("NFC", file_info["path"].stem).strip()


def offer_add_extra_files_to_truth(extra_files, truth_file):
    if not extra_files:
        return

    lines = [truth_line_from_file(file_info) for file_info in extra_files]

    print(f"\n{len(lines)} FILMI POLE NIMEKIRJAS")
    print("=" * 80)
    for line in lines:
        print(line)

    add_missing = (
        input(f"\nLisa need {len(lines)} filmi nimekirja? (jah/ei): ")
        .strip()
        .lower()
        .startswith("j")
    )

    if not add_missing:
        return

    with open(truth_file, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(f"\n{line}")

    print(f"Lisatud {len(lines)} filmi: {truth_file}")


def build_rename_plan(matches):
    plan = []
    for file_info, match in matches:
        old_path = file_info["path"]
        new_name = truth_filename(match["item"], old_path.suffix)
        if unicodedata.normalize("NFC", old_path.name) != new_name:
            plan.append((old_path, old_path.parent / new_name))
    return plan


def perform_rename(plan):
    for old_path, new_path in plan:
        case_only = old_path.name.lower() == new_path.name.lower()

        if new_path.exists() and not case_only:
            print(f"VAHELE JÄETUD (fail on juba olemas): {old_path.name}")
            print(f"          ->  {new_path.name}")
            continue

        if case_only:
            tmp_path = old_path.with_name(old_path.name + ".__tmp__")
            old_path.rename(tmp_path)
            tmp_path.rename(new_path)
        else:
            old_path.rename(new_path)

        print(f"ÜMBER NIMETATUD: {old_path.name}")
        print(f"             ->  {new_path.name}")


def dry_run_rename(matches):
    plan = build_rename_plan(matches)

    print(f"\nEELVAADE: {len(matches)} FAILI SKANNITUD, {len(plan)} VAJAVAD ÜMBERNIMETAMIST")
    print("=" * 80)

    for old_path, new_path in plan:
        label = "NIMETA ÜMBER (ainult tähed)" if old_path.name.lower() == new_path.name.lower() else "NIMETA ÜMBER"
        print(f"{label}: {old_path.name}")
        print(f"    ->  {new_path.name}")

    if not plan:
        return

    do_rename = (
        input(f"\nNimeta {len(plan)} faili ümber? (jah/ei): ")
        .strip()
        .lower()
        .startswith("j")
    )

    if do_rename:
        perform_rename(plan)


SCRIPT_DIR = Path(__file__).parent

TRUTH_OPTIONS = {
    "1": {
        "label": "Filmid",
        "file": SCRIPT_DIR / "filmid.txt",
        "default_folder": SCRIPT_DIR / ".." / "Eesti Filmid",
        "folder_prompt": "filmide kaust",
    },
    "2": {
        "label": "Multikad",
        "file": SCRIPT_DIR / "multikad.txt",
        "default_folder": SCRIPT_DIR / ".." / "Eesti Multikad",
        "folder_prompt": "multikate kaust",
    },
}


def main():
    print("Vali nimekiri")
    for key, opt in TRUTH_OPTIONS.items():
        print(f"{key}. {opt['label']}")

    lib_choice = input("\n> ").strip()
    if lib_choice not in TRUTH_OPTIONS:
        print("Vale valik")
        return

    selected = TRUTH_OPTIONS[lib_choice]
    truth_file = selected["file"]
    default_folder = selected["default_folder"]

    print(f"\nKus {selected['folder_prompt']} asub? default = [{default_folder.resolve()}]")
    folder_input = input("> ").strip()
    folder = Path(folder_input) if folder_input else default_folder

    print("\nVali (1-2)")
    print("1. Kontrolli hetke seisu")
    print("2. Nimeta failid ümber")

    choice = input("\n> ").strip()

    truth_items = load_truth_list(truth_file)

    if choice == "1":
        print("\nSkannimine...")
        movie_files = scan_movies(folder)
        print(f"Leitud {len(movie_files)} videofaili.")
        print("Võrdlemine nimekirjaga...")
        matches, missing_truth, extra_files = build_matches(movie_files, truth_items)
        show_status(matches, missing_truth, extra_files)

        wrong_name = sum(
            1 for file_info, match in matches
            if unicodedata.normalize("NFC", file_info["path"].name) != truth_filename(match["item"], file_info["path"].suffix)
        )
        print("\n" + "=" * 80)
        print(f"{len(matches)} Filmi olemas")
        print(f"{len(missing_truth)} Filmi puudu")
        print(f"{len(extra_files)} Filmid mis pole nimekirjas")
        print(f"{wrong_name} Filmi mille pealkiri on nimekirjast erinev")
        offer_add_extra_files_to_truth(extra_files, truth_file)

    elif choice == "2":
        print("\nFaili formaat: Eesti pealkiri (Aasta) [English title]")
        print("\nSkannimine...")
        movie_files = scan_movies(folder)
        print(f"Leitud {len(movie_files)} videofaili.")
        print("Võrdlemine nimekirjaga...")
        matches, missing_truth, extra_files = build_matches(movie_files, truth_items)
        dry_run_rename(matches)
        offer_add_extra_files_to_truth(extra_files, truth_file)

    else:
        print("Invalid choice")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
    finally:
        input("\nPress Enter to exit...")
