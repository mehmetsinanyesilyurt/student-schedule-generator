import streamlit as st
import streamlit.components.v1 as components

# Sayfa ayarlarını yapalım (Geniş ekran)
st.set_page_config(layout="wide", page_title="Ders Planlayıcı")

# --- HTML/CSS/JS KODU (LOGIC DAHİL) ---
# Flask yerine tüm mantığı JavaScript'e gömdüm. Böylece sunucuya ihtiyaç duymadan çalışır.
html_code = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src='https://cdn.jsdelivr.net/npm/fullcalendar@6.1.10/index.global.min.js'></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Inter', sans-serif; background-color: #FAFAFA; margin: 0; padding: 0; }
        .fc-theme-standard td, .fc-theme-standard th { border-color: #F1F5F9; }
        .fc-col-header-cell-cushion { color: #64748B; font-weight: 500; padding: 10px 0; }
        .fc-timegrid-slot-label-cushion { color: #94A3B8; font-size: 0.85rem; }
        .fc-event { border: none; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
        ::-webkit-scrollbar { width: 6px; }
        ::-webkit-scrollbar-thumb { background-color: #E2E8F0; border-radius: 10px; }
        
        /* Streamlit iframe uyumu için */
        #root { display: flex; height: 100vh; overflow: hidden; }
    </style>
</head>
<body>
    <div id="root">
        <aside class="w-80 bg-white border-r border-slate-100 flex flex-col shadow-sm z-10 overflow-y-auto">
            <div class="p-6 border-b border-slate-50">
                <h1 class="text-xl font-semibold tracking-tight text-slate-900">Planlayıcı</h1>
                <p class="text-xs text-slate-400 mt-1">Haftalık ders programı.</p>
            </div>
            <div class="p-6">
                <form id="addEventForm" class="space-y-5">
                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-500 uppercase">Ders Adı</label>
                        <input type="text" id="title" class="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900" placeholder="Örn: Veri Tabanı" required>
                    </div>
                    <div class="space-y-1">
                        <label class="text-xs font-semibold text-slate-500 uppercase">Gün</label>
                        <select id="day" class="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900">
                            <option value="1">Pazartesi</option>
                            <option value="2">Salı</option>
                            <option value="3">Çarşamba</option>
                            <option value="4">Perşembe</option>
                            <option value="5">Cuma</option>
                        </select>
                    </div>
                    <div class="grid grid-cols-2 gap-3">
                        <div class="space-y-1">
                            <label class="text-xs font-semibold text-slate-500 uppercase">Başlangıç</label>
                            <input type="time" id="start" class="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900" required>
                        </div>
                        <div class="space-y-1">
                            <label class="text-xs font-semibold text-slate-500 uppercase">Bitiş</label>
                            <input type="time" id="end" class="w-full p-2.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-slate-900" required>
                        </div>
                    </div>
                    <button type="submit" class="w-full py-3 bg-slate-900 text-white font-medium rounded-lg hover:bg-slate-800 text-sm transition-all">Ders Ekle</button>
                </form>
                <div id="msg" class="mt-4 hidden p-3 rounded-md text-xs font-medium"></div>
                <button onclick="calendar.getEventSources()[0].remove(); events=[];" class="mt-4 w-full py-2 text-red-500 text-xs font-medium hover:text-red-700">Temizle</button>
            </div>
        </aside>

        <main class="flex-1 bg-white relative">
            <div id='calendar' class="h-full w-full p-6"></div>
        </main>
    </div>

    <script>
        let events = []; // Verileri tarayıcı hafızasında tutuyoruz
        let calendar;

        document.addEventListener('DOMContentLoaded', function() {
            var calendarEl = document.getElementById('calendar');
            calendar = new FullCalendar.Calendar(calendarEl, {
                initialView: 'timeGridWeek',
                locale: 'tr',
                firstDay: 1,
                slotMinTime: "08:00:00",
                slotMaxTime: "20:00:00",
                allDaySlot: false,
                headerToolbar: false,
                dayHeaderFormat: { weekday: 'long' },
                height: '100%',
                expandRows: true,
                events: events,
                eventColor: '#3B82F6'
            });
            calendar.render();

            document.getElementById('addEventForm').addEventListener('submit', function(e) {
                e.preventDefault();
                
                let title = document.getElementById('title').value;
                let day = document.getElementById('day').value;
                let start = document.getElementById('start').value;
                let end = document.getElementById('end').value;
                let msg = document.getElementById('msg');

                // 1. Validasyon: Saat Kontrolü
                if (start >= end) {
                    showMsg('Bitiş saati başlangıçtan önce olamaz!', 'error');
                    return;
                }

                // 2. Çakışma Kontrolü (Conflict Detection)
                let hasConflict = events.some(event => {
                    if (event.daysOfWeek.includes(day)) {
                        return (start < event.endTime && end > event.startTime);
                    }
                    return false;
                });

                if (hasConflict) {
                    showMsg('DİKKAT: Bu saatte başka ders var!', 'error');
                    return;
                }

                // Ekleme
                let newEvent = {
                    title: title,
                    startTime: start,
                    endTime: end,
                    daysOfWeek: [day],
                    color: '#3B82F6'
                };
                
                events.push(newEvent);
                calendar.addEvent(newEvent);
                showMsg('Ders eklendi.', 'success');
            });

            function showMsg(text, type) {
                let msg = document.getElementById('msg');
                msg.innerText = text;
                msg.className = type === 'success' 
                    ? "mt-4 p-3 rounded-md text-xs font-medium bg-green-50 text-green-700 block"
                    : "mt-4 p-3 rounded-md text-xs font-medium bg-red-50 text-red-700 block";
                setTimeout(() => { msg.classList.add('hidden'); }, 3000);
            }
        });
    </script>
</body>
</html>
"""

# HTML'i Streamlit içine gömüyoruz (Boyutları tam ekran yapıyoruz)
components.html(html_code, height=800, scrolling=False)
