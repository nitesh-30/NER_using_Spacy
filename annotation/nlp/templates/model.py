import spacy
from spacy.tokens import DocBin
from tqdm import tqdm
import subprocess
import json
def trianmodel():
    nlp = spacy.blank("en")  # load a new spaCy model
    db = DocBin()

    with open('annotations.json') as f:
        TRAIN_DATA = json.load(f)

    for text, annot in tqdm(TRAIN_DATA['annotations']):
        doc = nlp.make_doc(text)
        ents = []
        for start, end, label in annot["entities"]:
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                print("Skipping entity")
            else:
                ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk("./training_data.spacy")

    # Full path to your Python interpreter
    import sys

    python_path = sys.executable
    print(f"Python Interpreter Path: {python_path}")


    # Run spaCy init command
    init_command = f"{python_path} -m spacy init config config.cfg --lang en --pipeline ner --optimize efficiency"
    subprocess.run(init_command, shell=False)

    # Run spaCy train command
    train_command = f"{python_path} -m spacy train config.cfg --output ./ --paths.train ./training_data.spacy --paths.dev ./training_data.spacy"
    subprocess.run(train_command, shell=False)
