import time

_DELETED = object()


class MyDict:
    def __init__(self, size=8):
        self._buckets = [[] for _ in range(size)]
        self._entries = []
        self._len = 0

    def _bucket_index(self, key):
        return hash(key) % len(self._buckets)

    def _resize(self, new_size):
        old_entries = self._entries
        self._buckets = [[] for _ in range(new_size)]
        self._entries = []
        for item in old_entries:
            if item is not _DELETED:
                key, value = item
                entry_idx = len(self._entries)
                self._entries.append((key, value))
                self._buckets[self._bucket_index(key)].append(entry_idx)

    def __setitem__(self, key, value):
        bucket_idx = self._bucket_index(key)
        bucket = self._buckets[bucket_idx]
        for entry_idx in bucket:
            k, _ = self._entries[entry_idx]
            if k == key:
                self._entries[entry_idx] = (k, value)
                return

        entry_idx = len(self._entries)
        self._entries.append((key, value))
        bucket.append(entry_idx)
        self._len += 1

        if self._len > len(self._buckets) * 2 / 3:
            self._resize(len(self._buckets) * 2)

    def __getitem__(self, key):
        bucket_idx = self._bucket_index(key)
        for entry_idx in self._buckets[bucket_idx]:
            k, v = self._entries[entry_idx]
            if k == key:
                return v
        raise KeyError(key)

    def __delitem__(self, key):
        bucket_idx = self._bucket_index(key)
        bucket = self._buckets[bucket_idx]
        for pos, entry_idx in enumerate(bucket):
            k, _ = self._entries[entry_idx]
            if k == key:
                del bucket[pos]
                self._entries[entry_idx] = _DELETED
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        bucket_idx = self._bucket_index(key)
        for entry_idx in self._buckets[bucket_idx]:
            k, _ = self._entries[entry_idx]
            if k == key:
                return True
        return False

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def stats(self):
        longest = max((len(b) for b in self._buckets), default=0)
        return (len(self._buckets), self._len, longest)

    def keys(self):
        return [item[0] for item in self._entries if item is not _DELETED]

    def values(self):
        return [item[1] for item in self._entries if item is not _DELETED]

    def items(self):
        return [item for item in self._entries if item is not _DELETED]

    def __iter__(self):
        for item in self._entries:
            if item is not _DELETED:
                yield item[0]

    def __repr__(self):
        pairs = ', '.join(f'{k!r}: {v!r}' for k, v in self.items())
        return f'MyDict({{{pairs}}})'


if __name__ == '__main__':
    # Тесты из условия
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print('Результат stats():', d.stats())

    # Проверка порядка вставки (задание 1*)
    order_test = MyDict()
    order_test['first'] = 1
    order_test['second'] = 2
    order_test['third'] = 3
    del order_test['second']
    order_test['second'] = 22
    assert order_test.keys() == ['first', 'third', 'second']
    # Эксперимент с хешем 42
    class BadKey:
        def __init__(self, val):
            self.val = val

        def __hash__(self):
            return 42

        def __eq__(self, other):
            return isinstance(other, BadKey) and self.val == other.val

    t0 = time.perf_counter()
    good = MyDict()
    for i in range(1000):
        good[f'k{i}'] = i
    t_good = time.perf_counter() - t0

    t0 = time.perf_counter()
    bad = MyDict()
    for i in range(1000):
        bad[BadKey(i)] = i
    t_bad = time.perf_counter() - t0

    print(f'Обычные ключи: stats={good.stats()}, время={t_good:.4f} сек')
    print(f'Плохие ключи (hash=42): stats={bad.stats()}, время={t_bad:.4f} сек')


# Ответы на вопросы:
# 1. Номер корзины вычисляется как hash(key) % len(self._buckets). Когда мы увеличиваем таблицу,
# делитель меняется, поэтому у большинства ключей остаток станет другим. Если оставить элементы
# на старых местах, то при поиске по новому размеру мы пойдем не в ту корзину и не найдем их.
#
# 2. Для 1000 строковых ключей stats() возвращает (2048, 1000, 5) — ключи раскиданы равномерно,
# а вставка занимает около 0.001 сек. Для ключей с константным хешем 42 stats() возвращает
# (2048, 1000, 1000), так как абсолютно все элементы свалились в одну корзину. Из-за длинной
# цепочки каждая вставка проверяет все предыдущие элементы, и время возрастает примерно до 0.03 сек.