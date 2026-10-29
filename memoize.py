import time

_KWARGS_MARK = object()


def memoize(func):
    """Возвращает новую функцию с кэшем результатов через замыкание."""
    cache = {}

    def wrapper(*args, **kwargs):
        # Формируем уникальный ключ из позиционных и именованных аргументов
        if kwargs:
            key = args + (_KWARGS_MARK,) + tuple(sorted(kwargs.items()))
        else:
            key = args

        # Проверяем наличие в кэше; если аргументы нехешируемые — выполняем напрямую
        try:
            in_cache = key in cache
        except TypeError:
            return func(*args, **kwargs)

        if in_cache:
            wrapper.hits += 1
            return cache[key]

        wrapper.misses += 1
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.cache_clear = cache_clear
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__

    return wrapper


if __name__ == '__main__':
    # 1. Проверки из условия задания
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'

    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)

    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    # 2. Эксперимент с рекурсией
    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    # Вариант A
    fast_fib = memoize(fib)
    t0 = time.perf_counter()
    res_a = fast_fib(30)
    time_a = time.perf_counter() - t0

    # Вариант B
    fib = memoize(fib)
    t0 = time.perf_counter()
    res_b = fib(30)
    time_b = time.perf_counter() - t0

    print(f"Вариант A: misses = {fast_fib.misses}, время = {time_a:.6f} с")
    print(f"Вариант B: misses = {fib.misses}, время = {time_b:.6f} с")

# Объяснение по правилу LEGB:
# Когда внутри функции вызывается fib(n - 1), Python ищет переменную `fib`
# по цепочке LEGB: Local -> Enclosing -> Global -> Built-in.
# Внутри тела fib локальной переменной с таким именем нет, поэтому поиск идет в Global.
# - В варианте A в глобальной области видимости под именем `fib` все еще лежит старая медленная функция.
#   Поэтому кэшируется только самый первый вызов fast_fib(30), а вся рекурсия идет мимо кэша.
# - В варианте B мы перезаписали глобальное имя `fib` оберткой с кэшем (`fib = memoize(fib)`).
#   Теперь рекурсивные вызовы обращаются уже к мемоизированной функции, и промежуточные шаги берутся из кэша.