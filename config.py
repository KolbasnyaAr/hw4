class Config:
    def __init__(self, data: dict):
        if not isinstance(data, dict):
            raise TypeError("Ожидается словарь")
        # Сохраняем исходный словарь в обход переопределенного __setattr__
        object.__setattr__(self, '_data', data)

    def __getattr__(self, name: str):
        data = object.__getattribute__(self, '_data')
        try:
            val = data[name]
        except KeyError:
            raise AttributeError(f"Атрибут '{name}' не найден")
        
        # Если значение внутри — словарь, оборачиваем его в Config
        if isinstance(val, dict):
            return Config(val)
        return val

    def __setattr__(self, name: str, value):
        data = object.__getattribute__(self, '_data')
        # Если присваиваем объект Config, достаем из него сырой словарь
        if isinstance(value, Config):
            value = value.to_dict()
        data[name] = value

    def to_dict(self) -> dict:
        return object.__getattribute__(self, '_data')

    def __dir__(self):
        data = object.__getattribute__(self, '_data')
        return list(super().__dir__()) + [str(k) for k in data.keys()]


if __name__ == '__main__':
    raw = {'db': {'host': 'localhost', 'port': 5432}, 'debug': True}
    cfg = Config(raw)
    assert cfg.debug is True
    assert cfg.db.host == 'localhost' and cfg.db.port == 5432
    assert getattr(cfg, 'timeout', 30) == 30
    assert hasattr(cfg.db, 'user') is False
    cfg.db.port = 6543                    # запись меняет исходный словарь
    assert raw['db']['port'] == 6543
    cfg.timeout = 10
    assert raw['timeout'] == 10
    assert cfg.to_dict() is raw
    assert 'db' in dir(cfg)               


# Ответы на вопросы к заданию:
#
# 1. Почему hasattr и getattr со значением по умолчанию перестанут работать, если бросать KeyError?
# Функции hasattr и getattr внутри ловят исключительно ошибку AttributeError.
# Если при отсутствии ключа выбрасывать KeyError, встроенная логика этих функций
# не сможет её перехватить, и программа аварийно упадет с ошибкой KeyError
# вместо того, чтобы вернуть False или дефолтное значение.
#
# 2. Как избежать бесконечной рекурсии при обращении к собственному атрибуту, в котором хранится словарь?
# Метод __setattr__ вызывается при любой попытке присвоить значение через точку (self.field = value).
# Если бы в __init__ мы написали self._data = data, то вызвали бы __setattr__,
# который попытался бы прочитать еще не существующее поле self._data, что снова вызвало бы __getattr__,
# приведя к бесконечному циклу. Чтобы разорвать этот круг, мы обращаемся напрямую
# к базовой реализации через object.__setattr__ и object.__getattribute__.