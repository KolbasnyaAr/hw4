class Money:
    """Неизменяемый хешируемый класс денежной суммы в минимальных единицах валюты."""

    __slots__ = ('amount', 'currency')

    def __init__(self, amount: int, currency: str):
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError(f"Объект Money неизменяем: нельзя изменить или добавить атрибут '{name}'")

    def __delattr__(self, name):
        raise AttributeError(f"Объект Money неизменяем: нельзя удалить атрибут '{name}'")

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f"Нельзя складывать разные валюты: '{self.currency}' и '{other.currency}'")
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self):
        return f"Money({self.amount}, '{self.currency}')"


def total_by_currency(payments: list[Money]) -> dict[str, Money]:
    """Группирует платежи по валютам и возвращает словарь с суммарными объектами Money."""
    totals: dict[str, Money] = {}
    for payment in payments:
        if payment.currency in totals:
            totals[payment.currency] = totals[payment.currency] + payment
        else:
            totals[payment.currency] = payment
    return totals


# ==============================================================================
# Комментарий к заданию:
# Если бы поля объекта можно было менять после помещения в хеш-таблицу (множество или словарь),
# то изменился бы его хеш, вычисляемый от этих полей, однако сам объект остался бы в прежней
# корзине (bucket), рассчитанной по исходному хешу.
# Как в примере с Point из лекции (где после изменения p.x проверка p in visited возвращала False),
# поиск по новому хешу пойдет уже в другую корзину, из-за чего объект фактически потеряется
# внутри коллекции, нарушив базовые инварианты хеш-таблицы.
# При этом объект будет по-прежнему физически присутствовать в памяти множества/словаря,
# порождая трудноуловимые утечки и логические ошибки.
# ==============================================================================


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    m = Money(1500, 'RUB')
    assert repr(m) == "Money(1500, 'RUB')"
    assert (m == "1500 RUB") is False

    print("Все тесты пройдены успешно!")