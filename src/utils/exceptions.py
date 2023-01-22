from inspect import signature, Parameter


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

    retry_param = Parameter('retries', Parameter.KEYWORD_ONLY, default=2, annotation=int)
    sig = signature(fn)
    sig = sig.replace(parameters=(*sig.parameters.values(), retry_param))
    wrapper.__name__ = fn.__name__
    wrapper.__signature__ = sig
    return wrapper
