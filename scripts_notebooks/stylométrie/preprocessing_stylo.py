import re
import unicodedata
from typing import List


# --------------------------------------------------
# 4.1 NORMALISATION
# --------------------------------------------------

def normalize_text(text: str) -> str:
    """
    Normalisation légère et réversible.
    - minuscules
    - apostrophes, tirets, espaces normalisés
    - pas de modification lexicale
    """
    if not text:
        return ""

    # Unicode canonique
    text = unicodedata.normalize("NFKC", text)

    # Minuscules
    text = text.lower()

    # Apostrophes et guillemets
    text = re.sub(r"[’‘´`]", "'", text)
    text = re.sub(r"[“”«»]", '"', text)

    # Tirets
    text = re.sub(r"[–—−]", "-", text)

    # Espaces multiples
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def remove_long_quotes(
    text: str,
    min_words: int = 40
) -> str:
    """
    Supprime les citations longues (ex. blocs entre guillemets)
    pour éviter le bruit intertextuel.
    """
    def _filter(match):
        content = match.group(1)
        if len(content.split()) >= min_words:
            return ""
        return match.group(0)

    # Citations entre guillemets
    text = re.sub(r'"([^"]+)"', _filter, text)

    return text.strip()


# --------------------------------------------------
# 4.2 NETTOYAGE CONTRÔLÉ
# --------------------------------------------------

def neutralize_proper_names(
    text: str,
    blacklist: List[str],
    token: str = "__PN__"
) -> str:
    """
    Neutralise (remplace) des noms propres thématiques
    sans supprimer la structure syntaxique.
    
    Ex :
    "Macron a déclaré" → "__PN__ a déclaré"
    """
    if not blacklist:
        return text

    for name in blacklist:
        pattern = r"\b" + re.escape(name.lower()) + r"\b"
        text = re.sub(pattern, token, text)

    return text


def clean_text(
    text: str,
    proper_names: List[str] = None,
    remove_quotes: bool = True
) -> str:
    """
    Pipeline de nettoyage contrôlé :
    - normalisation
    - suppression citations longues
    - neutralisation noms propres
    """
    text = normalize_text(text)

    if remove_quotes:
        text = remove_long_quotes(text)

    if proper_names:
        text = neutralize_proper_names(text, proper_names)

    return text


# --------------------------------------------------
# UTILITAIRE POUR CORPUS
# --------------------------------------------------

def preprocess_corpus(
    texts: List[str],
    proper_names: List[str] = None
) -> List[str]:
    """
    Applique le même prétraitement à un corpus entier.
    """
    return [
        clean_text(t, proper_names=proper_names)
        for t in texts
        if t and t.strip()
    ]