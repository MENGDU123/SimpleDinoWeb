from flask import Flask, render_template
import random
import os

app = Flask(__name__)

app.config['upload_dir'] = 'static'
@app.route('/')
def index():
    #读取/static/music目录
    music_folder = os.path.join(app.config['upload_dir'],'music')
    selected_music = None
    if os.path.isdir(music_folder):
        music_files = []
        for filename in os.listdir(music_folder):
            if filename.endswith(".mp3"):
                #如果是以mp3结尾的文件将会被加入列表。
                music_files.append(filename)
        if music_files:
            selected_music = random.choice(music_files)
        else:
            raise FileNotFoundError("Music file not found!")
            #如果内容为空，抛出错误，停止运行。

    #读取/static/resource目录
    resource_folder = os.path.join(app.config['upload_dir'], 'resource')
    resource_files = []
    if os.path.isdir(resource_folder):
        for filename in os.listdir(resource_folder):
            #排除文件夹，防止意外。
            file_path = os.path.join(resource_folder, filename)
            if os.path.isfile(file_path):
                resource_files.append(filename)
        resource_files.sort()

    return render_template('index.html',selected_music = selected_music,resource_file = resource_files)

@app.route('/about')
def about():
    return render_template('about.html')



if __name__ == '__main__':
    app.run(debug=True)
