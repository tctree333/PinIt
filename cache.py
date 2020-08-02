import functools

def cache(func=None):
    """Cache decorator based on functools.lru_cache for async functions.

    This does not have a max_size and does not evict items.
    """

    def wrapper(func):
        sentinel = object()

        cache_ = {}
        hits = misses = 0
        cache_get = cache_.get
        cache_len = cache_.__len__

        async def wrapped(*args, **kwds):
            # Simple caching without ordering or size limit
            print("checking cache")
            nonlocal hits, misses
            key = hash(args)
            result = cache_get(key, sentinel)
            if result is not sentinel:
                print(f"{args[0]} found in cache!")
                hits += 1
                return result
            print(f"did not find {args[0]} in cache")
            misses += 1
            result = await func(*args, **kwds)
            cache_[key] = result
            return result

        def cache_info():
            """Report cache statistics"""
            return functools._CacheInfo(hits, misses, None, cache_len())

        wrapped.cache_info = cache_info
        return functools.update_wrapper(wrapped, func)

    if func:
        return wrapper(func)
    return wrapper