import spacy
from spacy.tokens import Span
from spacy.language import Language

# Define a list of medications
medications = ['aspirin', 'ibuprofen', 'paracetamol']
nlp = spacy.load('en_ner_bionlp13cg_md')



# Add the medication entities to the NER model
MEDICATION = nlp.vocab.strings[u'MEDICATION']

# Add the medication entities to the NER model
ner = nlp.get_pipe('ner')
for med in medications:
    ner.add_label(str(MEDICATION))

# Define a custom component to add the medication entities to the doc
@Language.component('add_medication_entities')
def add_medication_entities(doc):
    new_ents = []
    for ent in doc.ents:
        if ent.label_ == "CHEMICAL":
            if ent.text.lower() in medications:
                new_ent = Span(doc, ent.start, ent.end, label=MEDICATION)
                new_ents.append(new_ent)
    doc.ents = list(doc.ents) + new_ents
    return doc

# Add the custom component to the pipeline
nlp.add_pipe('add_medication_entities', after='ner')

def MedicalWords(text):

    # Process text with spaCy NER model
    doc = nlp(text)

    # Extract medication entities
    medications = []
    for ent in doc.ents:
        if ent.label_ == "MEDICATION":
            medications.append(ent.text)

    # Print identified medication entities
    print("Identified medications:", medications)