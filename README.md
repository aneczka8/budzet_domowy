Jest to silnik do aplikacji zarządzania budżetem domowym.

Zawiera funkcje do dodawania oraz logowania użytkownika.
Funkcje do dodawania i usuwania wpływów i wydatków.
Oblicza sumę oraz średnią całych wpływów i wydatków z danego okresu oraz liczy ich bilans. A także z poszczególnych kategorii (np. wydatki na jedzenie).
Dla czytelnego zobrazowania generuje raport z sytuacji finansowej z ostatniego miesiąca, trzech, sześciu oraz dwunastu miesięcy.

W tym celu łączy się z bazą danych i na niej pracuje. W związku z tym należy wpisać dane do logowania z bazą danych.

Poniżej zamieszczam kod do stworzenia odpowiedniej bazy danych:

    CREATE DATABASE budzet_domowy;
    CREATE TABLE expenses(id INT(11) NOT NULL AUTO_INCREMENT, category VARCHAR(45), name VARCHAR(45), money FLOAT, periodicity TINYINT(4), period_amount INT(11), period_type VARCHAR(45), date DATE, user_id INT(11), PRIMARY KEY (id))
    CREATE TABLE income(id INT(11) NOT NULL AUTO_INCREMENT, name VARCHAR(45), money FLOAT, periodicity TINYINT(4), period_amount INT(11), period_type VARCHAR(45), date DATE, user_id INT(11), PRIMARY KEY (id))
    CREATE TABLE users(user_id INT(11) NOT NULL AUTO_INCREMENT, username VARCHAR(45), password_hash LONGTEXT, PRIMARY KEY (user_id))

Do wygenerowania testowego raportu można użyć linii 282 - 334, które na początku są wykomentowane.

W linii 194 załączam czcionkę, która używa polskich znaków. Także należy ją zainstalować (lub użyć innej) i wpisać odpowiednią ścieżkę.