import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QDialog
from PyQt6.uic import loadUi

class CoffeeDatabaseViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("main.ui", self)
        self.setWindowTitle("Кофе в базе данных")
        self.db_file_name = "coffee.sqlite"
        self.add_edit_button = QPushButton("Добавить/Редактировать запись", self)
        self.add_edit_button.clicked.connect(self.show_add_edit_form)
        self.verticalLayout.addWidget(self.add_edit_button)
        self.load_data()

    def load_data(self):
        try:
            con = sqlite3.connect(self.db_file_name)
            cur = con.cursor()
            cur.execute("SELECT * FROM coffee")
            data = cur.fetchall()
            columns = [description[0] for description in cur.description]
            self.table.setColumnCount(len(columns))
            self.table.setHorizontalHeaderLabels(columns)
            self.table.setRowCount(len(data))
            for row_num, row_data in enumerate(data):
                for col_num, col_data in enumerate(row_data):
                    item = QTableWidgetItem(str(col_data))
                    self.table.setItem(row_num, col_num, item)
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
        finally:
            con.close()

    def show_add_edit_form(self):
        form = AddEditCoffeeForm(self.db_file_name, self)
        form.exec()
        self.load_data()

class AddEditCoffeeForm(QDialog):
    def __init__(self, db_file_name, parent=None):
        super().__init__(parent)
        loadUi("addEditCoffeeForm.ui", self)
        self.db_file_name = db_file_name
        self.coffee_id = None
        self.init_form()
        self.save_button.clicked.connect(self.save_data)

    def init_form(self):
        if self.coffee_id is not None:
            self.setWindowTitle("Редактирование записи о кофе")
            self.load_coffee_data()
        else:
            self.setWindowTitle("Добавление новой записи о кофе")

    def load_coffee_data(self):
        try:
            con = sqlite3.connect(self.db_file_name)
            cur = con.cursor()
            cur.execute('''
                SELECT * FROM coffee WHERE ID=?
            ''', (self.coffee_id,))
            coffee_data = cur.fetchone()
            if coffee_data:
                self.name_input.setText(coffee_data[1])
                self.roast_input.setText(coffee_data[2])
                self.grind_input.setText(coffee_data[3])
                self.flavor_input.setText(coffee_data[4])
                self.price_input.setText(str(coffee_data[5]))
                self.volume_input.setText(str(coffee_data[6]))
        except sqlite3.Error as e:
            print(f"Ошибка при загрузке данных о кофе: {e}")
        finally:
            con.close()

    def save_data(self):
        name = self.name_input.text()
        roast = self.roast_input.text()
        grind = self.grind_input.text()
        flavor = self.flavor_input.text()
        price = self.price_input.text()
        volume = self.volume_input.text()

        try:
            con = sqlite3.connect(self.db_file_name)
            cur = con.cursor()
            if self.coffee_id is not None:
                cur.execute('''
                    UPDATE coffee
                    SET "Название сорта"=?, "Степень обжарки"=?, "молотый/в зернах"=?,
                        "Описание вкуса"=?, "Цена"=?, "объем упаковки"=?
                    WHERE ID=?
                ''', (name, roast, grind, flavor, price, volume, self.coffee_id))
            else:
                cur.execute('''
                    INSERT INTO coffee ("Название сорта", "Степень обжарки", "молотый/в зернах",
                                        "Описание вкуса", "Цена", "объем упаковки")
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (name, roast, grind, flavor, price, volume))
            con.commit()
        except sqlite3.Error as e:
            print(f"Ошибка при работе с базой данных: {e}")
        finally:
            con.close()
        self.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeDatabaseViewer()
    window.show()
    sys.exit(app.exec())