from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB

class Model(CountVectorizer, MultinomialNB):
    def __init__(self):
        super().__init__()
        self.x = None
        self.data_list = []
        self.leval_list = []
        self.cv = CountVectorizer()
        self.model = MultinomialNB()

    def add_data(self, data, leval):
        if isinstance(data, list):
            self.data_list.extend(data)
            if isinstance(leval, list):
                self.leval_list.extend(leval)
            else:
                self.leval_list.extend([leval] * len(data))

        elif isinstance(data, str):
            self.data_list.append(data)
            if isinstance(leval, list):
                self.leval_list.append(leval[0])
            else:
                self.leval_list.append(leval)
        else:
            raise Exception('ERROR ! ERROR ! Your input is not a string or list')

    def train(self):
        self.x = self.cv.fit_transform(self.data_list)
        self.model.fit(self.x, self.leval_list)

    def classify(self, text: str):
        text_vector = self.cv.transform([text])
        return self.model.predict(text_vector)[0] # 결과값만 반환하도록 [0] 추가
