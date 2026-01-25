import streamlit as st
import pandas as pd
from supabase import create_client

# --- KONFIGURACJA POŁĄCZENIA ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

st.set_page_config(page_title="Magazyn Supabase", layout="wide")
st.title("⚡ Zarządzanie Bazą Supabase")

tab1, tab2 = st.tabs(["🛍️ Produkty", "📂 Kategorie"])

# --- TABELA: KATEGORIE ---
with tab2:
    st.header("Kategorie")
    
    # Dodawanie
    with st.expander("Dodaj nową kategorię"):
        with st.form("add_cat"):
            nazwa = st.text_input("Nazwa")
            opis = st.text_area("Opis")
            if st.form_submit_button("Wyślij do Supabase"):
                data, count = supabase.table("Kategorie").insert({"nazwa": nazwa, "opis": opis}).execute()
                st.success("Dodano pomyślnie!")
                st.rerun()

    # Wyświetlanie i usuwanie
    res_k = supabase.table("Kategorie").select("*").execute()
    df_k = pd.DataFrame(res_k.data)
    
    if not df_k.empty:
        st.dataframe(df_k, use_container_width=True)
        cat_to_del = st.selectbox("Wybierz ID kategorii do usunięcia", df_k['id'])
        if st.button("Usuń kategorię"):
            supabase.table("Kategorie").delete().eq("id", cat_id).execute()
            st.rerun()

# --- TABELA: PRODUKTY ---
with tab1:
    st.header("Produkty")
    
    # Dodawanie produktu
    with st.expander("Dodaj nowy produkt"):
        if not df_k.empty:
            with st.form("add_prod"):
                p_nazwa = st.text_input("Nazwa produktu")
                p_liczba = st.number_input("Liczba", step=1)
                p_cena = st.number_input("Cena", step=0.01)
                # Wybór kategorii z listy pobranej z Supabase
                p_kat = st.selectbox("Kategoria", df_k['id'], 
                                   format_func=lambda x: df_k[df_k['id']==x]['nazwa'].values[0])
                
                if st.form_submit_button("Zapisz produkt"):
                    payload = {
                        "nazwa": p_nazwa, 
                        "liczba": p_liczba, 
                        "Cena": p_cena, 
                        "kategoria_id": p_kat
                    }
                    supabase.table("produkty").insert(payload).execute()
                    st.success("Produkt zapisany!")
                    st.rerun()
        else:
            st.error("Brak kategorii w bazie!")

    # Wyświetlanie produktów
    res_p = supabase.table("produkty").select("id, nazwa, liczba, Cena, Kategorie(nazwa)").execute()
    if res_p.data:
        # Spłaszczanie wyniku dla czytelności (relacja z Kategorie)
        flat_data = []
        for item in res_p.data:
            item['kategoria_nazwa'] = item['Kategorie']['nazwa'] if item['Kategorie'] else "Brak"
            flat_data.append(item)
        
        df_p = pd.DataFrame(flat_data).drop(columns=['Kategorie'])
        st.dataframe(df_p, use_container_width=True)

        # Usuwanie produktu
        p_id_del = st.selectbox("Wybierz ID produktu do usunięcia", df_p['id'])
        if st.button("Usuń wybrany produkt"):
            supabase.table("produkty").delete().eq("id", p_id_del).execute()
            st.rerun()
