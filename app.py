from flask import Flask, render_template, send_file, jsonify, request, redirect, url_for, flash
import os
import json
import subprocess
import threading
import time
from datetime import datetime
from data_scraper import get_hot_topics
from idea_generator import make_ideas
from image_generator import create_stickers
from packager import package_set

app = Flask(__name__)
app.secret_key = 'sticker_generator_secret_key'

# 全局状态
generation_status = {
    'running': False,
    'progress': '',
    'results': [],
    'error': None
}

def load_today_sets():
    """加载今日生成的贴图套件"""
    sets = []
    output_dir = "output"
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            if item.endswith('.zip'):
                set_name = item.replace('.zip', '')
                # 获取文件修改时间
                file_path = os.path.join(output_dir, item)
                mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                sets.append({
                    'name': set_name,
                    'zip_path': file_path,
                    'created_time': mod_time.strftime('%Y-%m-%d %H:%M'),
                    'file_size': f"{os.path.getsize(file_path) // 1024} KB"
                })
    return sorted(sets, key=lambda x: x['created_time'], reverse=True)

def estimate_cost(mode):
    """估算成本"""
    if mode == 'ideas_only':
        return {'gpt4': 0.30, 'dalle': 0, 'total': 0.30, 'rmb': 2.1}
    elif mode == 'budget':
        return {'gpt4': 0.15, 'dalle': 0.32, 'total': 0.47, 'rmb': 3.3}
    else:  # normal
        return {'gpt4': 0.30, 'dalle': 0.64, 'total': 0.94, 'rmb': 6.6}

@app.route('/')
def index():
    """主页：功能控制面板"""
    sets = load_today_sets()
    return render_template('index.html', 
                         sets=sets, 
                         status=generation_status,
                         costs={
                             'ideas_only': estimate_cost('ideas_only'),
                             'budget': estimate_cost('budget'),
                             'normal': estimate_cost('normal')
                         })

@app.route('/hot_topics')
def hot_topics():
    """获取热词"""
    try:
        topics = get_hot_topics(force_refresh=True)
        return jsonify({'success': True, 'topics': topics[:10]})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generate_ideas', methods=['POST'])
def generate_ideas():
    """生成创意"""
    try:
        topics = request.json.get('topics', [])
        if not topics:
            return jsonify({'success': False, 'error': '请选择热词'})
        
        # 限制最多2个话题
        selected_topics = topics[:2]
        ideas = make_ideas(selected_topics, mock=False)
        
        return jsonify({
            'success': True, 
            'ideas': ideas,
            'cost': estimate_cost('ideas_only')
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def run_generation(ideas, mode):
    """后台运行图片生成"""
    global generation_status
    
    try:
        generation_status['running'] = True
        generation_status['progress'] = '开始生成图片...'
        generation_status['error'] = None
        
        all_zip_paths = []
        
        for idx, idea in enumerate(ideas, 1):
            generation_status['progress'] = f'正在生成第{idx}套贴图: {idea["character"]}'
            
            # 生成图片
            out_dir = f"output/set_{idx}_{int(time.time())}"
            image_paths = create_stickers(idea, mock=False, out_dir=out_dir)
            
            # 打包
            zip_path = package_set(image_paths, idea, out_dir="output")
            all_zip_paths.append(zip_path)
            
            generation_status['progress'] = f'第{idx}套贴图生成完成'
        
        generation_status['running'] = False
        generation_status['progress'] = f'全部完成！生成了{len(all_zip_paths)}套贴图'
        generation_status['results'] = all_zip_paths
        
    except Exception as e:
        generation_status['running'] = False
        generation_status['error'] = str(e)
        generation_status['progress'] = f'生成失败: {e}'

@app.route('/generate_images', methods=['POST'])
def generate_images():
    """生成图片（异步）"""
    if generation_status['running']:
        return jsonify({'success': False, 'error': '已有生成任务在运行中'})
    
    try:
        ideas = request.json.get('ideas', [])
        mode = request.json.get('mode', 'budget')  # budget 或 normal
        
        if not ideas:
            return jsonify({'success': False, 'error': '请先生成创意'})
        
        # 根据模式限制数量
        if mode == 'budget':
            ideas = ideas[:1]
        
        # 启动后台任务
        thread = threading.Thread(target=run_generation, args=(ideas, mode))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True, 
            'message': '开始生成图片，请稍候...',
            'cost': estimate_cost(mode)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/generation_status')
def get_generation_status():
    """获取生成状态"""
    return jsonify(generation_status)

@app.route('/download/<set_name>')
def download_set(set_name):
    """下载指定贴图套件"""
    zip_path = os.path.join('output', f'{set_name}.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001) 