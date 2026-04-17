from flask import Flask,render_template,request,abort
from importlib.metadata import version
from optparse import OptionParser
from datetime import datetime
import platform
import psutil
import random
import sys
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
            raise FileNotFoundError("Music file is None!")
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
                if filename.endswith(".html") or filename.endswith(".pdf"):
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
    page_files = file_info[start:end]   # 分页后的列表

    return render_template('notice.html', notice_files=page_files, page=page, total_pages=total_pages)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/hidden')
def hidden():
    #如果启动参数没有-e或者--extra，返回403
    if not options.hidden:
        abort(403)

    #隐藏页-系统信息
    flask_info = version('flask')
    python_info = sys.version
    app_info = "SimpleDinoWeb Version: 26.4.0 (Design by Cream_MENGDU.)"
    #隐藏页-运行状态
    system_name = platform.system()
    system_release = platform.release()
    system_machine = platform.machine()
    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    memory = psutil.virtual_memory()
    #读取/static/hidden文件夹
    hidden_folder = os.path.join(app.config['upload_dir'], 'hidden')
    hidden_files = []
    if os.path.isdir(hidden_folder):
        for filename in os.listdir(hidden_folder):
            file_path = os.path.join(hidden_folder, filename)
            if os.path.isfile(file_path):
                hidden_files.append(filename)
        hidden_files.sort()

    return render_template(
        'hidden.html',
        flask_info=flask_info,python_info=python_info,app_info=app_info,
        system_name=system_name,system_release=system_release,system_machine=system_machine,
        cpu_percent = cpu_percent,memory = memory,
        hidden_files = hidden_files
    )
@app.errorhandler(404)
def page_not_found(error):
    error_title = "404 Not Found!"
    error_info = "The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."
    return render_template("abandon.html",error_info = error_info,error_title = error_title),404

@app.errorhandler(403)
def forbidden(error):
    error_title = "403 Forbidden!"
    error_info = "You don't have the permission to access the requested resource. It is either read-protected or not readable by the server."
    return render_template("abandon.html",error_info = error_info,error_title = error_title),403

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-i", "--ip", dest="ip", type="string",help="listen address",default="0.0.0.0")
    parser.add_option("-p", "--port", dest="port", type="int",help="port number",default="5000")
    parser.add_option("-d", "--debug", dest="debug", action="store_true",help="enable debug mode")
    parser.add_option("-e","--extra",dest="hidden",action="store_true",help="show hidden page")
    parser.add_option("-v", "--version", dest="version_info",action="store_true",help="show version information")
    (options, args) = parser.parse_args()

    if options.version_info:
        print(f"Flask Version: {version('flask')}")
        print(f"Python Version: {sys.version}")
        print("SimpleDinoWeb Version: 26.4.0 (Design by Cream_MENGDU.)")
        #如果参数里包含-v或者--version，只输出版本信息而不启动。
        sys.exit(0)

    print("Please use nginx to proxy the application, or use a WSGI server directly..")
    app.run(host=options.ip, port=options.port,debug=options.debug)