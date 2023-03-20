import base64
import io
import json

from flask import Flask

from tmbd import info as tmbd
from tmbd import api_key as tmbd_api_key

from api_ninja import info as api_ninja
from api_ninja import api_key as api_ninja_api_key

import requests

app = Flask(__name__)


def transform_response(response):
    keys = ['title', 'name', 'media_type', 'poster_path', 'profile_path', 'image']
    data = response.json()
    unique = []
    new_data = []
    for content in data['results']:
        image_found = False

        if 'profile_path' in content and content['profile_path'] is None:
            del content['profile_path']
        if 'poster_path' in content and content['poster_path'] is None:
            del content['poster_path']
        for key in list(content):
            if key not in keys:
                del content[key]
            if key == 'poster_path' and content[key] is not None:
                image_found = True
                content['image'] = tmbd.image_base_url + content['poster_path']
                del content['poster_path']
            if key == 'profile_path' and content[key] is not None:
                image_found = True
                content['image'] = tmbd.image_base_url + content['profile_path']
                del content['profile_path']
        if not image_found:
            content['image'] = 'https://via.placeholder.com/500x750'
        content_key = (content['title'] if 'title' in content else content['name']) + \
                      content['media_type'] + content['image']
        if content_key not in unique:
            unique.append(content_key)
            new_data.append(content)
        else:
            del content

    # make json from new data
    new_data_json = json.dumps(new_data)
    qr_code = generate_QR_code(new_data_json)
    if qr_code is None:
        qr_code = 'error'
    temp = {"movies": new_data, "qr_code": qr_code}
    new_data = temp
    data['results'] = new_data
    response._content = bytes(json.dumps(data), 'utf-8')
    return response


# route should be/ trending/{item}/week
@app.route('/trending/<string:item>/<string:timerange>', methods=['GET'])
def trending_item_timerange(item, timerange):
    return trending(item, timerange)


@app.route('/search/<string:query>', methods=['GET'])
def multi_search(query):
    req = tmbd.hostname + 'search/multi?api_key=' + tmbd_api_key.api_key + '&query=' + query
    response = requests.get(req)
    response = transform_response(response)
    return json.loads(response.text)


def trending(item, timerange):
    if item not in ['movie', 'tv', 'person', 'all']:
        item = 'all'
    if timerange not in ['day', 'week']:
        timerange = 'week'
    req = tmbd.hostname + 'trending/' + item + '/' + timerange
    req += '?api_key=' + tmbd_api_key.api_key
    response = requests.get(req)
    response = transform_response(response)

    return json.loads(response.text)


@app.route('/songs', methods=['GET'])
def get_movie_downloads():
    local_hostname = 'http://127.0.0.1:8000/'
    req = local_hostname + 'songs'
    response = requests.get(req)
    return response.text


def generate_QR_code(movie_json):
    fmt = 'png'
    api_url = api_ninja.hostname + '?data={}&format={}'.format(movie_json, fmt)
    response = requests.get(api_url, headers={'X-Api-Key': api_ninja_api_key.api_key, 'Accept': 'image/png'},
                            stream=True)
    if response.status_code == requests.codes.ok:
        image_data = io.BytesIO(response.content)
        return base64.b64encode(image_data.getvalue()).decode('utf-8')
    else:
        print("Error:", response.status_code, response.text)
        return None


if __name__ == '__main__':
    app.run()
