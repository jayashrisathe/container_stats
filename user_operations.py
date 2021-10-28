""""This file is used to define HTTP methods"""
import re
import json
from aiohttp import web
import sqlalchemy
from models import user


def validate_data(data, mothod):
    """
    @description - Used to validate user data.
    @param - data(dictionary): User details which are to be insert or update
    @returns - message(string) if data is invalid.
    """
    message = ''
    if mothod == 'POST':
        if not data.get('email'):
            message += 'Email must be present.'
        if not data.get('name'):
            message += 'User name must be present.'

    if data.get('email'):
        result = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                          data.get('email'))
        if result is None:
            message += 'Invalid email'
    if data.get('phone'):
        result = re.findall(r'[A-Za-z]', data.get('phone'))
        if result:
            message += ' Invalid Phone'
    if data.get('name'):
        result = re.findall(r'[0-9]', data.get('name'))
        if result:
            message += ' Invalid name'
    if data.get('age'):
        if not str(data.get('age')).isdigit():
            message += ' Invalid age'
    return message


class UserCrud(web.View):
    """Used to define HTTP methods"""

    async def delete(self):
        """
        @description - Used to delete user record
        @param - self: delete request with id to delete record.
        @returns - response with status 200 in case of success and 500 in case of exception.
        """
        user_to_delete = self.app.session.query(
            user.User).filter(user.User.id == self.match_info.get('id')).first()
        if not user_to_delete:
            response_obj = {'Message': 'Sorry, Requested user is not present'}
            return web.Response(text=json.dumps(response_obj), status=404)
        try:
            self.app.session.delete(user_to_delete)
            self.app.session.commit()
            return web.Response(status=204)
        except sqlalchemy.orm.exc.UnmappedInstanceError as exception:
            response_obj = {'status': 'failed', 'reason': str(exception)}
            return web.Response(text=json.dumps(response_obj), status=500)

    async def put(self):
        """
        @description - Used to update user record.
        @param - self: put request with id to update record and data to update.
        @returns - response with status 200 in case of success and 500 in case of exception.
        """
        data = await self.json()
        message = validate_data(data, self.method)
        if message:
            response_obj = {'status': 'failed', 'reason': message}
            return web.Response(text=json.dumps(response_obj), status=500)
        user_obj = self.app.session.query(user.User).filter(
            user.User.id == self.match_info.get('id')).first()
        if not user_obj:
            return web.Response(text=json.dumps({'Message': 'Sorry, Requested user is not present'}), status=404)
        if data.get('name'):
            user_obj.name = data.get('name')
        if data.get('phone'):
            user_obj.phone = data.get('phone')
        if data.get('email'):
            user_obj.email = data.get('email')
        if data.get('age'):
            user_obj.age = data.get('age')

        try:
            self.app.session.add(user_obj)
            self.app.session.commit()
        except (exception.IntegrityError, exception.InvalidRequestError) as exception:
            response_obj = {'status': 'failed', 'reason': str(exception)}
            return web.Response(text=json.dumps(response_obj), status=500)
        return web.Response(
            status=200, text=json.dumps({'Message': 'User updated successfully'}),
            content_type='application/json')

    async def get(self):
        """
        @description - Used to get all or specific user details.
        @param - self: get request with id or without id.
        @returns - response with status 200 in case of success and 500 in case of exception.
        """
        if self.match_info.get('id'):
            user_obj = self.app.session.query(
                user.User).filter(user.User.id == self.match_info.get('id')).first()

            data_dict = {}
            status = 200
            if user_obj:
                data_dict.update({
                    'id': user_obj.id, 'name': user_obj.name,
                    'phone': user_obj.phone, 'email': user_obj.email,
                    'age': user_obj.age})
            else:
                status = 404
                data_dict.update({'Message': 'Sorry, Requested user is not present'})
            return web.Response(status=status, body=json.dumps({
                'users': [data_dict]}), content_type='application/json')

        all_users = [
            {'name': i.name, 'id': i.id, 'phone': i.phone, 'email': i.email, 'age': i.age}
            for i in self.app.session.query(user.User)]
        return web.Response(
            status=200, body=json.dumps({'users': all_users}),
            content_type='application/json')

    async def post(self):
        """
        @description - Used to insert user records.
        @param - self: post request with data to insert.
        @returns - response with status 200 in case of success and 500 in case of exception.
        """
        data = await self.json()
        message = validate_data(data, self.method)
        if message:
            response_obj = {'status': 'failed', 'reason': message}
            return web.Response(text=json.dumps(response_obj), status=500)
        phone = data.get('phone')
        age = data.get('age')
        name = data.get('name')
        email = data.get('email')

        user_obj = user.User(name=name, phone=phone, email=email, age=age)
        try:
            res = self.app.session.add(user_obj)
            self.app.session.commit()
        except (exception.IntegrityError, exception.InvalidRequestError) as exception:
            response_obj = {'status': 'failed', 'reason': 'Invalid Request!'}
            return web.Response(text=json.dumps(response_obj), status=500)
        response_obj = {'status': 'success'}
        # return a success json response with status code 200 i.e. 'OK'
        return web.Response(text=json.dumps(response_obj), status=200)

    async def handle(self):
        """@param - self: request with URL:'/'
           @returns - response with success status.
        """
        return web.Response(text=json.dumps({'status': 'success'}))
