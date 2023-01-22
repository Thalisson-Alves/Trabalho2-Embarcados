class ModbusWriteError(RuntimeError):
    ...


class ModbusReadError(RuntimeError):
    ...


class ModbusCRCError(RuntimeError):
    ...


def retry_log(fn):
    def wrapper(*args, retries: int = 2, **kwargs):
        for _ in range(retries + 1):
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                print(f'Error on {fn.__name__} - {e}')

    wrapper.__name__ = fn.__name__
    return wrapper
