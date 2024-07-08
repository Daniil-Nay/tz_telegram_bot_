class InjectMiddleware:
    """
    Данная миддлварь нужна для передочи дополнительных параметров в методы (хэндлеры) роутеров.
    Если просто говорить, то я не хотел несколько раз вызывать (или во всех файлах) load_config, а хотел сделать
    выгрузку конфигурационных данных в одном месте - main в bot.py
    """
    def __init__(self, **kwargs):
        self.dependencies = kwargs

    async def __call__(self, handler, event, data):
        data.update(self.dependencies)
        return await handler(event, data)