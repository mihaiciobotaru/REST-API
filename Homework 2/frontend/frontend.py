import requests
from flask import Flask, render_template

backend_host = 'http://localhost:5001/'
app = Flask(__name__)


@app.route('/', methods=["GET"])
def main_page():
    return render_template('index.html')


def all_content_to_html(content_list, qr_code=None):
    if qr_code is not 'error':
        qr_code = 'data:image/png;base64,' + qr_code
        qr_code = f'<img src="{qr_code}">'
    else:
        qr_code = ''

    html = '<div class="all-content-items">'
    for content in content_list:
        html += content_to_html(content)
    html += '</div>'
    html += '<div class="qr_code">'
    html += qr_code
    html += '</div>'
    return html


def content_to_html(content_json):
    # print all keys in movie_json
    title = content_json['title'] if 'title' in content_json else content_json['name']
    content_type = content_json['media_type']
    content_type = content_type[0].upper() + content_type[1:]
    if content_type == 'Tv':
        content_type = 'TV Series'

    image = content_json['image']

    html = '<div class="content-item">'
    html += f'<img src="{image}">'
    html += f'<div class="content_data">'
    html += f'<div class="content_info">'
    html += f'<h3 class="title">{title}</h3>'
    # html += f'<p>{movie_json["overview"]}</p>'
    html += f'<hr>'
    html += f'<p>{content_type}</p>'
    # add a button to add to favorites
    html += f'</div>'
    html += f'</div>'
    html += f'</div>'
    return html


@app.route('/trending/<string:item>/<string:timerange>', methods=['GET'])
def search(item, timerange):
    try:
        response = requests.get(backend_host + f'trending/{item}/{timerange}')
        if response.status_code == 200:
            response_json = response.json()
            content_list = response_json['results']['movies']
            qr_code = response_json['results']['qr_code']

            return all_content_to_html(content_list, qr_code)
        else:
            return ""
    except Exception as e:
        return ""


@app.route('/search/<string:query>', methods=['GET'])
def trending_item_timerange(query):
    try:
        response = requests.get(backend_host + f'search/{query}')
        if response.status_code == 200:
            response_json = response.json()
            content_list = response_json['results']['movies']
            qr_code = response_json['results']['qr_code']

            return all_content_to_html(content_list, qr_code)
        else:
            return ""
    except Exception as e:
        return ""


def song_to_html(song):
    title = song['song_name']
    artist = song['name']
    country = song['country']
    created_at = song['created_at']
    age = song['age']
    html = '<div class="song-item">'
    html += f'<h3 class="title">Song: {title}</h3>'
    html += f'<p>Artist: {artist}</p>'
    html += f'<p>Country: {country}</p>'
    html += f'<p>Age: {age}</p>'
    html += f'<p>Created at: {created_at}</p>'
    html += f'</div>'
    return html


def all_songs_to_html(songs_list):
    html = '<h1>Songs: </h1>'
    html += '<div class="all-songs">'
    for song in songs_list:
        html += song_to_html(song)
    html += '</div>'
    return html


@app.route('/songs', methods=['GET'])
def get_songs():
    try:
        response = requests.get(backend_host + 'songs')

        if response.status_code == 200:
            data = response.text
            data = eval(data)
            return all_songs_to_html(data)
        else:
            return ""
    except Exception as e:
        return ""


if __name__ == '__main__':
    app.run()
