# Разбор (разметка) корпуса текстов через natasha
# на входе - корпус исходных текстов (калатог в котором 1 файл - 1 статья источника-сайта)
# на выходе - ______________
from pathlib import Path
from natasha import (
    Segmenter,
    MorphVocab,
    
    NewsEmbedding,
    NewsMorphTagger,
    NewsSyntaxParser,
    NewsNERTagger,
    
    #PER,
    NamesExtractor,
    #AddrExtractor,
    #DatesExtractor,
    #MoneyExtractor,

    Doc
)

def main (corpus_path: str):
    # !!! внимание. исходные файлы должны быть сохранение в определенном формате
    paths = Path(corpus_path).glob('*.txt')
    for filename in paths:
        with open(filename, encoding='utf-8') as fdr:
            create_date, href, title, text = [line.strip('\n') for line in fdr][:4]

            segmenter = Segmenter()
            morph_vocab = MorphVocab()

            emb = NewsEmbedding()
            morph_tagger = NewsMorphTagger(emb)
            syntax_parser = NewsSyntaxParser(emb)
            ner_tagger = NewsNERTagger(emb)
            
            doc = Doc(text)
            doc.segment(segmenter)
            doc.tag_morph(morph_tagger)
            doc.parse_syntax(syntax_parser)
            doc.tag_ner(ner_tagger)
            
            for span in doc.spans:
                span.normalize(morph_vocab)

            for token in doc.tokens:
                token.lemmatize(morph_vocab)
            

            # разбор в разреще предложения
            '''
            for sent in doc.sents[:2]:               
                objects = {_.tokens[0].id: {'val': _.normal, 'type': _.type} for _ in sent.spans}
                rel = {_.head_id: {'obj': _.id, 'type': _.rel} for _ in sent.tokens if _.id in objects}
                subj = {_.id: _.lemma for _ in sent.tokens if _.id in rel}
                digest.append({'objects': objects, 'subj': subj, 'rel':rel})
            '''
            '''               
            # разбор в разрезе всего документа-новости
            objects = {_.tokens[0].id: {'normal': _.normal, 'type': _.type, 'text': _.text} for _ in doc.spans}
            rel = {_.head_id: {'obj': _.id, 'type': _.rel} for _ in doc.tokens if _.id in objects}
            subj = {_.id: {'lemma': _.lemma, 'text': _.text, 'pos': _.pos} for _ in doc.tokens if _.id in rel}
            digest = {'objects': objects, 'subj': subj, 'rel':rel}

            chunk={}
            for obj_id, obj_val in digest['objects'].items():
                object = obj_val['normal']
                chunk.setdefault(object, set([]))
                for subj_id, rel_val in digest['rel'].items():
                    if rel_val['obj'] == obj_id:
                        try:
                            chunk[object].add(f"{rel_val['type']} {digest['subj'][subj_id]['pos']} {digest['subj'][subj_id]['text']}")
                        except:
                            pass
            # в результате получаем объекты и связанные с ними сущности
            print (chunk)
            print ('--------------------')
            '''

if __name__ == '__main__':
    CORPUS_PATH = 'C:\\tmp\\docs\\#learning\\article\\Python\\example\\corpus\\rbc'
    main(CORPUS_PATH)

