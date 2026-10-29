import re
from collections import Counter


class SearchIndex:
    """
    Поисковый индекс на базе инвертированного индекса.

    Для быстрого поиска используется словарь _inverted_index (слово -> множество id документов).
    Чтобы remove и перезапись работали быстро без перебора всей базы, хранится
    словарь _doc_words (id документа -> счетчик слов). Благодаря ему при удалении
    документа мы сразу знаем, из каких слов нужно убрать doc_id.
    Счетчик _word_counts хранит общую частотность слов для метода top_words.
    """

    def __init__(self):
        self._inverted_index = {}
        self._doc_words = {}
        self._word_counts = Counter()

    @staticmethod
    def _tokenize(text: str):
        return re.findall(r'\w+', text.lower())

    def add(self, doc_id, text: str):
        if doc_id in self._doc_words:
            self.remove(doc_id)

        tokens = self._tokenize(text)
        counts = Counter(tokens)
        self._doc_words[doc_id] = counts

        for word, freq in counts.items():
            if word not in self._inverted_index:
                self._inverted_index[word] = set()
            self._inverted_index[word].add(doc_id)
            self._word_counts[word] += freq

    def remove(self, doc_id):
        counts = self._doc_words.pop(doc_id, None)
        if counts is None:
            return

        for word, freq in counts.items():
            docs = self._inverted_index.get(word)
            if docs is not None:
                docs.discard(doc_id)
                if not docs:
                    del self._inverted_index[word]
            self._word_counts[word] -= freq
            if self._word_counts[word] <= 0:
                del self._word_counts[word]

    def search_all(self, *words: str):
        if not words:
            return set()
        normalized = [w.lower() for w in words]
        sets = []
        for w in normalized:
            docs = self._inverted_index.get(w)
            if not docs:
                return set()
            sets.append(docs)
        sets.sort(key=len)
        result = set(sets[0])
        for s in sets[1:]:
            result &= s
            if not result:
                break
        return result

    def search_any(self, *words: str):
        if not words:
            return set()
        result = set()
        for w in words:
            docs = self._inverted_index.get(w.lower())
            if docs:
                result |= docs
        return result

    def top_words(self, n: int):
        if n <= 0:
            return []
        return sorted(
            self._word_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )[:n]

    def search_ranked(self, query: str, limit: int = 10):
        if limit <= 0:
            return []
        query_words = self._tokenize(query)
        if not query_words:
            return []

        scores = {}
        for word in set(query_words):
            for doc_id in self._inverted_index.get(word, ()):
                scores[doc_id] = scores.get(doc_id, 0) + self._doc_words[doc_id][word]

        ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
        return [doc_id for doc_id, _ in ranked[:limit]]


if __name__ == '__main__':
    idx = SearchIndex()
    idx.add(1, 'Python is a programming language.')
    idx.add(2, 'A dict is a hash table; a set is a hash table too!')
    idx.add(3, 'Python dict and set are fast.')
    assert idx.search_all('python') == {1, 3}
    assert idx.search_all('dict', 'set') == {2, 3}
    assert idx.search_all('python', 'hash') == set()
    assert idx.search_any('language', 'fast') == {1, 3}
    assert idx.search_all('PYTHON') == {1, 3}
    assert idx.search_all('nothing') == set()
    assert idx.top_words(2) == [('a', 5), ('is', 3)]
    idx.remove(1)
    assert idx.search_all('python') == {3}
    assert idx.search_any('language', 'programming') == set()
    idx.add(3, 'Totally new text')
    assert idx.search_all('python') == set()
    assert idx.search_all('new') == {3}
    print("Все базовые проверки пройдены!")
