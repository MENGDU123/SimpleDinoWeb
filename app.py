import time
import threading
import random
import requests
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, render_template, request, abort, jsonify
from importlib.metadata import version
from optparse import OptionParser
from datetime import datetime
import platform
import textwrap
import psutil
import sys
import os

app = Flask(__name__)

#友链心跳配置
HEARTBEAT_INTERVAL = 30
HEARTBEAT_JITTER = 15 #抖动时长
CHECK_TIMEOUT = 5
MAX_WORKERS = 4

#存放状态缓存
_friend_cache = {}
_cache_lock = threading.Lock()
_stop_event = threading.Event()

#读取友谊链接
def _check_one(link):
    try:
        start = time.perf_counter()
        r = requests.get(link['url'], timeout=CHECK_TIMEOUT, allow_redirects=True)
        ms = (time.perf_counter() - start) * 1000
        return link['url'], f"[{r.status_code} {round(ms)}ms]"
    except Exception:
        return link['url'], "[离线]"

def _heartbeat_loop():
    """后台线程：每隔 HEARTBEAT_INTERVAL 秒刷新一次友链状态到缓存。"""
    while not _stop_event.is_set():
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
            results = list(pool.map(_check_one, FRIEND_LINKS))

        now = time.time()
        with _cache_lock:
            for url, status in results:
                _friend_cache[url] = {'status': status, 'checked_at': now}
        # 睡到下一轮，加随机抖动
        sleep_time = HEARTBEAT_INTERVAL + random.uniform(-HEARTBEAT_JITTER, HEARTBEAT_JITTER)
        if _stop_event.wait(sleep_time):
            break

def start_heartbeat():
    """启动友链心跳线程。"""
    t = threading.Thread(target=_heartbeat_loop, name='friend-heartbeat', daemon=True)
    t.start()
    return t

#定义友链数据
FRIEND_LINKS = [
    {
        'name': '浅水咲',
        'url': 'https://www.bilibili.com/read/readlist/rl1061728?spm_id_from=333.1387.0.0',
        'desc': '🪄喜欢魔法少女请关注B站~我们都称呼他为Saki！'
    },
    {
        'name': 'peter2500zz',
        'url': 'https://mygo.plus/',
        'desc': '✨我有一个写代码很厉害的朋友，晴雨表mygo.plus。'
    },
    {
        'name': 'Yasaitori',
        'url': 'https://yatori.cc',
        'desc': '🐟喜欢摸鱼，擅长睡觉，Toriest。'
    }
]

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

    #读取友链状态（只读缓存）
    with _cache_lock:
        friend_links_with_status = []
        for link in FRIEND_LINKS:
            cached = _friend_cache.get(link['url'])
            status = cached['status'] if cached else '[未知]'
            friend_links_with_status.append({
                'name': link['name'],
                'url': link['url'],
                'desc': link['desc'],
                'status': status
            })

    return render_template('index.html',selected_music = selected_music,resource_file = resource_files, friend_links = friend_links_with_status)

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

@app.route('/nuoshui')
def nuoshui():
    #与文章页完全一致，不过遍历的目录不同
    nuoshui_folder = os.path.join(app.config['upload_dir'], 'nuoshui')
    file_info = []
    if os.path.isdir(nuoshui_folder):
        for filename in os.listdir(nuoshui_folder):
            try:
                if filename.endswith(".pdf"):
                    filepath = os.path.join(nuoshui_folder, filename)
                    mtime = os.path.getmtime(filepath)
                    time_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                    file_info.append((filename, time_str))
            except FileNotFoundError:
                continue
        file_info.sort(key=lambda x: os.path.getmtime(os.path.join(nuoshui_folder, x[0])), reverse=True)

    #分页
    PER_PAGE = 20
    page = request.args.get('page', 1, type=int)
    total = len(file_info)
    total_pages = (total + PER_PAGE - 1) // PER_PAGE if total > 0 else 1
    if page < 1:
        page = 1
    if page > total_pages and total_pages > 0:
        page = total_pages
    start = (page - 1) * PER_PAGE
    end = start + PER_PAGE
    page_files = file_info[start:end]

    return render_template('nuoshui.html', nuoshui_files=page_files, page=page, total_pages=total_pages)

@app.route('/about')
def about():
    return render_template('about.html')

#君子协议
@app.route('/robots.txt')
def robots_txt():
    content = textwrap.dedent("""
        User-agent: *
        Disallow: /
        Allow: /$
        Allow: /about$
    """).strip()
    return content, 200, {'Content-Type': 'text/plain'}

@app.route('/hidden')
def hidden():
    #如果启动参数没有-e或者--extra，返回403
    if not options.hidden:
        abort(403)

    #隐藏页-系统信息
    flask_info = version('flask')
    python_info = sys.version
    app_info = "SimpleDinoWeb Version: 26.9.28b (Design by Cream_MENGDU.)"
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
        print("SimpleDinoWeb Version: 26.9.28b (Design by Cream_MENGDU.)")
        #如果参数里包含-v或者--version，只输出版本信息而不启动。
        sys.exit(0)

    if not options.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        start_heartbeat()

    print("Please use nginx to proxy the application, or use a WSGI server directly..")
    app.run(host=options.ip, port=options.port,debug=options.debug)


