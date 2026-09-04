import os
import glob
from flask import Flask, render_template, jsonify

app = Flask(__name__)

MAPS_DIR = os.path.join(app.root_path, 'static', 'maps')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/maps')
def get_maps():
    """إرجاع قائمة بكافة الخرائط المتاحة مرتّبة زمنياً"""
    files = sorted(glob.glob(os.path.join(MAPS_DIR, "precip_f*.png")))
    maps_info = []
    
    for filepath in files:
        filename = os.path.basename(filepath)
        try:
            forecast_hour = filename.split('_f')[1].split('.')[0]
            maps_info.append({
                'url': f'/static/maps/{filename}',
                'hour': f"+{int(forecast_hour)}h",
                'forecast_num': int(forecast_hour)
            })
        except IndexError:
            continue
        
    return jsonify(maps_info)

if __name__ == '__main__':
    os.makedirs(MAPS_DIR, exist_ok=True)
    # استخدام المنفذ المخصص من Render أو 5000 محلياً
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)