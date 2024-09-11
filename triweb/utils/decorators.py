def lock(lock):
    def decorator(func):
        def wrapper(*args, **kw):
            with lock:
                return func(*args, **kw)
        return wrapper
    return decorator
