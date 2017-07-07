Health master: [![Code Health](https://landscape.io/github/blatinier/onestpasdespigeons/master/landscape.svg?style=plastic)](https://landscape.io/github/blatinier/onestpasdespigeons/master)
Health devel: [![Code Health](https://landscape.io/github/blatinier/onestpasdespigeons/devel/landscape.svg?style=plastic)](https://landscape.io/github/blatinier/onestpasdespigeons/devel)


# Backend

Backend part is in pigeon/

To launch it, install freezed requirements (ideally in a venv):

    # pip install -r requirements/freeze.pip

And launch the gunicorn server:

    # gunicorn pigeon.wsgi:application

Note: This is not fit for production use. The gunicorn should receive requests via a proxy http server (apache2, nginx, ...) and some deamon management system should handle the gunicorn (systemd, supervisord, ...)
