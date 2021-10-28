from aiohttp import web
from stats import Stats, StatsOperations, get_db_seesion
URL = '/stats'
# URL_WITH_ID = '/stats/{id}'

def get_app():
    """
    @description - Used to create database session and calls HTTP methods
    @returns - returns web app
    """
    app = web.Application()
    app.session = get_db_seesion()
    app.router.add_get('/', StatsOperations.handle)
    app.router.add_get('/stats', StatsOperations.get)
    app.router.add_post('/insert_current_stats', StatsOperations.post)
    return app


if __name__ == '__main__':
    web.run_app(get_app())
