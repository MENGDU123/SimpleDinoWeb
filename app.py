from flask import Flask,render_template,request
from datetime import datetime
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

@app.route('/notice')
def notice():
    notice_folder = os.path.join(app.config['upload_dir'], 'notice')
    file_info = []
    if os.path.isdir(notice_folder):
        for filename in os.listdir(notice_folder):
            try:
                if filename.endswith(".html") or filename.endswith(".md"):
                    filepath = os.path.join(notice_folder, filename)
                    mtime = os.path.getmtime(filepath)
                    time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                    file_info.append((filename, time_str))
            except FileNotFoundError:
                continue
        # 按修改时间倒序排序
        file_info.sort(key=lambda x: os.path.getmtime(os.path.join(notice_folder, x[0])), reverse=True)

    # 分页
    PER_PAGE = 15
    page = request.args.get('page', 1, type=int)
    total = len(file_info)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE if total > 0 else 1
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_files = file_info[start:end]   # 分页后的列表，每个元素是 (文件名, 时间字符串)

    return render_template('notice.html', notice_files=page_files, page=page, total_pages=total_pages)


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
