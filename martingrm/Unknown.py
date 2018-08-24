from json import JSONEncoder

class Unknown(object):
    """An unknown word

    Attributes:
        sentence: Dest sentence.
        originalSentence: Original sentence.
        sentenceNumber: Original sentence position.
        wordNumber: relative position on the nmt output sentence.
        original: A string, the original word.
        translation: The user will provide this, which is the translation for the unknown word.
        embedding: An array, the embedding.
        originalWordNumber: relative position on the source sentence
    """

    def __init__(self, sen, senNum, wNum):
        self.sentence = sen
        self.sentenceNumber = senNum
        self.wordNumber = wNum
        self.originalWordNumber = -1
        self.original = ""
        self.originalSentence = ""
        self.translation = ""
        self.embedding = []

    def default(self, o):
        return "{ok}"

    def set_embedding(self, emb):
        self.embedding = emb

    def set_translation(self, trans):
        self.translation = trans

    def set_original(self, word):
        self.original = word

    def set_original_wordNumber(self, num):
        self.originalWordNumber = num

    def set_original_sentence(self, sentence):
        self.originalSentence = sentence



class MyEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Unknown):
            return super(MyEncoder, self).default(obj)
        del obj.sentence
        del obj.sentenceNumber
        del obj.wordNumber
        del obj.originalSentence
        del obj.originalWordNumber
        # del obj.original
        return obj.__dict__


class MyEvaluationEncoder(JSONEncoder):
    def default(self, obj):
        if not isinstance(obj, Unknown):
            return super(MyEvaluationEncoder, self).default(obj)
        del obj.sentence
        #del obj.sentenceNumber
        #del obj.wordNumber
        del obj.originalSentence
        obj.originalWordNumber = obj.originalWordNumber.item()
        #del obj.original
        #del obj.translation
        del obj.embedding
        return obj.__dict__
