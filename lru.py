class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = {}

    def get(self, key, default=None):
        if key not in self.data:
            return default
        # При обращении переносим ключ в конец, делая его самым свежим
        value = self.data.pop(key)
        self.data[key] = value
        return value

    def put(self, key, value) -> None:
        if key in self.data:
            # Перезапись ключа: удаляем старый, чтобы вставить в конец
            del self.data[key]
        elif len(self.data) >= self.capacity:
            # Вытесняем самый первый (самый старый) элемент
            oldest_key = next(iter(self.data))
            del self.data[oldest_key]
        self.data[key] = value

    def __len__(self) -> int:
        return len(self.data)

    def __contains__(self, key) -> bool:
        return key in self.data


if __name__ == '__main__':
    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    assert c.get('a') == 1        # теперь 'a' свежее, чем 'b'
    c.put('c', 3)                 # вытесняется 'b'
    assert 'b' not in c and c.get('a') == 1 and c.get('c') == 3
    c.put('a', 10)                # перезапись делает 'a' свежим
    c.put('d', 4)                 # вытесняется 'c'
    assert c.get('c') is None and c.get('a') == 10 and len(c) == 2

    # Дополнительная проверка: 'in' не должен обновлять свежесть
    c2 = LRUCache(2)
    c2.put('x', 1)
    c2.put('y', 2)
    assert 'x' in c2
    c2.put('z', 3)
    assert 'x' not in c2 and 'y' in c2

    print("Все проверки пройдены!")

# Удаление самого старого элемента за O(1):
# В стандартном dict порядок вставки сохраняется. Самый старый элемент всегда лежит
# в самом начале словаря. Конструкция next(iter(self.data)) берет первый ключ словаря 
# напрямую из итератора, не создавая промежуточных списков ключей (в отличие от list(self.data)[0], 
# который тратит O(N) памяти и времени). Удаление ключа по хешу через del также занимает O(1) в среднем.