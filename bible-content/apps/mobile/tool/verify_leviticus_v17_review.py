import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BOOK_PATH = ROOT / "apps/mobile/assets/bibles/rv1909/books/LEV.json"
LAYER_PATH = ROOT / "apps/mobile/assets/bible_direction/leviticus_reading_2026.rv1909.v1.json"
CHANGE_SET_PATH = ROOT / "editorial-changes/v17.json"
REGISTRY_PATH = ROOT / "editorial-review/registry.json"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    book = load(BOOK_PATH)
    layer = load(LAYER_PATH)
    change_set = load(CHANGE_SET_PATH)
    registry = load(REGISTRY_PATH)
    source = {
        (chapter["chapter"], verse["verse"]): verse["text"]
        for chapter in book["chapters"]
        for verse in chapter["verses"]
    }
    assert len(source) == 859
    assert change_set["contentVersion"] == 17
    assert len(change_set["changes"]) == 455
    assert len(change_set["pendingReview"]) == 23
    assert layer["ownerReview"] == {
        "contentVersion": 17,
        "changeSet": "editorial-changes/v17.json",
        "appliedEditCount": 455,
    }

    for change in change_set["changes"]:
        ref = (change["chapter"], change["verse"])
        assert ref in source
        assert source[ref].count(change["expected"]) == 1, (ref, change["expected"])
        assert change["expected"] != change["replacement"]
        assert change["reason"].strip()
        assert len(change["evidence"]) >= 2

    rendered = dict(source)
    for verse in layer["verses"]:
        ref = (verse["chapter"], verse["verse"])
        text = source[ref]
        prior_end = len(text) + 1
        for edit in sorted(verse["edits"], key=lambda value: value["startOffset"], reverse=True):
            start, end = edit["startOffset"], edit["endOffset"]
            assert 0 <= start < end <= len(text)
            assert end <= prior_end
            assert text[start:end] == edit["expected"], (ref, edit["expected"], text[start:end])
            text = text[:start] + edit["replacement"] + text[end:]
            prior_end = start
        rendered[ref] = text

    required = {
        (6, 4): ["cuando haya pecado y sea culpable", "o lo obtenido por extorsión"],
        (13, 43): ["en su coronilla calva o en su frente calva"],
        (19, 17): ["reprenderás con franqueza", "no participarás de su pecado"],
        (19, 23): ["consideraréis prohibido su primer fruto", "durante tres años os será prohibido"],
        (21, 20): ["llaga supurante"],
        (22, 2): ["las cosas santas que los hijos de Israel me consagran", "para que no profanen mi santo nombre"],
        (22, 4): ["el que toque el cuerpo de un animal muerto naturalmente"],
        (25, 23): ["porque la tierra es mía", "vosotros sois forasteros y extranjeros para conmigo"],
        (27, 29): ["Toda persona que haya sido consagrada irrevocablemente no podrá ser rescatada"],
    }
    forbidden = [
        "ó por el daño de la calumnia",
        "en su calva ó en su antecalva",
        "no consentirás sobre él pecado",
        "considerarán prohibido su primer fruto",
        "les será prohibido",
        "se abstengan de las santificaciones",
        "cosa inmunda de mortecino",
        "porque la tierra mía es",
        "Cualquier anatema (cosa consagrada) de hombres que se consagrare, no será redimido",
    ]
    for ref, phrases in required.items():
        for phrase in phrases:
            assert phrase in rendered[ref], (ref, phrase, rendered[ref])
    leviticus_text = "\n".join(rendered.values())
    for phrase in forbidden:
        assert phrase not in leviticus_text, phrase

    pending_ids = [
        item for item in registry["pending"]
        if item.get("id", "").startswith("leviticus-v17-")
    ]
    assert len(pending_ids) == 23
    assert registry["activeChangeSet"] == "editorial-changes/v17.json"
    print(json.dumps({
        "ok": True,
        "sourceVerses": len(source),
        "newEdits": len(change_set["changes"]),
        "pendingReview": len(pending_ids),
        "renderedSpotChecks": sum(len(value) for value in required.values()),
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
