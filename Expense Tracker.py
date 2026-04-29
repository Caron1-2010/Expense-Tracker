import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import json
import os
import subprocess # Для работы с Git

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("800x600") # Увеличим размер окна

        self.expenses = []
        self.data_file = "data.json" # Имя файла для хранения данных

        # Проверка и загрузка данных при запуске
        self.load_expenses()

        self.create_widgets()
        self.load_treeview() # Загружаем данные в таблицу после создания виджетов

        # Проверка существования Git репозитория
        if not self.is_git_repo():
            messagebox.showwarning("Git", "Git репозиторий не найден. Автосохранение в Git будет недоступно.")


    def is_git_repo(self):
        """Проверяет, является ли текущая директория Git репозиторием."""
        try:
            # Проверяем наличие .git папки или выполняем команду git status
            subprocess.run(["git", "status"], check=True, capture_output=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def commit_changes(self, message="Автосохранение"):
        """Совершает коммит изменений в Git."""
        if self.is_git_repo():
            try:
                # Добавляем все изменения
                subprocess.run(["git", "add", "."], check=True, capture_output=True, text=True)
                # Делаем коммит
                commit_result = subprocess.run(
                    ["git", "commit", "-m", message],
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding='utf-8' # Явно указываем кодировку
                )
                print(f"Git commit successful: {commit_result.stdout}")
            except subprocess.CalledProcessError as e:
                print(f"Git commit failed: {e.stderr}")
                # Если ошибка связана с отсутствием изменений, это нормально
                if "nothing to commit" not in e.stderr and "nothing added to commit" not in e.stderr:
                     messagebox.showerror("Git Error", f"Ошибка коммита: {e.stderr}")
            except FileNotFoundError:
                 print("Git command not found. Make sure Git is installed and in your PATH.")
        else:
            print("Git repository not found. Skipping commit.")


    def create_widgets(self):
        """Создает все элементы GUI."""
        # --- Фрейм для ввода данных ---
        input_frame = ttk.LabelFrame(self.root, text="Новый расход", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.amount_entry = ttk.Entry(input_frame, validate="key", validatecommand=(self.root.register(self.validate_amount), '%P'))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_entry = ttk.Entry(input_frame)
        self.category_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.date_entry = ttk.Entry(input_frame)
        self.date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        # Устанавливаем текущую дату по умолчанию
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.add_button = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_button.grid(row=3, column=0, columnspan=2, padx=5, pady=10)

        input_frame.columnconfigure(1, weight=1) # Позволяет полю ввода растягиваться

        # --- Фрейм для таблицы расходов ---
        table_frame = ttk.Frame(self.root, padding="10")
        table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("id", "amount", "category", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)

        # Определение заголовков
        self.tree.heading("id", text="ID")
        self.tree.heading("amount", text="Сумма")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")

        # Определение ширины колонок
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("amount", width=100, anchor=tk.E) # Выравнивание по правому краю
        self.tree.column("category", width=150, anchor=tk.W)
        self.tree.column("date", width=100, anchor=tk.CENTER)

        # --- Скроллбар для таблицы ---
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        # --- Фрейм для фильтрации и общей суммы ---
        filter_frame = ttk.LabelFrame(self.root, text="Фильтр и итоги", padding="10")
        filter_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(filter_frame, text="Начальная дата:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.start_date_filter_entry = ttk.Entry(filter_frame)
        self.start_date_filter_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(filter_frame, text="Конечная дата:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.end_date_filter_entry = ttk.Entry(filter_frame)
        self.end_date_filter_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ttk.Label(filter_frame, text="Категория:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_filter_entry = ttk.Entry(filter_frame)
        self.category_filter_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        filter_button = ttk.Button(filter_frame, text="Фильтровать", command=self.filter_expenses)
        filter_button.grid(row=1, column=2, padx=5, pady=5)

        reset_filter_button = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        reset_filter_button.grid(row=1, column=3, padx=5, pady=5)

        self.total_sum_label = ttk.Label(filter_frame, text="Общая сумма: 0.00", font=("Arial", 12, "bold"))
        self.total_sum_label.grid(row=2, column=0, columnspan=4, pady=10)

        filter_frame.columnconfigure(1, weight=1)
        filter_frame.columnconfigure(3, weight=1)

        # --- Меню ---
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Сохранить", command=self.save_expenses)
        file_menu.add_command(label="Сохранить как...", command=self.save_expenses_as)
        file_menu.add_command(label="Загрузить", command=self.load_expenses_dialog)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)

        # Настройка растягивания главного окна
        self.root.rowconfigure(1, weight=1)
        self.root.columnconfigure(0, weight=1)


    def validate_amount(self, text):
        """Проверяет, является ли введенный текст корректной суммой."""
        if text == "":
            return True # Разрешаем пустое поле для очистки
        try:
            # Проверяем, что введенное значение может быть преобразовано в float
            # и что оно положительное (или ноль)
            amount = float(text)
            if amount >= 0:
                return True
            else:
                return False
        except ValueError:
            return False

    def validate_date(self, date_text):
        """Проверяет, соответствует ли строка формату YYYY-MM-DD."""
        try:
            datetime.strptime(date_text, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_expense(self):
        """Добавляет новый расход."""
        amount_str = self.amount_entry.get()
        category = self.category_entry.get().strip()
        date_str = self.date_entry.get().strip()

        # Валидация полей
        if not amount_str or not category or not date_str:
            messagebox.showwarning("Ошибка ввода", "Все поля (Сумма, Категория, Дата) должны быть заполнены.")
            return

        if not self.validate_amount(amount_str):
            messagebox.showwarning("Ошибка ввода", "Сумма должна быть положительным числом.")
            return

        if not self.validate_date(date_str):
            messagebox.showwarning("Ошибка ввода", "Дата должна быть в формате YYYY-MM-DD.")
            return

        # Преобразуем сумму в float
        try:
            amount = float(amount_str)
        except ValueError:
            # Эта проверка дублируется, но на всякий случай
            messagebox.showwarning("Ошибка ввода", "Некорректное значение суммы.")
            return

        # Создаем ID для расхода (можно использовать timestamp или UUID для больших приложений)
        expense_id = f"E{len(self.expenses) + 1:04d}" # Пример простого ID
        new_expense = {
            "id": expense_id,
            "amount": amount,
            "category": category,
            "date": date_str,
        }

        self.expenses.append(new_expense)
        self.save_expenses() # Сохраняем данные после добавления
        self.update_treeview() # Обновляем таблицу
        self.calculate_total_sum() # Обновляем общую сумму
        self.clear_input_fields() # Очищаем поля ввода

    def clear_input_fields(self):
        """Очищает поля ввода и устанавливает текущую дату."""
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        # Возвращаем текущую дату по умолчанию
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

    def load_expenses(self):
        """Загружает данные из JSON файла."""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
                    # Валидация загруженных данных (опционально)
                    for expense in self.expenses:
                        if not all(k in expense for k in ("id", "amount", "category", "date")):
                            print(f"Предупреждение: Некорректный формат записи в {self.data_file}: {expense}")
                            # Можно удалить или исправить некорректную запись
            except json.JSONDecodeError:
                messagebox.showerror("Ошибка загрузки", f"Невозможно декодировать JSON из файла {self.data_file}. Файл может быть поврежден.")
                self.expenses = [] # Сбрасываем, если файл поврежден
            except Exception as e:
                messagebox.showerror("Ошибка загрузки", f"Произошла ошибка при загрузке данных: {e}")
                self.expenses = []
        else:
            self.expenses = [] # Если файла нет, начинаем с пустого списка

    def save_expenses(self):
        """Сохраняет текущие данные в JSON файл."""
        try:
            # Сначала сортируем по дате перед сохранением (опционально, но удобно)
            self.expenses.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))

            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, indent=4, ensure_ascii=False)
            print(f"Данные сохранены в {self.data_file}")
            self.commit_changes() # Выполняем коммит после сохранения
        except IOError as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные в файл {self.data_file}: {e}")
        except Exception as e:
             messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка при сохранении: {e}")

    def load_expenses_dialog(self):
        """Открывает диалог для выбора файла и загрузки данных."""
        filepath = filedialog.askopenfilename(
            title="Выберите файл данных",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filepath:
            self.data_file = filepath # Обновляем текущее имя файла
            self.load_expenses()
            self.update_treeview()
            self.calculate_total_sum()
            messagebox.showinfo("Загрузка данных", f"Данные успешно загружены из {os.path.basename(filepath)}")

    def save_expenses_as(self):
        """Открывает диалог для сохранения данных под новым именем."""
        filepath = filedialog.asksaveasfilename(
            title="Сохранить данные как",
            defaultextension=".json",
            filetypes=(("JSON files", "*.json"), ("All files", "*.*"))
        )
        if filepath:
            try:
                # Сортируем перед сохранением
                self.expenses.sort(key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"))
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.expenses, f, indent=4, ensure_ascii=False)
                self.data_file = filepath # Обновляем текущее имя файла
                print(f"Данные сохранены в {filepath}")
                # Коммит для "Save As" не делаем автоматически, чтобы не засорять историю
                # self.commit_changes(f"Сохранение данных как {os.path.basename(filepath)}")
                messagebox.showinfo("Сохранение данных", f"Данные успешно сохранены в {os.path.basename(filepath)}")
            except IOError as e:
                messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные в файл {filepath}: {e}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка при сохранении: {e}")


    def update_treeview(self, data=None):
        """Очищает и заполняет таблицу данными."""
        # Удаляем все старые записи
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Определяем источник данных
        source_data = data if data is not None else self.expenses

        # Вставляем новые записи
        for expense tk.END, values=(
                expense.get('id', 'N/A'),
                formatted_amount,
                expense.get('category', 'N/A'),
                expense.get('date', 'N/A')
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
                # Фильтруем только если дата расхода валидна
                filtered_list = [exp for exp in filtered_list if self.validate_date(exp["date"]) and datetime.strptime(exp["date"], "%Y-%m-%d") >= start_date]
            except ValueError: # Не должно произойти, если validate_date работает
                pass

        # Фильтр по конечной дате
        if end_date_str:
            if not self.validate_date(end_date_str):
                messagebox.showerror("Ошибка ввода", "Конечная дата должна быть в формате YYYY-MM-DD.")
                return
            try:
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                 # Фильтруем только если дата расхода валидна
                filtered_list = [exp for exp in filtered_list if self.validate_date(exp["date"]) and datetime.strptime(exp["date"], "%Y-%m-%d") <= end_date]
            except ValueError:
                pass

        # Фильтр по категории
        if category_filter:
            filtered_list = [exp for exp in filtered_list if exp.get("category", "").lower() == category_filter]

        self.update_treeview(filtered_list)
        self.calculate_total_sum(filtered_list) # Пересчитываем сумму для отфильтрованных данных

    def reset_filter(self):
        """Сбрасывает поля фильтра и обновляет таблицу."""
        self.start_date_filter_entry.delete(0, tk.END)
        self.end_date_filter_entry.delete(0, tk.END)
        self.category_filter_entry.delete(0, tk.END)
        self.update_treeview() # Обновляем с полным списком
        self.calculate_total_sum() # Пересчитываем общую сумму с полным списком

    def calculate_total_sum(self, data=None):
        """Подсчитывает общую сумму расходов (для всех или отфильтрованных)."""
        source_data = data if data is not None else self.expenses
        total = sum(exp.get("amount", 0.0) for exp in source_data) # Используем .get для безопасности
        self.total_sum_label.config(text=f"Общая сумма: {total:.2f}")


if __name__ == "__main__":
    # Проверка наличия Git
    if not os.path.exists(".git"):
        print("Предупреждение: Директория .git не найдена. Git-коммиты будут отключены.")
        # Можно добавить 'git init' здесь, если хотим автоматически инициализировать
        # try:
        #     subprocess.run(["git", "init"], check=True)
        #     print("Git репозиторий инициализирован.")
        # except Exception as e:
        #     print(f"Не удалось инициализировать Git: {e}")

    root = tk.Tk()
    app = ExpenseTracker(root)
    # Устанавливаем имя файла, как в README
    app.root.title("Expense Tracker") # Убедимся, что заголовок окна соответствует
    root.mainloop()
