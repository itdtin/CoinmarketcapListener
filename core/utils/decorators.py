import time

from core.logger.logger import logger


def log_api(wrap):
    def wrap_function(*args, **kwargs):
        response = wrap(*args, **kwargs)
        body = (
            response.request.body
            if response.request.body is not None
            else "Empty request body"
        )
        logger.debug(args[0])
        logger.debug(
            "\n{}\n{}\n\n{}\n\n{}\n".format(
                "-----------Request----------->",
                response.request.method + " " + response.request.url,
                "\n".join(
                    "{}: {}".format(k, v) for k, v in response.request.headers.items()
                ),
                "request body: " + body,
            )
        )
        logger.debug(
            "\n{}\n{}\n\n{}\n\n".format(
                "<-----------Response-----------",
                "Status code:" + str(response.status_code),
                "\n".join("{}: {}".format(k, v) for k, v in response.headers.items()),
            )
        )
        return response

    return wrap_function


def timecheck(method):
    """Check the time it takes to execute a function"""

    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        execute_time = (te - ts) * 1000
        if "log_time" in kw:
            name = kw.get("log_name", method.__name__.upper())
            kw["log_time"][name] = int(execute_time)
        else:
            logger.debug(f"{method.__name__} {round(execute_time, 3)} ms")
        return result

    return timed
