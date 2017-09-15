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

    example =>
        routes = [
            Route(path='/hello',
                  template='index.html',
                  remote='https://example.com/api/v1/hello'),
            ...
        ]

    params =>
    :param path:       the url path of the page
    :param template:   the name of jinja template
    :param remote_url: (optional) the full url of remote context. If exists, 
                       json response from address will be pass to template with
                       name ``objects``
    
    keyword arguments =>
    
    """

    def __init__(self, path: str, template: str, remote_url: str = None):
        def __f():
            if remote_url is None:
                return render_template(template)

            # Build remote request url
            url = remote_url
            if request.args:
                url += ('?' + urlencode(request.args))

            # Make remote request
            try:
                req_body = request.get_json(force=True)
                res = http.request(request.method, url, body=req_body)
            except JSONDecodeError:
                return abort(500)

            # Make object for template
            obj = json.loads(res.data)
            options = {
                'objects': obj,
                'context': {
                    'params': request.args
                }
            }

            return render_template(template, **options)

        self.path = path
        self.f = __f


def start(__name__, routes: List[Route], host=None, port=None, debug=None, **kwargs):
    """
    Run tinyweb application

    example =>
        if __name__ == '__main__':
            start(__name__, routes, host='127.0.0.1')
    """

    app = Flask(__name__)
    for route in routes:
        app.add_url_rule(route.path, endpoint=route.path, view_func=route.f)

    app.run(host=host, port=port, debug=debug, **kwargs)
