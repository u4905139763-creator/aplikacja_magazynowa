import streamlit as st
import sqlite3
import pandas as pd

# Funkcja inicjalizująca bazę danych lokalnie (SQLite)
def init_db():
    conn = sqlite3.connect('magazyn.db', check_same_thread=False)
    c = conn.cursor()
    # Tabela Kategorie wg schematu: id, nazwa, opis
    c.execute('''CREATE TABLE IF NOT EXISTS Kategorie (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nazwa TEXT NOT NULL,
                    opis TEXT)''')
    # Tabela produkty wg schematu: id, nazwa, liczba, cena, kategoria_id
    c.execute('''CREATE TABLE IF NOT EXISTS produkty (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nazwa TEXT NOT NULL,
                    liczba INTEGER,
                    cena REAL,
                    kategoria_id INTEGER,
                    FOREIGN KEY (kategoria_id) REFERENCES Kategorie(id) ON DELETE CASCADE)''')
    conn.commit()
    return conn

conn = init_db()

st.set_page_config(page_title="Zarządzanie Bazą Supabase", layout="wide")
st.title("📦 System Zarządzania Produktami i Kategoriami")

tab1, tab2 = st.tabs(["🛍️ Produkty", "📂 Kategorie"])

# --- TAB KATEGORIE ---
with tab2:
    st.header("Zarządzanie Kategoriami")
    
    with st.form("form_kat"):
        st.subheader("Dodaj nową kategorię")
        kat_nazwa = st.text_input("Nazwa (Tekst)")
        kat_opis = st.text_area("Opis (Tekst)")
        if st.form_submit_button("Dodaj kategorię"):
            if kat_nazwa:
                conn.execute("INSERT INTO Kategorie (nazwa, opis) VALUES (?, ?)", (kat_nazwa, kat_opis))
                conn.commit()
                st.success(f"Dodano kategorię: {kat_nazwa}")
                st.rerun()

    st.subheader("Lista kategorii")
    df_kat = pd.read_sql_query("SELECT * FROM Kategorie", conn)
    st.dataframe(df_kat, use_container_width=True)

    if not df_kat.empty:
        id_to_del = st.selectbox("Wybierz ID kategorii do usunięcia", df_kat['id'])
        if st.button("Usuń kategorię", help="Usunie również wszystkie produkty w tej kategorii"):
            conn.execute("DELETE FROM Kategorie WHERE id = ?", (int(id_to_del),))
            conn.commit()
            st.rerun()

# --- TAB PRODUKTY ---
with tab1:
    st.header("Zarządzanie Produktami")
    
    df_kat_check = pd.read_sql_query("SELECT id, nazwa FROM Kategorie", conn)
    
    if df_kat_check.empty:
        st.warning("Najpierw dodaj przynajmniej jedną kategorię w zakładce 'Kategorie'!")
    else:
        with st.form("form_prod"):
            st.subheader("Dodaj nowy produkt")
            prod_nazwa = st.text_input("Nazwa produktu (Tekst)")
            prod_liczba = st.number_input("Liczba (int8)", min_value=0, step=1)
            prod_cena = st.number_input("Cena (Numeryczne)", min_value=0.0, step=0.01)
            # Mapowanie nazwy kategorii na jej ID (klucz obcy)
            opcje_kat = {row['nazwa']: row['id'] for _, row in df_kat_check.iterrows()}
            wybrana_kat = st.selectbox("Kategoria (kategoria_id)", list(opcje_kat.keys()))
            
            if st.form_submit_button("Dodaj produkt"):
                if prod_nazwa:
                    conn.execute("INSERT INTO produkty (nazwa, liczba, cena, kategoria_id) VALUES (?, ?, ?, ?)",
                                 (prod_nazwa, prod_liczba, prod_cena, opcje_kat[wybrana_kat]))
                    conn.commit()
                    st.success(f"Dodano produkt: {prod_nazwa}")
                    st.rerun()

    st.subheader("Lista produktów")
    # Join dla czytelności wyświetlania
    query = """
    SELECT p.id, p.nazwa, p.liczba, p.cena, k.nazwa as kategoria 
    FROM produkty p 
    LEFT JOIN Kategorie k ON p.kategoria_id = k.id
    """
    df_prod = pd.read_sql_query(query, conn)
    st.dataframe(df_prod, use_container_width=True)

    if not df_prod.empty:
        p_id_to_del = st.selectbox("Wybierz ID produktu do usunięcia", df_prod['id'])
        if st.button("Usuń produkt"):
            conn.execute("DELETE FROM produkty WHERE id = ?", (int(p_id_to_del),))
            conn.commit()
            st.rerun()
