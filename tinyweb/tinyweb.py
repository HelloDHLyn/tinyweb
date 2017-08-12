from json import JSONDecodeError
from typing import List
from urllib.parse import urlencode

import certifi
import urllib3
from flask import Flask, render_template, json, request, abort

http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())


class Route:
    """
    Object for routes.

    example:
        routes = [
            Route(path='/hello',
                  template='index.html',
                  ctx_path='https://example.com/api/v1/hello'),
            ...
        ]

    :param path:     the url path of the page
    :param template: the name of jinja template
    :param ctx_path: (optional) the full url of context. If exists, json
                     response from ctx_path will be pass to template with
                     name ``context``
    """

    def __init__(self, path: str, template: str, ctx_path: str = None):
        def __f():
            if ctx_path is None:
                return render_template(template)
            else:
                url = ctx_path
                if request.args:
                    url += ('?' + urlencode(request.args))

                try:
                    ctx = json.loads(http.request('GET', url).data)
                except JSONDecodeError:
                    return abort(500)

                return render_template(template, context=ctx)

        self.path = path
        self.f = __f


def start(__name__, routes: List[Route], host: str):
    """
    Run flask application

    example:
        if __name__ == '__main__':
            start(__name__, routes, host='127.0.0.1')
    """

    app = Flask(__name__)
    for route in routes:
        app.add_url_rule(route.path, endpoint=route.path, view_func=route.f)

    app.run(host=host)
