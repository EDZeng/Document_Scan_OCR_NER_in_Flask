import spacy
from spacy.tokens import DocBin
import pickle

nlp = spacy.blank("en")

# load Data
training_data = pickle.load(open('./data/TrainData.pickle', 'rb'))
test_data = pickle.load(open('./data/TestData.pickle', 'rb'))

# the DocBin will store the example documents
db = DocBin()
for text, annotations in training_data:
    doc = nlp(text)
    ents = []
    for start, end, label in annotations['entities'] :      # annotations['entities']就是在資料前處理時的索引資訊
        span = doc.char_span(start, end, label=label)
        ents.append(span)
    doc.ents = ents
    db.add(doc)
db.to_disk("./data/train.spacy")



# the DocBin will store the example documents
db_test = DocBin()
for text, annotations in test_data:
    doc = nlp(text)
    ents = []
    for start, end, label in annotations['entities']:
        span = doc.char_span(start, end, label=label)
        ents.append(span)
    doc.ents = ents
    db_test.add(doc)
db_test.to_disk("./data/test.spacy")


