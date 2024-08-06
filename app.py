from flask import Flask, request, jsonify
import plistlib
import os

app = Flask(__name__)

def parse_itunes_library(file):
    plist = plistlib.load(file)

    playlists = plist.get('Playlists', [])
    tracks = plist.get('Tracks', {})

    playlist_dict = {}

    for playlist in playlists:
        playlist_name = playlist.get('Name')
        track_ids = [track['Track ID'] for track in playlist.get('Playlist Items', [])]
        file_paths = [tracks[str(track_id)].get('Location') for track_id in track_ids if str(track_id) in tracks]
        playlist_dict[playlist_name] = file_paths

    return playlist_dict

@app.route('/get_playlists', methods=['POST'])
def get_playlists():
    if 'xml_path' in request.form:
        xml_path = request.form.get('xml_path')
        if not xml_path or not os.path.exists(xml_path):
            return jsonify({'error': 'Valid xml_path is required'}), 400
        
        try:
            with open(xml_path, 'rb') as f:
                playlists = parse_itunes_library(f)
            return jsonify(playlists)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif 'xml_file' in request.files:
        xml_file = request.files['xml_file']
        try:
            playlists = parse_itunes_library(xml_file)
            return jsonify(playlists)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    else:
        return jsonify({'error': 'xml_path or xml_file is required'}), 400

if __name__ == '__main__':
    app.run(debug=True)
