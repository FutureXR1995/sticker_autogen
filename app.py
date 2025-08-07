from flask import Flask, render_template, send_file, jsonify
import os
import json

app = Flask(__name__)

def load_today_sets():
    """加载今日生成的贴图套件"""
    sets = []
    output_dir = "output"
    if os.path.exists(output_dir):
        for item in os.listdir(output_dir):
            if item.endswith('.zip'):
                set_name = item.replace('.zip', '')
                sets.append({
                    'name': set_name,
                    'zip_path': os.path.join(output_dir, item),
                    'preview_images': []  # 可以添加预览图路径
                })
    return sets

@app.route('/')
def index():
    """主页：展示所有贴图套件"""
    sets = load_today_sets()
    return render_template('index.html', sets=sets)

@app.route('/download/<set_name>')
def download_set(set_name):
    """下载指定贴图套件"""
    zip_path = os.path.join('output', f'{set_name}.zip')
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 