import argparse
import csv
import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


# Liste volontairement compacte et robuste pour FR (oral/ecrit)
FUNCTION_WORDS = [
    "je", "tu", "il", "elle", "on", "nous", "vous", "ils", "elles",
    "me", "te", "se", "moi", "toi", "lui", "leur", "leurs",
    "ce", "cet", "cette", "ces", "ça", "cela", "c", "ca",
    "le", "la", "les", "un", "une", "des", "du", "de", "d",
    "au", "aux", "en", "dans", "sur", "sous", "chez", "par", "pour",
    "avec", "sans", "entre", "vers", "contre", "avant", "apres", "après",
    "et", "ou", "mais", "donc", "or", "ni", "car",
    "que", "qu", "qui", "quoi", "dont", "où", "ou",
    "si", "comme", "quand", "lorsque", "puisque", "parce", "afin",
    "ne", "pas", "plus", "moins", "jamais", "toujours", "rien", "tout",
    "tous", "toute", "toutes", "aucun", "aucune",
    "être", "etre", "avoir", "faire", "aller", "venir", "dire", "voir",
]

DISCOURSE_MARKERS = [
    "en fait", "je pense", "je pense que", "donc", "cependant", "en revanche",
    "d'ailleurs", "alors", "du coup", "finalement", "au fond", "en somme",
    "eh bien", "bon", "voilà", "en tout cas", "or", "ainsi", "par ailleurs",
]

WORD_RE = re.compile(r"[a-zàâäéèêëîïôöùûüÿçœæ']+", flags=re.IGNORECASE)
SENT_SPLIT_RE = re.compile(r"[.!?]+")


def normalize_min(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower()
    text = re.sub(r"[’‘´`]", "'", text)
    text = re.sub(r"[–—−]", "-", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize_words(text: str) -> List[str]:
    return WORD_RE.findall(text)


def split_sentences(text: str) -> List[str]:
    chunks = [s.strip() for s in SENT_SPLIT_RE.split(text) if s.strip()]
    return chunks


def iter_char_ngrams(text: str, n_values: Iterable[int]) -> Iterable[str]:
    text = re.sub(r"\s+", " ", text)
    for n in n_values:
        if len(text) < n:
            continue
        for i in range(len(text) - n + 1):
            yield text[i : i + n]


def load_segments(path: Path, corpus_label: str) -> List[Dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    segments: List[Dict[str, str]] = []

    # Format 1: {"books": {"name": ["bloc1", ...]}}
    if isinstance(data.get("books"), dict):
        for book_name, blocks in data["books"].items():
            if not isinstance(blocks, list):
                continue
            for i, block in enumerate(blocks):
                if isinstance(block, str) and block.strip():
                    segments.append(
                        {
                            "corpus": corpus_label,
                            "source_file": path.name,
                            "source": data.get("source", ""),
                            "subsource": book_name,
                            "segment_id": f"{book_name}_{i}",
                            "text": block,
                        }
                    )

    # Format 2: {"blocks": ["bloc1", ...]}
    if isinstance(data.get("blocks"), list):
        for i, block in enumerate(data["blocks"]):
            if isinstance(block, str) and block.strip():
                segments.append(
                    {
                        "corpus": corpus_label,
                        "source_file": path.name,
                        "source": data.get("source", ""),
                        "subsource": "blocks",
                        "segment_id": f"blocks_{i}",
                        "text": block,
                    }
                )

    # Format 3 (si besoin plus tard): {"chapters": [{"paragraphs": [...]}]}
    if isinstance(data.get("chapters"), list):
        for chap in data["chapters"]:
            chap_id = chap.get("id", "na")
            paragraphs = chap.get("paragraphs", [])
            if isinstance(paragraphs, list):
                text = " ".join(p for p in paragraphs if isinstance(p, str))
                if text.strip():
                    segments.append(
                        {
                            "corpus": corpus_label,
                            "source_file": path.name,
                            "source": data.get("source", ""),
                            "subsource": f"chapter_{chap_id}",
                            "segment_id": f"chapter_{chap_id}",
                            "text": text,
                        }
                    )

    return segments


def compute_sentence_stats(text: str, short_threshold: int) -> Tuple[float, float, float, int]:
    sentences = split_sentences(text)
    if not sentences:
        return 0.0, 0.0, 0.0, 0
    lengths = [len(tokenize_words(s)) for s in sentences]
    lengths = [x for x in lengths if x > 0]
    if not lengths:
        return 0.0, 0.0, 0.0, len(sentences)
    mean_len = statistics.fmean(lengths)
    var_len = statistics.pvariance(lengths) if len(lengths) > 1 else 0.0
    short_ratio = sum(1 for x in lengths if x <= short_threshold) / len(lengths)
    return mean_len, var_len, short_ratio, len(lengths)


def top_char_ngram_vocab(texts: List[str], n_values: Iterable[int], top_k: int) -> List[str]:
    counts = Counter()
    for text in texts:
        counts.update(iter_char_ngrams(text, n_values))
    return [ng for ng, _ in counts.most_common(top_k)]


def rel_freq(count: int, total: int) -> float:
    return (count / total) if total > 0 else 0.0


def main() -> None:
    parser = argparse.ArgumentParser(description="Extraction de traits stylométriques (étape 5).")
    parser.add_argument(
        "--input",
        action="append",
        required=True,
        help="Entrée au format LABEL=/chemin/fichier.json, ex: E=data/blocks2/blocks_livres_bardella.json",
    )
    parser.add_argument("--output-dir", default="data/features", help="Dossier de sortie")
    parser.add_argument("--top-k-char-ngrams", type=int, default=500, help="Taille du vocabulaire char n-grammes")
    parser.add_argument("--short-sentence-threshold", type=int, default=8, help="Seuil phrase courte en nb de mots")
    parser.add_argument("--normalize", action="store_true", help="Appliquer une normalisation légère avant extraction")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    all_segments: List[Dict[str, str]] = []
    for item in args.input:
        if "=" not in item:
            raise ValueError(f"Entrée invalide: {item}. Format attendu LABEL=path")
        label, raw_path = item.split("=", 1)
        path = Path(raw_path)
        segs = load_segments(path, corpus_label=label)
        all_segments.extend(segs)

    if not all_segments:
        raise ValueError("Aucun segment trouvé dans les entrées.")

    for seg in all_segments:
        t = seg["text"]
        seg["text_norm"] = normalize_min(t) if args.normalize else t

    vocab = top_char_ngram_vocab(
        [seg["text_norm"] for seg in all_segments], n_values=(3, 4), top_k=args.top_k_char_ngrams
    )
    vocab_set = set(vocab)

    summary_by_corpus = Counter(seg["corpus"] for seg in all_segments)

    handcrafted_rows: List[Dict[str, object]] = []
    char_ngram_rows: List[Dict[str, object]] = []

    for seg in all_segments:
        text = seg["text_norm"]
        words = tokenize_words(text)
        total_words = len(words)
        total_chars = len(text)
        word_counts = Counter(words)
        mean_len, var_len, short_ratio, sentence_count = compute_sentence_stats(
            text, short_threshold=args.short_sentence_threshold
        )

        marker_counts = {}
        for marker in DISCOURSE_MARKERS:
            marker_counts[marker] = len(re.findall(r"\b" + re.escape(marker) + r"\b", text))

        row = {
            "corpus": seg["corpus"],
            "source_file": seg["source_file"],
            "source": seg["source"],
            "subsource": seg["subsource"],
            "segment_id": seg["segment_id"],
            "total_words": total_words,
            "total_chars": total_chars,
            "sentence_count": sentence_count,
            "avg_sentence_len_words": mean_len,
            "var_sentence_len_words": var_len,
            "short_sentence_ratio": short_ratio,
        }

        for fw in FUNCTION_WORDS:
            row[f"fw::{fw}"] = rel_freq(word_counts.get(fw, 0), total_words)

        for marker, cnt in marker_counts.items():
            row[f"dm::{marker}"] = rel_freq(cnt, sentence_count)

        handcrafted_rows.append(row)

        ngram_counts = Counter(iter_char_ngrams(text, (3, 4)))
        total_ngrams = sum(ngram_counts.values())
        ngram_row = {
            "corpus": seg["corpus"],
            "source_file": seg["source_file"],
            "source": seg["source"],
            "subsource": seg["subsource"],
            "segment_id": seg["segment_id"],
        }
        for ng in vocab:
            ngram_row[f"cng::{ng}"] = rel_freq(ngram_counts.get(ng, 0), total_ngrams)

        char_ngram_rows.append(ngram_row)

    handcrafted_path = output_dir / "features_handcrafted.csv"
    char_ngrams_path = output_dir / "features_char_ngrams.csv"
    vocab_path = output_dir / "char_ngram_vocabulary.json"
    manifest_path = output_dir / "manifest_features.json"

    handcrafted_fields = list(handcrafted_rows[0].keys())
    with handcrafted_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=handcrafted_fields)
        writer.writeheader()
        writer.writerows(handcrafted_rows)

    char_fields = list(char_ngram_rows[0].keys())
    with char_ngrams_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=char_fields)
        writer.writeheader()
        writer.writerows(char_ngram_rows)

    vocab_path.write_text(json.dumps(vocab, ensure_ascii=False, indent=2), encoding="utf-8")

    manifest = {
        "n_segments": len(all_segments),
        "segments_by_corpus": dict(summary_by_corpus),
        "top_k_char_ngrams": args.top_k_char_ngrams,
        "short_sentence_threshold": args.short_sentence_threshold,
        "normalize": bool(args.normalize),
        "files": {
            "handcrafted": str(handcrafted_path),
            "char_ngrams": str(char_ngrams_path),
            "vocabulary": str(vocab_path),
        },
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"OK: {len(all_segments)} segments traités")
    print(f"Corpus: {dict(summary_by_corpus)}")
    print(f"Sorties: {handcrafted_path}, {char_ngrams_path}, {vocab_path}, {manifest_path}")


if __name__ == "__main__":
    main()
