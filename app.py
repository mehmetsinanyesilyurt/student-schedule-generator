from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Verileri şimdilik RAM'de tutuyoruz. Proje büyürse SQL'e geçeriz.
# Yapı: [{'id': 1, 'title': 'Matematik', 'start': '2024-02-12T09:00:00', 'end': '...', 'day': 1}]
schedule_data = []

def check_conflict(new_event):
    """
    Risk Analizi: Yeni eklenen ders, mevcut derslerle çakışıyor mu?
    """
    new_start = datetime.strptime(new_event['startTime'], '%H:%M')
    new_end = datetime.strptime(new_event['endTime'], '%H:%M')
    new_day = int(new_event['dayOfWeek'])

    for event in schedule_data:
        # Aynı gün mü?
        if event['dayOfWeek'] == new_day:
            existing_start = datetime.strptime(event['startTime'], '%H:%M')
            existing_end = datetime.strptime(event['endTime'], '%H:%M')

            # Çakışma Mantığı (Overlap Logic)
            if (new_start < existing_end) and (new_end > existing_start):
                return True # Çakışma VAR!
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/events', methods=['GET'])
def get_events():
    return jsonify(schedule_data)

@app.route('/api/add', methods=['POST'])
def add_event():
    data = request.json
    
    # 1. Validasyon: Bitiş saati başlangıçtan önce olamaz
    if data['startTime'] >= data['endTime']:
        return jsonify({'status': 'error', 'message': 'Bitiş saati başlangıçtan önce olamaz!'}), 400

    # 2. Risk Analizi: Çakışma Kontrolü
    if check_conflict(data):
        return jsonify({'status': 'error', 'message': 'DİKKAT: Bu saatte başka bir dersiniz var!'}), 409

    # Veriyi FullCalendar formatına uygun saklayalım
    # Not: FullCalendar haftalık görünüm için tarih ister, biz burada
    # simülasyon için haftanın günlerini sabit bir referans tarihine mapleyeceğiz.
    schedule_data.append({
        'title': data['title'],
        'startTime': data['startTime'],
        'endTime': data['endTime'],
        'dayOfWeek': int(data['dayOfWeek']), # 1=Pazartesi, 2=Salı...
        'color': data.get('color', '#3B82F6') # Varsayılan Midas mavisi/indigo
    })
    
    return jsonify({'status': 'success', 'message': 'Ders başarıyla eklendi.'})

@app.route('/api/clear', methods=['POST'])
def clear_schedule():
    global schedule_data
    schedule_data = []
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # debug=False yapıyoruz çünkü Cloud ortamında 'reloader' hata verir.
    # host='0.0.0.0' yapıyoruz ki sunucu dış dünyaya açılabilsin.
    # port=5000 standarttır ama platforma göre değişebilir.
    app.run(debug=False, host='0.0.0.0', port=5000)
