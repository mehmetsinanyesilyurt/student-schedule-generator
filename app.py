from flask import Flask, jsonify, request, make_response
from datetime import datetime

app = Flask(__name__)

# --- VERİ VE MANTIK (BACKEND) ---
schedule_data = []

def check_conflict(new_event):
    new_start = datetime.strptime(new_event['startTime'], '%H:%M')
    new_end = datetime.strptime(new_event['endTime'], '%H:%M')
    new_day = str(new_event['dayOfWeek'])

    for event in schedule_data:
        if new_day in event['daysOfWeek']:
            existing_start = datetime.strptime(event['startTime'], '%H:%M')
            existing_end = datetime.strptime(event['endTime'], '%H:%M')
            if (new_start < existing_end) and (new_end > existing_start):
                return True 
    return False

# --- DÜZELTİLMİŞ HTML (Kavga Çıkarmayan) ---
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Akıllı Ders Planlayıcı</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js'></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #FAFAFA; }
        .fc-theme-standard td, .fc-theme-standard th { border-color: #F1F5F9; }
        .fc-col-header-cell-cushion { color: #64748B; font-weight: 500; padding: 10px 0; }
        .fc-timegrid-slot-label-cushion { color: #94A3B8; font-size: 0.85rem; }
        .fc-event { border: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background-color: #E2E8F0; border-radius: 10px; }
    </style>
</head>
<body class="text-slate-800 h-screen flex overflow-hidden">
    <aside class="w-96 bg-white border-r border-slate-100 flex flex-col shadow-sm z-10">
        <div class="p-8 border-b border-slate-50">
            <h1 class="text-2xl font-semibold tracking-tight text-slate-900">Planlayıcı</h1>
            <p class="text-sm text-slate-400 mt-1">Haftalık ders programını yönet.</p>
        </div>
        <div class="p-8 flex-1 overflow-y-auto">
            <form id="addEventForm" class="space-y-6">
                <div class="space-y-2">
                    <label class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Ders Adı</label>
                    <input type="text" id="title" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 transition-all text-sm font-medium" placeholder="Örn: Veri Tabanı Yönetimi" required>
                </div>
                <div class="space-y-2">
                    <label class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Gün</label>
                    <div class="grid grid-cols-2 gap-2">
                        <label class="cursor-pointer"><input type="radio" name="day" value="1" class="peer sr-only" checked><div class="p-2 text-center text-sm border border-slate-200 rounded-md peer-checked:bg-slate-900 peer-checked:text-white transition-all hover:bg-slate-50">Pazartesi</div></label>
                        <label class="cursor-pointer"><input type="radio" name="day" value="2" class="peer sr-only"><div class="p-2 text-center text-sm border border-slate-200 rounded-md peer-checked:bg-slate-900 peer-checked:text-white transition-all hover:bg-slate-50">Salı</div></label>
                        <label class="cursor-pointer"><input type="radio" name="day" value="3" class="peer sr-only"><div class="p-2 text-center text-sm border border-slate-200 rounded-md peer-checked:bg-slate-900 peer-checked:text-white transition-all hover:bg-slate-50">Çarşamba</div></label>
                        <label class="cursor-pointer"><input type="radio" name="day" value="4" class="peer sr-only"><div class="p-2 text-center text-sm border border-slate-200 rounded-md peer-checked:bg-slate-900 peer-checked:text-white transition-all hover:bg-slate-50">Perşembe</div></label>
                        <label class="cursor-pointer"><input type="radio" name="day" value="5" class="peer sr-only"><div class="p-2 text-center text-sm border border-slate-200 rounded-md peer-checked:bg-slate-900 peer-checked:text-white transition-all hover:bg-slate-50">Cuma</div></label>
                    </div>
                </div>
                <div class="grid grid-cols-2 gap-4">
                    <div class="space-y-2"><label class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Başlangıç</label><input type="time" id="start" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm" required></div>
                    <div class="space-y-2"><label class="text-xs font-semibold text-slate-500 uppercase tracking-wider">Bitiş</label><input type="time" id="end" class="w-full p-3 bg-slate-50 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-900 text-sm" required></div>
                </div>
                <button type="submit" class="w-full py-3.5 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 focus:ring-4 focus:ring-slate-200 transition-all flex justify-center items-center gap-2">Ders Ekle</button>
            </form>
            <div id="messageBox" class="mt-4 hidden p-3 rounded-md text-sm font-medium"></div>
            <button onclick="clearSchedule()" class="mt-6 w-full py-2 text-red-500 text-sm font-medium hover:text-red-700 transition-colors">Tüm Programı Temizle</button>
        </div>
    </aside>
    <main class="flex-1 bg-white relative"><div id='calendar' class="h-full w-full p-8"></div></main>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            var calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek', locale: 'tr', firstDay: 1,
                slotMinTime: "08:00:00", slotMaxTime: "20:00:00", allDaySlot: false,
                headerToolbar: false, dayHeaderFormat: { weekday: 'long' },
                events: '/api/events', height: '100%', expandRows: true, eventColor: '#1e293b',
            });
            calendar.render();

            document.getElementById('addEventForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                const title = document.getElementById('title').value;
                const day = document.querySelector('input[name="day"]:checked').value;
                const start = document.getElementById('start').value;
                const end = document.getElementById('end').value;
                const msgBox = document.getElementById('messageBox');

                const response = await fetch('/api/add', {
                    method: 'POST', headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ title: title, dayOfWeek: day, startTime: start, endTime: end })
                });
                const result = await response.json();
                msgBox.className = response.ok ? "mt-4 p-3 rounded-md text-sm font-medium bg-green-50 text-green-700 block" : "mt-4 p-3 rounded-md text-sm font-medium bg-red-50 text-red-700 block";
                msgBox.innerText = (response.ok ? "Başarılı: " : "Hata: ") + result.message;
                if (response.ok) calendar.refetchEvents();
                setTimeout(() => { msgBox.classList.add('hidden'); }, 3000);
            });
        });
        async function clearSchedule() {
            if(confirm('Tüm program silinecek. Emin misin?')) { await fetch('/api/clear', { method: 'POST' }); location.reload(); }
        }
    </script>
</body>
</html>
"""

# --- ROTALAR (FIX) ---
@app.route('/')
def index():
    # render_template_string YERİNE doğrudan string'i response olarak dönüyoruz.
    # Böylece Flask HTML içindeki JS kodlarına dokunmuyor.
    response = make_response(HTML_CONTENT)
    response.headers['Content-Type'] = 'text/html; charset=utf-8'
    return response

@app.route('/api/events', methods=['GET'])
def get_events():
    return jsonify(schedule_data)

@app.route('/api/add', methods=['POST'])
def add_event():
    data = request.json
    try:
        if data['startTime'] >= data['endTime']:
            return jsonify({'status': 'error', 'message': 'Bitiş saati başlangıçtan önce olamaz!'}), 400

        if check_conflict(data):
            return jsonify({'status': 'error', 'message': 'DİKKAT: Bu saatte başka bir dersiniz var!'}), 409

        new_event = {
            'title': data['title'],
            'startTime': data['startTime'],
            'endTime': data['endTime'],
            'daysOfWeek': [data['dayOfWeek']], 
            'color': '#3B82F6'
        }
        schedule_data.append(new_event)
        return jsonify({'status': 'success', 'message': 'Ders programa eklendi.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/clear', methods=['POST'])
def clear_schedule():
    global schedule_data
    schedule_data = []
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    # Hata ayıklama modunu kapattık ki Cloud ortamında çökmesin
    app.run(debug=False, host='0.0.0.0', port=5000)
