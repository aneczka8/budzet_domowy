import mysql.connector
import hashlib
from datetime import *
from dateutil.relativedelta import *
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfWriter
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
import os

connection = mysql.connector.connect(user='***', password='***', host='localhost', database='budzet_domowy')
cursor = connection.cursor()

def log(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    cursor.execute(f"SELECT username, user_id FROM users WHERE password_hash = '{password_hash}'")
    if cursor.fetchone():
        #user = cursor.fetchone()
        #return user[1]
        return "zalogowany"
    else:
        return "nie udało się zalogować"

password = "94$fNg37sry"
username = 'Lexis'
#print(log(username, password))

def add_user(username, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    query = "INSERT INTO users(username, password_hash) VALUES(%s, %s)"
    values = (username, password_hash)
    cursor.execute(query, values)
    connection.commit()

#add_user('Aneczka2', 'MojeNoweHasło')

def add_periodically(dictionary, table):
    columns = ', '.join(dictionary.keys())
    values = tuple(dictionary.values())
    dictionary_date = datetime.strptime(str(dictionary['date']), '%Y-%m-%d')
    if dictionary['period_type'] == 'dzień':
        for _ in range(1, round(730/dictionary['period_amount'])+1):
            query = f"INSERT INTO {table}({columns}) VALUES(" + ",".join(["%s" for _ in values]) + ")"
            cursor.execute(query, values)
            dictionary_date += relativedelta(days =+ dictionary['period_amount'])
            dictionary['date'] = dictionary_date.date()
            values = tuple(dictionary.values())
    if dictionary['period_type'] == 'miesiąc':
        for _ in range(1, round(24/dictionary['period_amount'])+1):
            query = f"INSERT INTO {table}({columns}) VALUES(" + ",".join(["%s" for _ in values]) + ")"
            cursor.execute(query, values)
            dictionary_date += relativedelta(months =+ dictionary['period_amount'])
            dictionary['date'] = dictionary_date.date()
            values = tuple(dictionary.values())
    if dictionary['period_type'] == 'rok':
        for _ in range(1, round(2/dictionary['period_amount'])+1):
            query = f"INSERT INTO {table}({columns}) VALUES(" + ",".join(["%s" for _ in values]) + ")"
            cursor.execute(query, values)
            dictionary_date += relativedelta(years =+ dictionary['period_amount'])
            dictionary['date'] = dictionary_date.date()
            values = tuple(dictionary.values())

def add_expense(expense):
    columns = ', '.join(expense.keys())
    values = tuple(expense.values())
    if expense['periodicity'] == 1:
        add_periodically(expense, 'expenses')
    else:
        query = f"INSERT INTO expenses({columns}) VALUES(" + ",".join(["%s" for _ in values]) + ")"
        cursor.execute(query, values)
    connection.commit()

expense = {'category': '', 'name': '', 'money': 45.99, 'date': '2023-07-15', 'user_id': 8, 'periodicity': 1, 'period_amount': 3, 'period_type': 'miesiąc'}

#add_expense(expense)

def delete_expense(expense_id):
    query = f"DELETE FROM expenses WHERE id = {expense_id}"
    cursor.execute(query)
    connection.commit()

#delete_expense(40)

def add_income(income):
    columns = ', '.join(income.keys())
    values = tuple(income.values())
    if income['periodicity'] == 1:
        add_periodically(income, 'income')
    else:
        query = f"INSERT INTO income({columns}) VALUES(" + ",".join(["%s" for _ in values]) + ")"
        cursor.execute(query, values)
    connection.commit()

income = {'name': 'praca na stoczni', 'money': 10000, 'periodicity': True, 'period_amount': 45, 'period_type': 'dzień', 'user_id': 4, 'date': date.today()}

#add_income(income)

def delete_income(income_id):
    query = f"DELETE FROM income WHERE id = {income_id}"
    cursor.execute(query)
    connection.commit()

#delete_income(25)

def sum_avg(days_amount, user_id, table):
    today = date.today()
    previous_date = today - timedelta(days = days_amount)
    query = f"SELECT SUM(money) FROM {table} WHERE user_id = {user_id} AND date BETWEEN '{str(previous_date)}' AND '{str(today)}'"
    cursor.execute(query)
    suma = cursor.fetchone()[0]
    query = f"SELECT AVG(money) FROM {table} WHERE user_id = {user_id} AND date BETWEEN '{str(previous_date)}' AND '{str(today)}'"
    cursor.execute(query)
    avg = cursor.fetchone()[0]
    if avg is not None:
        avg = round(avg, 2)
    else:
        avg = 0.0
    return (suma, avg)

#print(sum_avg(365, 6, 'expenses'))
#print(sum_avg(60, 6, 'income'))

def balance(days_amount, user_id):
    income  = sum_avg(days_amount, user_id, 'income')[0]
    expenses = sum_avg(days_amount, user_id, 'expenses')[0]
    return round(income - expenses, 2)

def sum_category(days_amount, user_id, category):
    today = date.today()
    previous_date = today - timedelta(days = days_amount)
    query = f"SELECT SUM(money) FROM expenses WHERE user_id = {user_id} AND category = '{category}' AND date BETWEEN '{str(previous_date)}' AND '{str(today)}'"
    cursor.execute(query)
    suma = cursor.fetchone()[0]
    return suma

#print(balance(90, 10))

def add_plot(user_id):
    month = date.today().month
    day = date.today().day

    months = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec", "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
    expenses = []
    incomes = []
    balances = []

    plot_months = []
    for _ in range(0, 13):
        plot_months.append(months[month-1])
        month += 1
        if month == 12:
            month = 0

    expenses.append(sum_avg(day, user_id, 'expenses')[0])
    incomes.append(sum_avg(day, user_id, 'income')[0])
    balances.append(balance(day, user_id))
    for i in range(1, 13):
        expenses.append(sum_avg(day+30*i, user_id, 'expenses')[0] - sum_avg(day+30*(i-1),user_id, 'expenses')[0])
        incomes.append(sum_avg(day+30*i, user_id, 'income')[0] - sum_avg(day+30*(i-1),user_id, 'income')[0])
        balances.append(balance(day+30*i, user_id) - balance(day+30*(i-1), user_id))

    expenses.reverse()
    incomes.reverse()
    balances.reverse()

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(range(13), expenses, marker='o', linestyle='-', color='red', label='Wydatki')
    ax.plot(range(13), incomes, marker='o', linestyle='-', color='green', label='Wpływy')
    ax.plot(range(13), balances, marker='o', linestyle='-', color='blue', label='Bilans')
    plt.xticks(range(13), plot_months, rotation = 45)
    
    y_min = round(min(balances), -2)
    y_max = round(max(expenses+incomes), -2)
    y_step = (y_max - y_min)/20
    y_values = []
    for i in range(21):
        y_values.append(y_min + i*y_step)
    
    ax.set_title('Raport roczny')
    ax.set_ylabel('Złotówki')
    ax.legend()
    ax.yaxis.grid(True)
    ax.yaxis.set_ticks(y_values)

    plt.tight_layout()
    plt.savefig('wykres.png', bbox_inches='tight')

pdfmetrics.registerFont(TTFont('DejaVuSans', '/users/Programista/anaconda3/lib/python3.11/site-packages/reportlab/fonts/DejaVuSans.ttf'))

def generate_raport(user_id, filename, months):
    c = canvas.Canvas(filename, pagesize=A4, bottomup=1)
    textobject = c.beginText()
    textobject.setTextOrigin(50, 790)
    textobject.setFont("DejaVuSans", 16)
    if months == 1:
        czas = "ostatniego miesiąca"
    elif months == 3:
        czas = "ostatnich trzech miesięcy"
    elif months == 6:
        czas = "ostatnich sześciu miesięcy"
    elif months == 12:
        czas = "ostatnich dwunastu miesięcy"
    textobject.textLine(text=f"Raport z {czas}")
    
    if months == 1:
        textobject.moveCursor(400, -20)
        data = date.today()
        textobject.textLine(text=f"{data}")
    else:
        textobject.moveCursor(400, 0)

    textobject.setFont("DejaVuSans", 12)
    textobject.moveCursor(-400, 20)
    suma_avg_wplywow = sum_avg(30*months, user_id, 'income')
    suma_avg_wydatkow = sum_avg(30*months, user_id, 'expenses')
    bilans = balance(30*months, user_id)
    textobject.textLine(text=f"W ciągu {czas}: ")
    textobject.moveCursor(15, 5)
    textobject.textLines(f'''
        - wpływy wyniosły {suma_avg_wplywow[0]} zł,
        - wydatki wyniosły {suma_avg_wydatkow[0]} zł,
        - bilans wynosi {bilans} zł.''')
    if months > 1:
        textobject.moveCursor(-15, 5)
        textobject.textLine(text=f"Co daje średnio miesięcznie: ")
        textobject.moveCursor(15, 5)
        textobject.textLines(f'''
            - wpływy - {round(suma_avg_wplywow[1],2)} zł,
            - wydatki - {round(suma_avg_wydatkow[1],2)} zł,
            - bilans - {round(bilans/months,2)} zł.''')

    textobject.moveCursor(-15, 10)
    categories = {'jedzenie': 0, 'rozrywka': 0, 'kredyt': 0, 'rachunek': 0, 'leki': 0, 'pies': 0, 'opłaty domowe': 0, 'auto': 0, 'ubrania': 0, 'inne': 0}
    textobject.textLine(text="Wydatki w poszczególnych kategoriach wyniosły: ")
    textobject.moveCursor(15, 5)
    for category in categories:
        if sum_category(30*months, user_id, category) == None:
            category_expenses = 0
        else:
            category_expenses = sum_category(30*months, user_id, category)
        categories[category] = category_expenses
        textobject.textLine(text=f"- {category} - {category_expenses} zł.")
    
    textobject.moveCursor(-15, 5)
    max_category = max(categories, key=categories.get)
    textobject.textLine(text=f"Największe wydatki były na {max_category}.")
    c.drawText(textobject)

    if months == 12:
        add_plot(user_id)
        c.drawImage('wykres.png', 50, 100, width=500, height=300)
    
    c.showPage()

    c.save()

generate_raport(11, 'raport1.pdf', 1)
generate_raport(11, 'raport3.pdf', 3)
generate_raport(11, 'raport6.pdf', 6)
generate_raport(11, 'raport12.pdf', 12)

data = date.today()
nazwa_pdf = f"raport-{data}"
merger = PdfWriter()
for pdf in [f'raport1.pdf', f'raport3.pdf', f'raport6.pdf', f'raport12.pdf']:
    merger.append(pdf)
merger.write(nazwa_pdf)
merger.close()

os.remove('wykres.png')
os.remove(f'raport1.pdf')
os.remove(f'raport3.pdf')
os.remove(f'raport6.pdf')
os.remove(f'raport12.pdf')

# income = {'name': 'praca Andrzeja', 'money': 10000, 'periodicity': True, 'period_amount': 1, 'period_type': 'miesiąc', 'user_id': 11, 'date': '2022-08-15'}
# add_income(income)
# income = {'name': 'praca Anny', 'money': 1650, 'periodicity': True, 'period_amount': 1, 'period_type': 'miesiąc', 'user_id': 11, 'date': '2022-08-01'}
# add_income(income)
# income = {'name': '500plus', 'money': 1000, 'periodicity': True, 'period_amount': 1, 'period_type': 'miesiąc', 'user_id': 11, 'date': '2022-08-17'}
# add_income(income)

# expense = {'category': 'leki', 'name': 'antyalergiczne, witaminy', 'money': 120, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'leki', 'name': '', 'money': 50, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'filtry, chemia', 'money': 65, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'kosmetyki', 'money': 50, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'zęby', 'money': 100, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 3, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'pieluchy', 'money': 36, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 7, 'period_type': 'dzień'}
# add_expense(expense)
# expense = {'category': 'rozrywka', 'name': 'basen dzieci', 'money': 2500, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 6, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'rozrywka', 'name': 'disneyplus', 'money': 75, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'rok'}
# add_expense(expense)
# expense = {'category': 'pies', 'name': 'karma', 'money': 270, 'date': '2022-09-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 3, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'pies', 'name': 'przysmaki', 'money': 3, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'dzień'}
# add_expense(expense)
# expense = {'category': 'auto', 'name': 'paliwo', 'money': 400, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'auto', 'name': 'przegląd, ubezpieczenie', 'money': 1200, 'date': '2022-07-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'rok'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'ubezpieczenia', 'money': 420, 'date': '2022-09-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'rok'}
# add_expense(expense)
# expense = {'category': 'inne', 'name': 'studia Andrzeja', 'money': 2100, 'date': '2022-10-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 6, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'opłaty domowe', 'name': 'czynsz', 'money': 620, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'rachunek', 'name': 'prąd, gaz', 'money': 500, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'rachunek', 'name': 'telefon, internet', 'money': 120, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'rachunek', 'name': 'żłobki', 'money': 2800, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'kredyt', 'name': 'mieszkanie', 'money': 2300, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'kredyt', 'name': 'Andrzeja', 'money': 1700, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'inne', 'name': 'firma', 'money': 600, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'miesiąc'}
# add_expense(expense)
# expense = {'category': 'jedzenie', 'name': 'tygodniowe', 'money': 300, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 7, 'period_type': 'dzień'}
# add_expense(expense)
# expense = {'category': 'jedzenie', 'name': 'codzienne', 'money': 35, 'date': '2022-08-10', 'user_id': 11, 'periodicity': 1, 'period_amount': 1, 'period_type': 'dzień'}
# add_expense(expense)

connection.close()