from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from aiohttp import web
import json
#from get_container_stats import get_curent_stats

DB_URI = 'sqlite:///container_stats.db'
Base = declarative_base()


class Stats(Base):
    __tablename__ = 'stats'

    # res = requests.post('http://localhost:8080/stats',data=json.dumps({'container_name': 'test', 'cpu_usage': 'test_data', 'memory_usage': 'test_data', 'memory_limit': 'test_data', 'container_image':'test_data'}))
    id = Column(Integer, primary_key=True)
    container_name = Column(String(50), nullable=False)
    cpu_usage = Column(String(50))
    memory_usage = Column(String(50))
    memory_limit = Column(String(50))
    container_image = Column(String(50))

    def __init__(self, container_name, cpu_usage, memory_usage, memory_limit, container_image):
        self.container_name = container_name
        self.cpu_usage = cpu_usage
        self.memory_usage = memory_usage
        self.memory_limit = memory_limit
        self.container_image = container_image

class StatsOperations(web.View):

    async def handle(self):
        """@param - self: request with URL:'/'
           @returns - response with success status.
        """
        return web.Response(text=json.dumps({'status': 'success'}))

    async def post(self):

        data = await self.json()
        
        print("data in post==============", data)
        stats_obj = Stats(container_name=data.get('container_name'),
                         cpu_usage=data.get('cpu_usage'),
                         memory_usage=data.get('memory_usage'),
                         memory_limit=data.get('memory_limit'),
                         container_image=data.get('container_image')

                         )
        try:
            res = self.app.session.add(stats_obj)
            self.app.session.commit()
        except (exception.IntegrityError, exception.InvalidRequestError) as exception:
            response_obj = {'status': 'failed', 'reason': 'Invalid Request!'}
            return web.Response(text=json.dumps(response_obj), status=500)
        response_obj = {'status': 'success'}
        return web.Response(text=json.dumps(response_obj), status=200)

    def get(self):
        all_data = [
            {'container_name': i.container_name, 'id': i.id, 'cpu_usage': i.cpu_usage, 'memory_usage': i.memory_usage,
             'memory_limit': i.memory_limit, 'container_image': i.container_name}
            for i in self.app.session.query(Stats)]
        #data1 = get_curent_stats()
        print("all_data-----------------", all_data)
        #print("data1----------------", data1)
        return web.Response(
            status=200, body=json.dumps({'container_stats': all_data}),
            content_type='application/json')

def get_db_seesion():
    engine = create_engine(DB_URI)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(autocommit=False, autoflush=False, bind=create_engine(DB_URI))
    session = scoped_session(session_maker)
    return session
