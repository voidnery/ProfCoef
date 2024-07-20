import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
import requests
import json
import os
import urllib.parse
import http.server
import socketserver
import threading
import time

# Класс для обработки HTTP запросов
class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.getcwd(), **kwargs)

class RequestApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Отправка POST запроса с заголовками и JSON данными')

        self.is_first_request = True
        self.first_url = None
        self.port = 8000

        # Создание элементов GUI для ввода URL
        self.url_label = tk.Label(root, text='URL для отправки запроса:')
        self.url_label.pack(pady=(10, 0))

        self.url_entry = tk.Entry(root, width=50)
        self.url_entry.insert(0, "https://ru-partners.sporthub.bet/api/partner_feed/v1/matches/get_by_tournament_ids")
        self.url_entry.pack()

        # Создание элементов GUI для ввода заголовков
        self.header_label = tk.Label(root, text='Заголовки (headers):')
        self.header_label.pack(pady=(10, 0))

        # Заголовок для названия компании
        self.company_type_label = tk.Label(root, text='Тип заголовка для названия компании:')
        self.company_type_label.pack()

        self.company_type_entry = tk.Entry(root, width=50)
        self.company_type_entry.insert(0, "x-partner")
        self.company_type_entry.pack()

        self.company_value_label = tk.Label(root, text='Значение заголовка для названия компании:')
        self.company_value_label.pack()

        self.company_value_entry = tk.Entry(root, width=50)
        self.company_value_entry.insert(0, "bbtennis_studio")
        self.company_value_entry.pack()

        # Заголовок для JWT ключа
        self.jwt_type_label = tk.Label(root, text='Тип заголовка для JWT ключа:')
        self.jwt_type_label.pack()

        self.jwt_type_entry = tk.Entry(root, width=50)
        self.jwt_type_entry.insert(0, "x-access-token")
        self.jwt_type_entry.pack()

        self.jwt_value_label = tk.Label(root, text='Значение заголовка для JWT ключа:')
        self.jwt_value_label.pack()

        self.jwt_value_entry = tk.Entry(root, width=50)
        self.jwt_value_entry.insert(0, "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjQwODM2NTA3OTh9.OvERmas2kUXhHrM9aJjrMPKnih60XCPe3212LxmptgY")
        self.jwt_value_entry.pack()

        # Поле для ввода ID турнира
        self.tournament_id_label = tk.Label(root, text='ID турнира:')
        self.tournament_id_label.pack(pady=(10, 0))

        self.tournament_id_entry = tk.Entry(root, width=50)
        self.tournament_id_entry.pack()

        # Поле для ввода типа матча
        self.match_type_label = tk.Label(root, text='Тип матча:')
        self.match_type_label.pack(pady=(10, 0))

        self.match_type_entry = tk.Entry(root, width=50)
        self.match_type_entry.pack()

        # Кнопки для выбора типа матча
        self.prematch_button = tk.Button(root, text='Prematch', command=lambda: self.set_match_type("prematch"))
        self.prematch_button.pack(pady=(5, 0))

        self.live_button = tk.Button(root, text='Live', command=lambda: self.set_match_type("live"))
        self.live_button.pack(pady=(5, 0))

        # Поле для отображения отредактированного JSON (только для чтения)
        self.edited_json_label = tk.Label(root, text='Отредактированный JSON:')
        self.edited_json_label.pack(pady=(10, 0))

        self.edited_json_text = scrolledtext.ScrolledText(root, width=60, height=10)
        self.edited_json_text.pack()
        self.edited_json_text.config(state=tk.DISABLED)

        # Поле для отображения URL файла JSON для vMix Data Source
        self.json_url_label = tk.Label(root, text='URL JSON файла для vMix Data Source:')
        self.json_url_label.pack(pady=(10, 0))

        self.json_url_entry = tk.Entry(root, width=60)
        self.json_url_entry.pack()

        # Поле для отображения URL отправки запроса
        self.request_url_label = tk.Label(root, text='URL отправки запроса:')
        self.request_url_label.pack(pady=(10, 0))

        self.request_url_entry = tk.Entry(root, width=60)
        self.request_url_entry.pack()
        self.request_url_entry.config(state=tk.DISABLED)

        # Кнопка для отправки запроса
        self.send_button = tk.Button(root, text='Отправить запрос', command=self.send_request)
        self.send_button.pack(pady=(20, 10))

        # Запуск веб-сервера
        self.start_web_server()

    def start_web_server(self):
        # Запуск веб-сервера в отдельном потоке
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def run_server(self):
        while True:
            try:
                with socketserver.TCPServer(("", self.port), RequestHandler) as httpd:
                    print(f"Веб-сервер запущен на порту {self.port}")
                    httpd.serve_forever()
            except OSError:
                print(f"Порт {self.port} занят, пробую следующий порт...")
                self.port += 1

    def send_request(self):
        url = self.url_entry.get().strip()
        if self.is_first_request:
            self.first_url = url

        # Отображение URL отправки запроса
        self.request_url_entry.config(state=tk.NORMAL)
        self.request_url_entry.delete(0, tk.END)
        self.request_url_entry.insert(0, url)
        self.request_url_entry.config(state=tk.DISABLED)

        # Получение данных от пользователя для заголовков
        company_header_type = self.company_type_entry.get().strip()
        company_header_value = self.company_value_entry.get().strip()
        jwt_header_type = self.jwt_type_entry.get().strip()
        jwt_header_value = self.jwt_value_entry.get().strip()

        # Формирование заголовков (headers) для запроса
        headers = {
            company_header_type: company_header_value,
            jwt_header_type: jwt_header_value
        }

        # Получение данных для тела запроса
        tournament_id = self.tournament_id_entry.get().strip()
        match_type = self.match_type_entry.get().strip()

        # Формирование JSON данных для тела запроса
        json_data = {
            "locale": "ru",
            "tournament_ids": [int(tournament_id)] if tournament_id else [8318],
            "market_ids": [36041],
            "type": match_type if match_type else "prematch"
        }

        try:
            # Отправка POST запроса с заголовками и JSON данными
            response = requests.post(url, headers=headers, json=json_data)
            response.raise_for_status()  # Проверка на ошибки в запросе

            # Обработка и вывод ответа от сервера в текстовое поле
            edited_json = self.edit_json(response.json())
            edited_json = self.reorder_stakes(edited_json)
            self.edited_json_text.config(state=tk.NORMAL)
            self.edited_json_text.delete('1.0', tk.END)  # Очистка текущего содержимого
            self.edited_json_text.insert(tk.END, edited_json)  # Вставка отредактированных данных
            self.edited_json_text.config(state=tk.DISABLED)

            # Экспорт отредактированного JSON в файл
            self.export_json(edited_json)

            if self.is_first_request:
                messagebox.showinfo('Успех', 'Запрос успешно отправлен и JSON файл экспортирован!')
                self.is_first_request = False
                self.start_auto_update()

        except ValueError:
            messagebox.showerror('Ошибка', 'Некорректный формат JSON данных!')
        except requests.exceptions.RequestException as e:
            messagebox.showerror('Ошибка', f'Не удалось отправить запрос: {e}')

    def set_match_type(self, match_type):
        self.match_type_entry.delete(0, tk.END)
        self.match_type_entry.insert(0, match_type)

    def paste_from_clipboard(self):
        focused_widget = self.root.focus_get()

        try:
            clipboard_text = self.root.clipboard_get()
        except tk.TclError:
            return
        
        if focused_widget == self.url_entry:
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text)
        elif focused_widget == self.company_type_entry:
            self.company_type_entry.delete(0, tk.END)
            self.company_type_entry.insert(0, clipboard_text)
        elif focused_widget == self.company_value_entry:
            self.company_value_entry.delete(0, tk.END)
            self.company_value_entry.insert(0, clipboard_text)
        elif focused_widget == self.jwt_type_entry:
            self.jwt_type_entry.delete(0, tk.END)
            self.jwt_type_entry.insert(0, clipboard_text)
        elif focused_widget == self.jwt_value_entry:
            self.jwt_value_entry.delete(0, tk.END)
            self.jwt_value_entry.insert(0, clipboard_text)

    def edit_json(self, data):
        # Автоматическое удаление указанных ключей и их свойств
        keys_objects_to_remove = "id,tournament_id,type,start_dttm,has_live_tv,short_name,image,stake_id,market_id,outcome_id,period_id,market_name,period_name,is_active,scoreboard,scores,sequence,home_score,away_score,is_favorite"
        keys_objects_list = [item.strip() for item in keys_objects_to_remove.split(',')]
        self.remove_keys_objects(data, keys_objects_list)
        return json.dumps(data, ensure_ascii=False, indent=4)

    def reorder_stakes(self, data):
        data_dict = json.loads(data)
        if "matches" in data_dict:
            for match in data_dict["matches"]:
                if "stakes" in match:
                    stakes = match["stakes"]
                    if stakes and stakes[0]["name"] == "П2":
                        stakes.reverse()
        return json.dumps(data_dict, ensure_ascii=False, indent=4)

    def remove_keys_objects(self, data, keys_objects_list):
        if isinstance(data, dict):
            keys_to_delete = []
            for key in data:
                if key in keys_objects_list:
                    keys_to_delete.append(key)
                elif isinstance(data[key], (dict, list)):
                    self.remove_keys_objects(data[key], keys_objects_list)
            for key in keys_to_delete:
                del data[key]
        elif isinstance(data, list):
            for item in data:
                self.remove_keys_objects(item, keys_objects_list)

    def export_json(self, edited_json):
        try:
            # Открываем окно для сохранения файла JSON
            json_filename = 'edited_data.json'
            json_file_path = os.path.join(os.getcwd(), json_filename)
            with open(json_file_path, 'w', encoding='utf-8') as f:
                f.write(edited_json)

            # Получение URL для файла JSON
            json_url = self.get_local_file_url(json_file_path)
            self.json_url_entry.config(state=tk.NORMAL)
            self.json_url_entry.delete(0, tk.END)
            self.json_url_entry.insert(0, json_url)
        except ValueError:
            messagebox.showerror('Ошибка', 'Некорректный формат JSON данных при экспорте!')

    def start_auto_update(self):
        self.update_thread = threading.Thread(target=self.auto_update)
        self.update_thread.daemon = True
        self.update_thread.start()

    def auto_update(self):
        while True:
            time.sleep(30)  # Задержка 30 секунд
            self.send_request_auto()

    def send_request_auto(self):
        if not self.first_url:
            return

        url = self.first_url

        # Отображение URL отправки запроса
        self.request_url_entry.config(state=tk.NORMAL)
        self.request_url_entry.delete(0, tk.END)
        self.request_url_entry.insert(0, url)
        self.request_url_entry.config(state=tk.DISABLED)

        # Получение данных от пользователя для заголовков
        company_header_type = self.company_type_entry.get().strip()
        company_header_value = self.company_value_entry.get().strip()
        jwt_header_type = self.jwt_type_entry.get().strip()
        jwt_header_value = self.jwt_value_entry.get().strip()

        # Формирование заголовков (headers) для запроса
        headers = {
            company_header_type: company_header_value,
            jwt_header_type: jwt_header_value
        }

        # Получение данных для тела запроса
        tournament_id = self.tournament_id_entry.get().strip()
        match_type = self.match_type_entry.get().strip()

        # Формирование JSON данных для тела запроса
        json_data = {
            "locale": "ru",
            "tournament_ids": [int(tournament_id)] if tournament_id else [8318],
            "market_ids": [36041],
            "type": match_type if match_type else "prematch"
        }

        try:
            # Отправка POST запроса с заголовками и JSON данными
            response = requests.post(url, headers=headers, json=json_data)
            response.raise_for_status()  # Проверка на ошибки в запросе

            # Обработка и вывод ответа от сервера в текстовое поле
            edited_json = self.edit_json(response.json())
            edited_json = self.reorder_stakes(edited_json)
            self.edited_json_text.config(state=tk.NORMAL)
            self.edited_json_text.delete('1.0', tk.END)  # Очистка текущего содержимого
            self.edited_json_text.insert(tk.END, edited_json)  # Вставка отредактированных данных
            self.edited_json_text.config(state=tk.DISABLED)

            # Экспорт отредактированного JSON в файл
            self.export_json(edited_json)

        except ValueError:
            print('Некорректный формат JSON данных при автоматическом запросе!')
        except requests.exceptions.RequestException as e:
            print(f'Не удалось отправить запрос при автоматическом обновлении: {e}')

    def get_local_file_url(self, file_path):
        # Формирование локального URL для файла JSON
        local_url = f'http://localhost:{self.port}/{os.path.basename(file_path)}'
        return local_url

# Создание главного окна приложения
root = tk.Tk()
app = RequestApp(root)
root.mainloop()
