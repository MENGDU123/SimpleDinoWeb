if (!document.cookie.includes('visited=')) {
    alert('欢迎来到DiguaCloud！这是你的小饼干（Cookie）~ 请收好。\n\n' +
          '地瓜盒不会收集您的任何隐私，仅使用功能性Cookie，目的是记录您来过。\n\n' +
          '简单说，这个弹窗7天内只会出现一次，不会追踪你，请放心~\n\n' +
          '本网站前后端均由梦都本人设计，没有任何管理、设置、上传页面，所以请不要再无休止地扫描我的服务器的页面。'
    );
    document.cookie = 'visited=1; path=/; max-age=604800';
}