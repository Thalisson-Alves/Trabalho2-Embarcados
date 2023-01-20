from threading import Lock

class SingletonMeta(type):
    __instances = {}
    __mutex = Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.__instances:
            with cls.__mutex:
                cls.__instances[cls] = super().__call__(*args, **kwargs)
        return cls.__instances[cls]
