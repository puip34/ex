import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QTableWidget, QTableWidgetItem, QPushButton,
                               QVBoxLayout, QWidget, QDialog, QFormLayout, QLineEdit, QComboBox, QLabel, QMessageBox,
                               QHBoxLayout)
from PySide6.QtGui import QIcon, QFont, QPixmap, QDoubleValidator, QIntValidator
from PySide6.QtCore import Qt
import mysql.connector
from mysql.connector import Error

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='',
            database='MosaicDB'
        )
        return connection
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

class AddEditMaterialDialog(QDialog):
    def __init__(self, parent=None, material_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить материал" if material_id is None else "Редактировать материал")
        self.setWindowIcon(QIcon('Наш декор.png'))
        self.material_id = material_id

        layout = QFormLayout()
        self.name_edit = QLineEdit()
        layout.addRow("Наименование:", self.name_edit)
        self.type_combo = QComboBox()
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaterialTypeID, TypeName FROM MaterialTypes")
                types = cursor.fetchall()
                for type_id, type_name in types:
                    self.type_combo.addItem(type_name, type_id)
            except Error as e:
                print(f"Ошибка загрузки типов материалов: {e}")
            finally:
                conn.close()
        layout.addRow("Тип материала:", self.type_combo)
        self.unit_price_edit = QLineEdit()
        self.unit_price_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        layout.addRow("Цена единицы:", self.unit_price_edit)
        self.stock_qty_edit = QLineEdit()
        self.stock_qty_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        layout.addRow("Количество на складе:", self.stock_qty_edit)
        self.unit_edit = QLineEdit()
        layout.addRow("Единица измерения:", self.unit_edit)
        self.qty_per_pkg_edit = QLineEdit()
        self.qty_per_pkg_edit.setValidator(QIntValidator(1, 10000))
        layout.addRow("Количество в упаковке:", self.qty_per_pkg_edit)
        self.min_qty_edit = QLineEdit()
        self.min_qty_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        layout.addRow("Минимальное количество:", self.min_qty_edit)
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.save_button.clicked.connect(self.save_material)
        layout.addRow(self.save_button)
        self.setLayout(layout)
        if material_id:
            self.load_material()

    def load_material(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT Name, MaterialTypeID, UnitPrice, StockQuantity, Unit, QuantityPerPackage, MinQuantity "
                               "FROM Materials WHERE MaterialID = %s", (self.material_id,))
                row = cursor.fetchone()
                if row:
                    name, type_id, unit_price, stock_qty, unit, qty_per_pkg, min_qty = row
                    self.name_edit.setText(name)
                    index = self.type_combo.findData(type_id)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                    self.unit_price_edit.setText(str(unit_price))
                    self.stock_qty_edit.setText(str(stock_qty))
                    self.unit_edit.setText(unit)
                    self.qty_per_pkg_edit.setText(str(qty_per_pkg))
                    self.min_qty_edit.setText(str(min_qty))
            except Error as e:
                print(f"Ошибка загрузки материала: {e}")
            finally:
                conn.close()

    def save_material(self):
        if not all([self.name_edit.text(), self.unit_price_edit.text(), self.stock_qty_edit.text(),
                    self.unit_edit.text(), self.qty_per_pkg_edit.text(), self.min_qty_edit.text()]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        name = self.name_edit.text()
        type_id = self.type_combo.currentData()
        unit_price = float(self.unit_price_edit.text())
        stock_qty = float(self.stock_qty_edit.text())
        unit = self.unit_edit.text()
        qty_per_pkg = int(self.qty_per_pkg_edit.text())
        min_qty = float(self.min_qty_edit.text())
        if unit_price < 0 or stock_qty < 0 or min_qty < 0:
            QMessageBox.warning(self, "Ошибка", "Цена, количество на складе и минимальное количество не могут быть отрицательными!")
            return
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if self.material_id:
                    query = ("UPDATE Materials SET Name=%s, MaterialTypeID=%s, UnitPrice=%s, StockQuantity=%s, "
                             "Unit=%s, QuantityPerPackage=%s, MinQuantity=%s WHERE MaterialID=%s")
                    cursor.execute(query, (name, type_id, unit_price, stock_qty, unit, qty_per_pkg, min_qty, self.material_id))
                else:
                    query = ("INSERT INTO Materials (Name, MaterialTypeID, UnitPrice, StockQuantity, Unit, QuantityPerPackage, "
                             "MinQuantity) VALUES (%s, %s, %s, %s, %s, %s, %s)")
                    cursor.execute(query, (name, type_id, unit_price, stock_qty, unit, qty_per_pkg, min_qty))
                conn.commit()
                self.accept()
            except Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить материал: {e}")
            finally:
                conn.close()

class AddEditProductDialog(QDialog):
    def __init__(self, parent=None, product_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить продукт" if product_id is None else "Редактировать продукт")
        self.setWindowIcon(QIcon('Наш декор.png'))
        self.product_id = product_id

        layout = QFormLayout()
        self.article_edit = QLineEdit()
        layout.addRow("Артикул:", self.article_edit)
        self.type_combo = QComboBox()
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT ProductTypeID, TypeName FROM ProductTypes")
                types = cursor.fetchall()
                for type_id, type_name in types:
                    self.type_combo.addItem(type_name, type_id)
            except Error as e:
                print(f"Ошибка загрузки типов продуктов: {e}")
            finally:
                conn.close()
        layout.addRow("Тип продукта:", self.type_combo)
        self.name_edit = QLineEdit()
        layout.addRow("Наименование:", self.name_edit)
        self.min_cost_edit = QLineEdit()
        self.min_cost_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        layout.addRow("Мин. стоимость для партнера:", self.min_cost_edit)
        self.roll_width_edit = QLineEdit()
        self.roll_width_edit.setValidator(QDoubleValidator(0.0, 100.0, 2))
        layout.addRow("Ширина рулона:", self.roll_width_edit)
        self.manage_materials_button = QPushButton("Управление материалами")
        self.manage_materials_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.manage_materials_button.clicked.connect(self.manage_materials)
        layout.addRow(self.manage_materials_button)
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.save_button.clicked.connect(self.save_product)
        layout.addRow(self.save_button)
        self.setLayout(layout)
        if product_id:
            self.load_product()

    def load_product(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT Article, ProductTypeID, Name, MinCostForPartner, RollWidth "
                               "FROM Products WHERE ProductID = %s", (self.product_id,))
                row = cursor.fetchone()
                if row:
                    article, type_id, name, min_cost, roll_width = row
                    self.article_edit.setText(article)
                    index = self.type_combo.findData(type_id)
                    if index >= 0:
                        self.type_combo.setCurrentIndex(index)
                    self.name_edit.setText(name)
                    self.min_cost_edit.setText(str(min_cost))
                    self.roll_width_edit.setText(str(roll_width))
            except Error as e:
                print(f"Ошибка загрузки продукта: {e}")
            finally:
                conn.close()

    def manage_materials(self):
        dialog = ManageProductMaterialsDialog(self.product_id, self)
        dialog.exec()

    def save_product(self):
        if not all([self.article_edit.text(), self.name_edit.text(), self.min_cost_edit.text(), self.roll_width_edit.text()]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        article = self.article_edit.text()
        type_id = self.type_combo.currentData()
        name = self.name_edit.text()
        min_cost = float(self.min_cost_edit.text())
        roll_width = float(self.roll_width_edit.text())
        if min_cost < 0 or roll_width < 0:
            QMessageBox.warning(self, "Ошибка", "Мин. стоимость и ширина рулона не могут быть отрицательными!")
            return
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if self.product_id:
                    query = ("UPDATE Products SET Article=%s, ProductTypeID=%s, Name=%s, MinCostForPartner=%s, RollWidth=%s "
                             "WHERE ProductID=%s")
                    cursor.execute(query, (article, type_id, name, min_cost, roll_width, self.product_id))
                else:
                    query = ("INSERT INTO Products (Article, ProductTypeID, Name, MinCostForPartner, RollWidth) "
                             "VALUES (%s, %s, %s, %s, %s)")
                    cursor.execute(query, (article, type_id, name, min_cost, roll_width))
                    self.product_id = cursor.lastrowid
                conn.commit()
                self.accept()
            except Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить продукт: {e}")
            finally:
                conn.close()

class ManageProductMaterialsDialog(QDialog):
    def __init__(self, product_id, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Управление материалами продукта")
        self.setWindowIcon(QIcon('Наш декор.png'))
        self.product_id = product_id

        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Материал", "Количество"])
        self.add_button = QPushButton("Добавить материал")
        self.add_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.add_button.clicked.connect(self.add_material)
        self.edit_button = QPushButton("Редактировать материал")
        self.edit_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.edit_button.clicked.connect(self.edit_material)
        self.remove_button = QPushButton("Удалить материал")
        self.remove_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.remove_button.clicked.connect(self.remove_material)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.add_button)
        buttons_layout.addWidget(self.edit_button)
        buttons_layout.addWidget(self.remove_button)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        self.load_materials()

    def load_materials(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = ("SELECT pm.ProductMaterialID, m.Name, pm.Quantity "
                         "FROM ProductMaterials pm JOIN Materials m ON pm.MaterialID = m.MaterialID "
                         "WHERE pm.ProductID = %s")
                cursor.execute(query, (self.product_id,))
                rows = cursor.fetchall()
                self.table.setRowCount(len(rows))
                for i, (pm_id, material_name, quantity) in enumerate(rows):
                    item = QTableWidgetItem(material_name)
                    item.setData(Qt.UserRole, pm_id)
                    self.table.setItem(i, 0, item)
                    self.table.setItem(i, 1, QTableWidgetItem(str(quantity)))
            except Error as e:
                print(f"Ошибка загрузки материалов продукта: {e}")
            finally:
                conn.close()

    def add_material(self):
        dialog = AddEditProductMaterialDialog(self.product_id, self)
        if dialog.exec():
            self.load_materials()

    def edit_material(self):
        row = self.table.currentRow()
        if row >= 0:
            pm_id = self.table.item(row, 0).data(Qt.UserRole)
            dialog = AddEditProductMaterialDialog(self.product_id, self, pm_id)
            if dialog.exec():
                self.load_materials()
        else:
            QMessageBox.information(self, "Информация", "Выберите материал для редактирования.")

    def remove_material(self):
        row = self.table.currentRow()
        if row >= 0:
            pm_id = self.table.item(row, 0).data(Qt.UserRole)
            reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить этот материал?",
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                conn = create_connection()
                if conn:
                    try:
                        cursor = conn.cursor()
                        cursor.execute("DELETE FROM ProductMaterials WHERE ProductMaterialID = %s", (pm_id,))
                        conn.commit()
                        self.load_materials()
                    except Error as e:
                        QMessageBox.critical(self, "Ошибка", f"Не удалось удалить материал: {e}")
                    finally:
                        conn.close()

class AddEditProductMaterialDialog(QDialog):
    def __init__(self, product_id, parent=None, pm_id=None):
        super().__init__(parent)
        self.setWindowTitle("Добавить материал продукта" if pm_id is None else "Редактировать материал продукта")
        self.setWindowIcon(QIcon('Наш декор.png'))
        self.product_id = product_id
        self.pm_id = pm_id

        layout = QFormLayout()
        self.material_combo = QComboBox()
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaterialID, Name FROM Materials")
                materials = cursor.fetchall()
                for material_id, material_name in materials:
                    self.material_combo.addItem(material_name, material_id)
            except Error as e:
                print(f"Ошибка загрузки материалов: {e}")
            finally:
                conn.close()
        layout.addRow("Материал:", self.material_combo)
        self.quantity_edit = QLineEdit()
        self.quantity_edit.setValidator(QDoubleValidator(0.0, 1000000.0, 2))
        layout.addRow("Количество:", self.quantity_edit)
        self.save_button = QPushButton("Сохранить")
        self.save_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.save_button.clicked.connect(self.save_product_material)
        layout.addRow(self.save_button)
        self.setLayout(layout)
        if pm_id:
            self.load_product_material()

    def load_product_material(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT MaterialID, Quantity FROM ProductMaterials WHERE ProductMaterialID = %s", (self.pm_id,))
                row = cursor.fetchone()
                if row:
                    material_id, quantity = row
                    index = self.material_combo.findData(material_id)
                    if index >= 0:
                        self.material_combo.setCurrentIndex(index)
                    self.quantity_edit.setText(str(quantity))
            except Error as e:
                print(f"Ошибка загрузки материала продукта: {e}")
            finally:
                conn.close()

    def save_product_material(self):
        if not self.quantity_edit.text():
            QMessageBox.warning(self, "Ошибка", "Введите количество!")
            return
        material_id = self.material_combo.currentData()
        quantity = float(self.quantity_edit.text())
        if quantity < 0:
            QMessageBox.warning(self, "Ошибка", "Количество не может быть отрицательным!")
            return
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if self.pm_id:
                    query = "UPDATE ProductMaterials SET MaterialID=%s, Quantity=%s WHERE ProductMaterialID=%s"
                    cursor.execute(query, (material_id, quantity, self.pm_id))
                else:
                    query = "INSERT INTO ProductMaterials (ProductID, MaterialID, Quantity) VALUES (%s, %s, %s)"
                    cursor.execute(query, (self.product_id, material_id, quantity))
                conn.commit()
                self.accept()
            except Error as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить материал продукта: {e}")
            finally:
                conn.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Наш Декор")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('Наш декор.png'))
        self.setStyleSheet("background-color: #FFFFFF;")

        self.tab_widget = QTabWidget()
        # Products tab
        self.products_tab = QWidget()
        self.products_layout = QVBoxLayout()
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(["Артикул", "Тип", "Наименование", "Мин. стоимость для партнера", "Ширина рулона", "Стоимость"])
        self.add_product_button = QPushButton("Добавить продукт")
        self.add_product_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.add_product_button.clicked.connect(self.add_product)
        self.edit_product_button = QPushButton("Редактировать продукт")
        self.edit_product_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.edit_product_button.clicked.connect(self.edit_product)
        self.products_layout.addWidget(self.products_table)
        self.products_layout.addWidget(self.add_product_button)
        self.products_layout.addWidget(self.edit_product_button)
        self.products_tab.setLayout(self.products_layout)
        # Materials tab
        self.materials_tab = QWidget()
        self.materials_layout = QVBoxLayout()
        self.materials_table = QTableWidget()
        self.materials_table.setColumnCount(7)
        self.materials_table.setHorizontalHeaderLabels(["Тип", "Наименование", "Цена единицы", "Количество на складе", "Единица измерения", "Количество в упаковке", "Минимальное количество"])
        self.add_material_button = QPushButton("Добавить материал")
        self.add_material_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.add_material_button.clicked.connect(self.add_material)
        self.edit_material_button = QPushButton("Редактировать материал")
        self.edit_material_button.setStyleSheet("background-color: #2D6033; color: white;")
        self.edit_material_button.clicked.connect(self.edit_material)
        self.materials_layout.addWidget(self.materials_table)
        self.materials_layout.addWidget(self.add_material_button)
        self.materials_layout.addWidget(self.edit_material_button)
        self.materials_tab.setLayout(self.materials_layout)
        # Add tabs
        self.tab_widget.addTab(self.products_tab, "Продукты")
        self.tab_widget.addTab(self.materials_tab, "Материалы")
        # Logo
        logo_label = QLabel()
        pixmap = QPixmap('Наш декор.png')
        logo_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        logo_label.setAlignment(Qt.AlignCenter)
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(logo_label)
        main_layout.addWidget(self.tab_widget)
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        # Load data
        self.load_products()
        self.load_materials()
        self.products_table.doubleClicked.connect(self.edit_product)
        self.materials_table.doubleClicked.connect(self.edit_material)

    def load_products(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = ("SELECT p.ProductID, p.Article, pt.TypeName, p.Name, p.MinCostForPartner, p.RollWidth "
                         "FROM Products p JOIN ProductTypes pt ON p.ProductTypeID = pt.ProductTypeID")
                cursor.execute(query)
                rows = cursor.fetchall()
                self.products_table.setRowCount(len(rows))
                for i, (product_id, article, type_name, name, min_cost, roll_width) in enumerate(rows):
                    cost = self.calculate_product_cost(product_id)
                    item = QTableWidgetItem(article)
                    item.setData(Qt.UserRole, product_id)
                    self.products_table.setItem(i, 0, item)
                    self.products_table.setItem(i, 1, QTableWidgetItem(type_name))
                    self.products_table.setItem(i, 2, QTableWidgetItem(name))
                    self.products_table.setItem(i, 3, QTableWidgetItem(f"{min_cost:.2f}"))
                    self.products_table.setItem(i, 4, QTableWidgetItem(f"{roll_width:.2f}"))
                    self.products_table.setItem(i, 5, QTableWidgetItem(f"{cost:.2f}"))
            except Error as e:
                print(f"Ошибка загрузки продуктов: {e}")
            finally:
                conn.close()

    def calculate_product_cost(self, product_id):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = ("SELECT SUM(m.UnitPrice * pm.Quantity) "
                         "FROM ProductMaterials pm JOIN Materials m ON pm.MaterialID = m.MaterialID "
                         "WHERE pm.ProductID = %s")
                cursor.execute(query, (product_id,))
                cost = cursor.fetchone()[0]
                return cost if cost is not None else 0.0
            except Error as e:
                print(f"Ошибка расчета стоимости продукта: {e}")
                return 0.0
            finally:
                conn.close()
        return 0.0

    def load_materials(self):
        conn = create_connection()
        if conn:
            try:
                cursor = conn.cursor()
                query = ("SELECT m.MaterialID, mt.TypeName, m.Name, m.UnitPrice, m.StockQuantity, m.Unit, m.QuantityPerPackage, m.MinQuantity "
                         "FROM Materials m JOIN MaterialTypes mt ON m.MaterialTypeID = mt.MaterialTypeID")
                cursor.execute(query)
                rows = cursor.fetchall()
                self.materials_table.setRowCount(len(rows))
                for i, (material_id, type_name, name, unit_price, stock_qty, stock_qty_unit, qty_per_pkg, min_qty) in enumerate(rows):
                    item = QTableWidgetItem(type_name)
                    item.setData(Qt.UserRole, material_id)
                    self.materials_table.setItem(i, 0, item)
                    self.materials_table.setItem(i, 1, QTableWidgetItem(name))
                    self.materials_table.setItem(i, 2, QTableWidgetItem(f"{unit_price:.2f}"))
                    self.materials_table.setItem(i, 3, QTableWidgetItem(f"{stock_qty:.2f}"))
                    self.materials_table.setItem(i, 4, QTableWidgetItem(stock_qty_unit))
                    self.materials_table.setItem(i, 5, QTableWidgetItem(str(qty_per_pkg)))
                    self.materials_table.setItem(i, 6, QTableWidgetItem(f"{min_qty:.2f}"))
            except Error as e:
                print(f"Ошибка загрузки материалов: {e}")
            finally:
                conn.close()

    def add_product(self):
        dialog = AddEditProductDialog(self)
        if dialog.exec():
            self.load_products()

    def edit_product(self, index):
        row = index.row()
        product_id = self.products_table.item(row, 0).data(Qt.UserRole)
        dialog = AddEditProductDialog(self, product_id)
        if dialog.exec():
            self.load_products()

    def add_material(self):
        dialog = AddEditMaterialDialog(self)
        if dialog.exec():
            self.load_materials()

    def edit_material(self, index):
        row = index.row()
        material_id = self.materials_table.item(row, 0).data(Qt.UserRole)
        dialog = AddEditMaterialDialog(self, material_id)
        if dialog.exec():
            self.load_materials()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    font = QFont("Gabriola")
    app.setFont(font)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())