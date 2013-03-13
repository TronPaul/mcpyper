from flask import Flask, current_app, request, send_file
from mcserver import MinecraftServer

app = Flask(__name__)
app.config['DEBUG'] = True
app.server = MinecraftServer()

@app.route('/status')
def status():
    current_app.server.status()
    return ('', 200, '')

@app.route('/clean', methods=['POST'])
def clean():
    current_app.server.clean()
    return ('', 200, '')

@app.route('/install', methods=['POST'])
def install():
    current_app.server.install()
    return ('', 201, '')

@app.route('/uninstall', methods=['POST'])
def uninstall():
    current_app.server.uninstall()
    return ('', 200, '')

@app.route('/update', methods=['POST'])
def update():
    current_app.server.update()
    return ('', 200, '')

@app.route('/start', methods=['POST'])
def start():
    current_app.server.start()
    return ('', 200, '')

@app.route('/stop', methods=['POST'])
def stop():
    current_app.server.stop()
    return ('', 200, '')

@app.route('/restart', methods=['POST'])
def restart():
    current_app.server.restart()
    return ('', 200, '')

@app.route('/kill', methods=['POST'])
def kill():
    current_app.server.kill()
    return ('', 200, '')

@app.route('/rcon', methods=['POST'])
def rcon():
    command = request.form['command']
    current_app.server.rcon(command)
    return ('', 200, '')

@app.route('/world')
def get_world():
    # TODO: rate limit or cache
    path = current_app.server.compress_world('world.tar.gz')
    return send_file(path)

@app.route('/world', methods=['DELETE'])
def delete_world():
    current_app.server.delete_world()
    return ('', 200, '')

if __name__ == '__main__':
    app.run()
