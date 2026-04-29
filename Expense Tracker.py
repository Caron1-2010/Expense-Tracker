import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600") # Установим начальный размер окна

        self.expenses = []
        self.data_file = "data.json"
        self.load_expenses() # Загружаем данные при запуске

        self.create_widgets()

    def create_widgets(self):
        # --- Фрейм для ввода расходов ---
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        # Поле "Сумма"
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Поле "Категория"
        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = ttk.Entry(input_frame, width=20)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Поле "Дата"
        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Устанавливаем текущую дату по умолчанию

        # Кнопка "Добавить расход"
        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)

        input_frame.columnconfigure(1, weight=1) # Растягиваем поле ввода суммы

        # --- Фрейм для отображения расходов ---
        table_frame = ttk.LabelFrame(self.root, text="Список расходов", padding="10")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Таблица (Treeview)
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Amount", "Category", "Date"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Amount", text="Сумма")
        self.tree.heading("Category", text="Категория")
        self.tree.heading("Date", text="Дата")

        self.tree.column("ID", width=50, anchor=tk.CENTER)
        self.tree.column("Amount", width=100, anchor=tk.E) # Выравнивание по правому краю
        self.tree.column("Category", width=150)
        self.tree.column("Date", width=100, anchor=tk.CENTER)

        # Прокрутка для таблицы
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.load_treeview() # Заполняем таблицу данными

        # --- Фрейм для фильтрации и суммирования ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация и подсчет", padding="10")
        filter_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        # Фильтр по дате
        ttk.Label(filter_frame, text="Начальная дата:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_filter_entry = ttk.Entry(filter_frame, width=15)
        self.start_date_filter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(filter_frame, text="Конечная дата:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.end_date_filter_entry = ttk.Entry(filter_frame, width=15)
        self.end_date_filter_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.category_filter_entry = ttk.Entry(filter_frame, width=15)
        self.category_filter_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        # Кнопки фильтрации и сброса
        filter_buttons_frame = ttk.Frame(filter_frame)
        filter_buttons_frame.grid(row=3, column=0, columnspan=2, pady=10)

        self.filter_button = ttk.Button(filter_buttons_frame, text="Фильтровать", command=self.filter_expenses)
        self.filter_button.grid(row=0, column=0, padx=5)

        self.reset_filter_button = ttk.Button(filter_buttons_frame, text="Сбросить фильтр", command=self.reset_filter)
        self.reset_filter_button.grid(row=0, column=1, padx=5)

        # Подсчет суммы
        self.total_sum_label = ttk.Label(filter_frame, text="Общая сумма: 0.00", font=("Arial", 12, "bold"))
        self.total_sum_label.grid(row=4, column=0, columnspan=2, pady=10)

        filter_frame.columnconfigure(1, weight=1)

        # --- Меню ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=filemenu)
        filemenu.add_command(label="Сохранить как...", command=self.save_expenses_as)
        filemenu.add_command(label="Загрузить...", command=self.load_expenses_dialog)
        filemenu.add_separator()
        filemenu.add_command(label="Выход", command=self.root.quit)

        # --- Конфигурация растягивания ---
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0) # Фрейм фильтров не будет растягиваться по ширине
        self.root.grid_rowconfigure(1, weight=1) # Таблица будет растягиваться по высоте

    def validate_amount(self, text):
        """Проверяет, является ли введенное значение положительным числом."""
        if text.isdigit() or text == "":
            return True
        if text.replace('.', '', 1).isdigit() and text.count('.') < 2:
            return True
        return False

    def validate_date(self, date_text):
        """Проверяет, соответствует ли дата формату YYYY-MM-DD."""
        if not date_text:
            return True # пустая строка допустима
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        """Добавляет новый расход в список."""
        amount_str = self.amount_entry.get()
        category = self.category_entry.get().strip()
        date_str = self.date_entry.get().strip()

        # Валидация ввода
        if not amount_str or not category or not date_str:
            messagebox.showwarning("Внимание", "Все поля (Сумма, Категория, Дата) должны быть заполнены.")
            return

        if not self.validate_amount(amount_str):
            messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
            return

        if not self.validate_date(date_str):
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате YYYY-MM-DD.")
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка ввода", "Сумма должна быть положительным числом.")
                return
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Некорректное значение суммы.")
            return

        # Формируем ID, если список пуст, иначе берем последний ID + 1
        expense_id = 1 if not self.expenses else max(exp["id"] for exp in self.expenses) + 1

        new_expense = {
            "id": expense_id,
            "amount": amount,
            "category": category,
            "date": date_str
        }
        self.expenses.append(new_expense)
        self.update_treeview()
        self.save_expenses()
        self.clear_input_fields()
        messagebox.showinfo("Успех", "Расход успешно добавлен.")

    def clear_input_fields(self):
        """Очищает поля ввода после добавления расхода."""
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d")) # Снова устанавливаем текущую дату

    def load_expenses(self):
        """Загружает расходы из JSON файла."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
                    # Преобразование строк дат обратно в объекты date, если нужно для логики
                    # for exp in self.expenses:
                    #     exp['date'] = datetime.strptime(exp['date'], "%Y-%m-%d").date()
            except (json.JSONDecodeError, IOError) as e:
                messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные: {e}")
                self.expenses = []
        else:
            self.expenses = []

    def save_expenses(self):
        """Сохраняет расходы в JSON файл."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, indent=4, ensure_ascii=False)
            # Git commit
            self.commit_changes("Сохранение расходов")
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")

    def commit_changes(self, message="Автосохранение"):
        """Добавляет изменения в Git и делает коммит."""
        try:
            # Проверяем, что мы в Git репозитории
            if os.path.exists(".git"):
                os.system(f'git add .') # Добавляем все измененные файлы
                os.system(f'git commit -m "{message}"')
                print(f"Git commit выполнен: '{message}'")
            else:
                print("Git репозиторий не найден. Коммит пропускается.")
        except Exception as e:
            print(f"Ошибка при выполнении Git команды: {e}")


    def load_expenses_dialog(self):
        """Открывает диалоговое окно для выбора файла и загрузки расходов."""
        filepath = filedialog.askopenfilename(
            initialdir=".", # Начать поиск из текущей директории
            title="Выберите файл с расходами",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )
        if not filepath:
            return

        self.data_file = filepath # Обновляем путь к файлу
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                self.expenses = json.load(f)
            self.update_treeview()
            self.total_sum_label.config(text="Общая сумма: 0.00") # Сбрасываем сумму после загрузки
            messagebox.showinfo("Успех", f"Данные успешно загружены из {os.path.basename(filepath)}")
        except (json.JSONDecodeError, IOError) as e:
            messagebox.showerror("Ошибка загрузки", f"Не удалось загрузить данные из {os.path.basename(filepath)}: {e}")
            self.expenses = [] # Сбрасываем при ошибке

    def save_expenses_as(self):
        """Открывает диалоговое окно для сохранения расходов в новый файл."""
        filepath = filedialog.asksaveasfilename(
            initialdir=".",
            title="Сохранить расходы как",
            defaultextension=".json",
            filetypes=(("JSON файлы", "*.json"), ("Все файлы", "*.*"))
        )
        if not filepath:
            return

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Успех", f"Данные успешно сохранены в {os.path.basename(filepath)}")
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {e}")


    def update_treeview(self, data=None):
        """Обновляет содержимое таблицы (Treeview)."""
        # Очищаем старые записи
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Вставляем новые записи. Если data не предоставлено, используем self.expenses
        sourceamount']:.2f}", # Форматируем сумму до 2 знаков после запятой
                expense["category"],
                expense["date"]
            ))

    def load_treeview(self):
        """Первоначальное заполнение таблицы данными."""
        self.update_treeview() # Используем self.expenses по умолчанию
        self.calculate_total_sum() # Считаем начальную сумму

    def filter_expenses(self):
        """Фильтрует расходы по заданным критериям."""
        start_date_str = self.start_date_filter_entry.get().strip()
        end_date_str = self.end_date_filter_entry.get().strip()
        category_filter = self.category_filter_entry.get().strip().lower()

        filtered_list = self.expenses

        # Фильтр по начальной дате
        if start_date_str:
            if not self.validate_date(start_date_str):
                messagebox.showerror("Ошибка ввода", "Начальная дата должна быть в формате YYYY-MM-DD.")
                return
            try:
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                filtered_list = [exp for exp in filtered_list if datetime.strptime(exp["date"], "%Y-%m-%d") >= start_date]
            except ValueError: # Если в данных есть некорректные даты
                pass # Пропускаем некорректные записи

        # Фильтр по конечной дате
        if end_date_str:
            if not self.validate_date(end_date_str):
                messagebox.showerror("Ошибка ввода", "Конечная дата должна быть в формате YYYY-MM-DD.")
                return
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                filtered_list = [exp for exp in filtered_list if datetime.strptime(exp["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                pass

        # Фильтр по категории
        if category_filter:
            filtered_list = [exp for exp in filtered_list if exp["category"].lower() == category_filter]

        self.update_treeview(filtered_list)
        self.calculate_total_sum(filtered_list)

    def reset_filter(self):
        """Сбрасывает поля фильтра и обновляет таблицу."""
        self.start_date_filter_entry.delete(0, tk.END)
        self.end_date_filter_entry.delete(0, tk.END)
        self.category_filter_entry.delete(0, tk.END)
        self.update_treeview()
        self.calculate_total_sum()

    def calculate_total_sum(self, data=None):
        """Подсчитывает общую сумму расходов (для всех или отфильтрованных)."""
        source_data = data if data is not None else self.expenses
        total = sum(exp["amount"] for exp in source_data)
        self.total_sum_label.config(text=f"Общая сумма: {total:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
