import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any
import threading
import status_code
import database
import options
import json
import datetime


def refresh_database():
    RestServer._database.clean_database()
    RestServer._database = database.Database()
    if RestServer._database.is_connected() == RestServer.ERROR:
        print("[-] Error connecting to database")
        return
    print("[+] Database refreshed")


class RestServer(BaseHTTPRequestHandler):
    ERROR = -1

    _database = None
    _running = False
    _log_enabled = False

    @staticmethod
    def init():
        RestServer._database = database.Database()
        if RestServer._database.is_connected() == RestServer.ERROR:
            print("[-] Error connecting to database")
            return

        RestServer._running = True
        print("[+] Server started")

    @staticmethod
    def is_running():
        return RestServer._running

    def validate_params(self, params, required_params, verb, route):
        for required_param in required_params:
            if required_param not in params:
                print(f"[-] Incorrect usage, {verb} {route} usage : " + required_params.__str__())
                return RestServer.ERROR

        if "user_id" in params:
            if not params["user_id"].isdigit():
                return RestServer.ERROR
        if "download_id" in params:
            if not params["download_id"].isdigit():
                return RestServer.ERROR
        if "age" in params:
            if not params["age"].isdigit():
                return RestServer.ERROR
        if "downloads" in params:
            if not params["downloads"].isdigit():
                return RestServer.ERROR
        if "first_name" in params:
            if not params["first_name"].isalpha():
                return RestServer.ERROR
        if "last_name" in params:
            if not params["last_name"].isalpha():
                return RestServer.ERROR
        if "country" in params:
            if not params["country"].isalpha():
                return RestServer.ERROR
        if "file_name" in params:
            if not params["file_name"].isalpha():
                pass
                # return RestServer.ERROR
        if "subscription" in params:
            if not params["subscription"].isalpha():
                return RestServer.ERROR
        if "last_visit" in params:
            try:
                datetime.datetime.strptime(params["last_visit"], '%Y-%m-%d')
            except ValueError:
                return RestServer.ERROR

        print("[+] Validated params")
        return True

    def get_body_data(self):
        content_length = int(self.headers['Content-Length'])
        body_data = self.rfile.read(content_length)
        body_data = body_data.decode('utf-8').split('&')
        body_data = {key_value_pair.split('=')[0]: key_value_pair.split('=')[1] for key_value_pair in body_data}
        print("[+] Body data: " + str(body_data))
        return body_data

    def handle_request(self, verb):
        print(f"[+] {verb} request received: " + self.path)
        result_code, result_item = self.route(self.path, verb)
        if result_code in status_code.EXCEPTED_STATUS_CODES[verb]:
            print(f"[+] Response: {result_code} {status_code.get_status_message(result_code)}")
            self.send_response(result_code)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(result_item).encode())
        else:
            print(f"[-] Response: {result_code} {status_code.get_status_message(result_code)}")
            self.send_response(result_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {f"{result_code}": f"{status_code.get_status_message(result_code)}"}
            self.wfile.write(json.dumps(response).encode())

        refresh_database()
        print("----------------------------------------")

    def route(self, path, verb):
        if verb == 'GET':
            if path == '/users':
                result = RestServer._database.get_users()
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                else:
                    return [status_code.OK, result]
            elif path == '/downloads_users':
                result = RestServer._database.get_downloads_join_users()
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                else:
                    return [status_code.OK, result]
            elif path == '/songs':
                result = RestServer._database.get_songs_join_singers()
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                else:
                    return [status_code.OK, result]
            elif path == '/downloads':
                result = RestServer._database.get_all_downloads()
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                else:
                    return [status_code.OK, result]
            elif path.startswith('/users/'):
                user_id = path.split('/')[2]
                if not user_id.isdigit():
                    return [status_code.BAD_REQUEST, None]
                result = RestServer._database.get_user(user_id)
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                elif result is None:
                    return [status_code.NOT_FOUND, None]
                else:
                    return [status_code.OK, result]
            elif path.startswith('/downloads/'):
                download_id = path.split('/')[2]
                if not download_id.isdigit():
                    return [status_code.BAD_REQUEST, None]
                result = RestServer._database.get_download(download_id)
                if result == RestServer.ERROR:
                    return [status_code.INTERNAL_SERVER_ERROR, None]
                elif result is None:
                    return [status_code.NOT_FOUND, None]
                else:
                    return [status_code.OK, result]
            else:
                return [status_code.NOT_IMPLEMENTED, None]
        elif verb == 'POST':
            if path == '/users':
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['first_name', 'last_name', 'age', 'country'],
                                        'POST', '/users') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.create_user(body_data['first_name'],
                                                              body_data['last_name'],
                                                              body_data['age'],
                                                              body_data['country'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    return [status_code.CREATED, result]

            elif path == '/downloads':
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['user_id', 'file_name'],
                                        'POST', '/downloads') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.create_download(body_data['user_id'],
                                                                  body_data['file_name'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    return [status_code.CREATED, result]

            else:
                return [status_code.NOT_IMPLEMENTED, None]

        elif verb == 'PUT':
            if path == '/users/downloads':
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['user_id', 'downloads'],
                                        'PUT', '/users/downloads') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.update_user_downloads(body_data['user_id'],
                                                                        body_data['downloads'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    elif result is None:
                        return [status_code.NOT_FOUND, None]
                    return [status_code.OK, result]
            elif path == "/users/subscription":
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['user_id', 'subscription'],
                                        'PUT', '/users/subscription') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.update_user_subscription(body_data['user_id'],
                                                                           body_data['subscription'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    elif result is None:
                        return [status_code.NOT_FOUND, None]
                    return [status_code.OK, result]
            elif path == "/users/last-visit":
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['user_id', 'last_visit'],
                                        'PUT', '/users/last-visit') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.update_user_last_visit(body_data['user_id'],
                                                                         body_data['last_visit'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    elif result is None:
                        return [status_code.NOT_FOUND, None]
                    return [status_code.OK, result]
            else:
                return [status_code.NOT_IMPLEMENTED, None]
        elif verb == 'DELETE':
            if path == '/users':
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['user_id'],
                                        'DELETE', '/users') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.delete_user(body_data['user_id'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    elif result is None:
                        return [status_code.NOT_FOUND, None]
                    return [status_code.OK, result]
            elif path == '/downloads':
                body_data = self.get_body_data()
                if self.validate_params(body_data, ['download_id'],
                                        'DELETE', '/downloads') == RestServer.ERROR:
                    return [status_code.BAD_REQUEST, None]
                else:
                    result = RestServer._database.delete_download(body_data['download_id'])
                    if result == RestServer.ERROR:
                        return [status_code.INTERNAL_SERVER_ERROR, None]
                    elif result is None:
                        return [status_code.NOT_FOUND, None]
                    return [status_code.OK, result]
        elif verb == 'OPTIONS':
            return [status_code.OK, options.OPTIONS]
        else:
            return [status_code.NOT_IMPLEMENTED, None]

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_PUT(self):
        self.handle_request('PUT')

    def do_PATCH(self):
        self.handle_request('PATCH')

    def do_DELETE(self):
        self.handle_request('DELETE')

    def do_OPTIONS(self):
        self.handle_request('OPTIONS')

    def log_message(self, format: str, *args: Any) -> None:
        if self._log_enabled:
            super().log_message(format, *args)


if __name__ == '__main__':
    _restServer = HTTPServer(('localhost', 8000), RestServer)
    RestServer.init()
    if RestServer.is_running():
        _restServer.serve_forever()
    else:
        print("[-] Server not started.")





