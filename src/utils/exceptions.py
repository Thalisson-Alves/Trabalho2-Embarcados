class ModbusWriteError(RuntimeError):
    ...


class ModbusReadError(RuntimeError):
    ...


class ModbusCRCError(RuntimeError):
    ...


def try_log(fn):
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception as e:
            print(f'Error on {fn.__name__} - {e}')
    
    wrapper.__name__ = fn.__name__
    return wrapper
