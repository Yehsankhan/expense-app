from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, Ellipse, Rectangle
from kivy.core.text import Label as CoreLabel

import math
import db
from export import export_pdf

from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.boxlayout import MDBoxLayout

from kivymd.uix.list import TwoLineRightIconListItem
from kivymd.uix.button import MDIconButton


# ---------------- SCREENS ----------------
class LoginScreen(Screen):
    pass

class DashboardScreen(Screen):
    pass

class ChartsScreen(Screen):
    pass


# ---------------- APP ----------------
class ExpenseApp(MDApp):

    def build(self):
        db.create_tables()

        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

        return Builder.load_file("ui.kv")

    # ---------------- LOGIN ----------------
    def login_user(self, username, password):
        db.cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        user = db.cursor.fetchone()

        if user:
            self.user_id = user[0]
            self.root.current = "dashboard"
            self.load_expenses()
            self.update_budget_ui()

    # ---------------- REGISTER ----------------
    def register_user(self, username, password):
        db.cursor.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )
        db.conn.commit()

    # ---------------- LOAD EXPENSES (WITH DELETE) ----------------
    def load_expenses(self):
        screen = self.root.get_screen("dashboard")
        screen.ids.expense_list.clear_widgets()

        db.cursor.execute(
            "SELECT id, amount, category FROM expenses WHERE user_id=?",
            (self.user_id,)
        )

        for exp_id, amount, category in db.cursor.fetchall():

            item = TwoLineRightIconListItem(
                text=f"{category}",
                secondary_text=f"{amount} Tk"
            )

            delete_btn = MDIconButton(
                icon="delete",
                on_release=lambda x, eid=exp_id: self.delete_expense(eid)
            )

            item.add_widget(delete_btn)
            screen.ids.expense_list.add_widget(item)

    # ---------------- DELETE EXPENSE ----------------
    def delete_expense(self, exp_id):
        db.cursor.execute("DELETE FROM expenses WHERE id=?", (exp_id,))
        db.conn.commit()

        self.load_expenses()
        self.update_budget_ui()

    # ---------------- ADD EXPENSE ----------------
    def add_expense_dialog(self):
        self.amount = MDTextField(hint_text="Amount")
        self.category = MDTextField(hint_text="Category")

        box = MDBoxLayout(
            orientation="vertical",
            spacing=10,
            size_hint_y=None,
            height="120dp"
        )

        box.add_widget(self.amount)
        box.add_widget(self.category)

        self.dialog = MDDialog(
            title="Add Expense",
            type="custom",
            content_cls=box,
            buttons=[MDRaisedButton(text="SAVE", on_release=self.save_expense)]
        )
        self.dialog.open()

    def save_expense(self, obj):
        import datetime

        db.cursor.execute(
            "INSERT INTO expenses(user_id,amount,category,date) VALUES(?,?,?,?)",
            (self.user_id, float(self.amount.text), self.category.text, str(datetime.date.today()))
        )
        db.conn.commit()

        self.dialog.dismiss()
        self.load_expenses()
        self.update_budget_ui()

    # ---------------- BUDGET ----------------
    def set_budget_dialog(self):
        self.budget_input = MDTextField(hint_text="Budget")

        self.dialog = MDDialog(
            title="Set Budget",
            type="custom",
            content_cls=self.budget_input,
            buttons=[MDRaisedButton(text="SAVE", on_release=self.save_budget)]
        )
        self.dialog.open()

    def save_budget(self, obj):
        db.cursor.execute("DELETE FROM budget WHERE user_id=?", (self.user_id,))
        db.cursor.execute(
            "INSERT INTO budget(user_id,amount) VALUES(?,?)",
            (self.user_id, float(self.budget_input.text))
        )
        db.conn.commit()

        self.dialog.dismiss()
        self.update_budget_ui()

    def update_budget_ui(self):
        screen = self.root.get_screen("dashboard")

        db.cursor.execute("SELECT amount FROM budget WHERE user_id=?", (self.user_id,))
        budget = db.cursor.fetchone()

        if not budget:
            return

        budget = budget[0]

        db.cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=?", (self.user_id,))
        spent = db.cursor.fetchone()[0] or 0

        percent = (spent / budget) * 100 if budget else 0

        screen.ids.budget_label.text = f"Budget: {budget} | Spent: {spent}"
        screen.ids.budget_bar.value = percent

    # ---------------- CHARTS ----------------
    def go_to_charts(self):
        self.root.current = "charts"
        self.draw_pie_chart()

    # ---------------- FIXED PIE CHART (CLEAN + LEGEND + % ) ----------------
    def draw_pie_chart(self):
        screen = self.root.get_screen("charts")
        layout = screen.ids.chart_area
        layout.canvas.clear()

        db.cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user_id=?
            GROUP BY category
        """, (self.user_id,))

        data = db.cursor.fetchall()

        total = sum([i[1] for i in data]) if data else 0
        if total == 0:
            return

        from kivy.graphics import Color, Ellipse, Rectangle
        from kivy.core.text import Label as CoreLabel

        start_angle = 0

        center_x, center_y = 60, 120
        size = 220

        with layout.canvas:

            # ---------------- PIE ----------------
            for cat, val in data:
                percent = val / total
                angle = percent * 360

                r = (hash(cat) % 255) / 255
                g = ((hash(cat) * 2) % 255) / 255
                b = ((hash(cat) * 3) % 255) / 255

                Color(r, g, b, 1)

                Ellipse(
                    pos=(center_x, center_y),
                    size=(size, size),
                    angle_start=start_angle,
                    angle_end=start_angle + angle
                )

                start_angle += angle

            # ---------------- LEGEND ----------------
            y = 420

            for cat, val in data:
                percent = (val / total) * 100

                r = (hash(cat) % 255) / 255
                g = ((hash(cat) * 2) % 255) / 255
                b = ((hash(cat) * 3) % 255) / 255

                Color(r, g, b, 1)
                Rectangle(pos=(200, y), size=(15, 15))

                Color(1, 1, 1, 1)

                text = CoreLabel(
                    text=f"{cat} | {val} Tk | {percent:.1f}%",
                    font_size=16
                )
                text.refresh()

                Rectangle(
                    texture=text.texture,
                    size=text.texture.size,
                    pos=(225, y - 5)
                )

                y -= 30

    # ---------------- PDF ----------------
    def export_pdf(self):
        db.cursor.execute("""
            SELECT category, SUM(amount)
            FROM expenses
            WHERE user_id=?
            GROUP BY category
        """, (self.user_id,))

        export_pdf(db.cursor.fetchall())


# ---------------- RUN ----------------
if __name__ == "__main__":
    ExpenseApp().run()