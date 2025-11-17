import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import psycopg2

st.set_page_config(page_title="Sante", page_icon="H", layout="wide")

def get_query(sql):
    try:
        conn = psycopg2.connect(host='localhost', port=5432, user='dwh_user', password='dwh_password', database='datawarehouse')
        cur = conn.cursor()
        cur.execute(sql)
        cols = [d[0] for d in cur.description]
        data = cur.fetchall()
        cur.close()
        conn.close()
        return pd.DataFrame(data, columns=cols)
    except:
        return pd.DataFrame()

# ===== HEADER =====
st.markdown("
st.markdown("Analyse des donnees medicales en temps reel")

# ===== SIDEBAR =====
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Selectionnez une page :",
    ["Dashboard", "Patients", "Tests", "Medicaments", "Rendez-vous", "Recherche"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Informations")
st.sidebar.markdown(f"Mise a jour : {datetime.now().strftime('%d/%m/%Y %H:%M')}")
st.sidebar.markdown("Source : Data Warehouse PostgreSQL")

# ===== PAGE 1 : DASHBOARD PRINCIPAL =====
if page == "Dashboard":
    st.header("Vue d'ensemble")
    
    # Recuperer les statistiques globales
    stats_query = """
    SELECT 
        (SELECT COUNT(*) FROM staging.stg_patients) as total_patients,
        (SELECT COUNT(*) FROM staging.stg_medical_tests) as total_tests,
        (SELECT COUNT(*) FROM staging.stg_medications) as total_medications,
        (SELECT COUNT(*) FROM staging.stg_appointments) as total_appointments;
    """
    stats = get_query(stats_query)
    
    if not stats.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Patients", int(stats['total_patients'].values[0]))
        with col2:
            st.metric("Tests Medicaux", int(stats['total_tests'].values[0]))
        with col3:
            st.metric("Medicaments", int(stats['total_medications'].values[0]))
        with col4:
            st.metric("Rendez-vous", int(stats['total_appointments'].values[0]))
    
    st.markdown("---")
    
    # Distribution par genre
    st.subheader("Distribution par Genre")
    
    gender_query = """
    SELECT gender, COUNT(*) as count
    FROM staging.stg_patients
    GROUP BY gender
    ORDER BY count DESC;
    """
    gender_df = get_query(gender_query)
    
    if not gender_df.empty:
        fig = px.pie(gender_df, values='count', names='gender', title="Repartition Genre")
        st.plotly_chart(fig, use_container_width=True)
    
    # Distribution Age
    st.subheader("Distribution des Ages")
    
    age_query = """
    SELECT 
        CASE 
            WHEN age < 30 THEN '< 30'
            WHEN age < 40 THEN '30-40'
            WHEN age < 50 THEN '40-50'
            WHEN age < 60 THEN '50-60'
            ELSE '60+'
        END as age_group,
        COUNT(*) as count
    FROM staging.stg_patients
    GROUP BY age_group
    ORDER BY age_group;
    """
    age_df = get_query(age_query)
    
    if not age_df.empty:
        fig = px.bar(age_df, x='age_group', y='count', title="Distribution par Groupe d'Age")
        st.plotly_chart(fig, use_container_width=True)

# ===== PAGE 2 : PATIENTS =====
elif page == "Patients":
    st.header("Gestion des Patients")
    
    st.subheader("Liste des Patients")
    
    patients_query = """
    SELECT 
        patient_id as ID,
        first_name || ' ' || last_name as Nom,
        age as Age,
        gender as Genre,
        blood_type as "Groupe Sanguin"
    FROM staging.stg_patients
    ORDER BY patient_id
    LIMIT 100;
    """
    patients_df = get_query(patients_query)
    
    if not patients_df.empty:
        st.dataframe(patients_df, use_container_width=True)

# ===== PAGE 3 : TESTS MÉDICAUX =====
elif page == "Tests":
    st.header("Tests Medicaux")
    
    st.subheader("Repartition des Tests")
    
    test_query = """
    SELECT test_type, COUNT(*) as Nombre
    FROM staging.stg_medical_tests
    GROUP BY test_type
    ORDER BY COUNT(*) DESC;
    """
    test_df = get_query(test_query)
    
    if not test_df.empty:
        fig = px.bar(test_df, x='test_type', y='Nombre', title="Types de Tests")
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    st.subheader("Niveaux de Cholesterol")
    
    chol_query = """
    SELECT 
        CASE 
            WHEN cholesterol < 200 THEN 'Normal'
            WHEN cholesterol < 240 THEN 'Limite'
            ELSE 'Eleve'
        END as level,
        COUNT(*) as count
    FROM staging.stg_medical_tests
    GROUP BY level
    ORDER BY count DESC;
    """
    chol_df = get_query(chol_query)
    
    if not chol_df.empty:
        fig = px.pie(chol_df, values='count', names='level', title="Cholesterol")
        st.plotly_chart(fig)

# ===== PAGE 4 : MÉDICAMENTS =====
elif page == "Medicaments":
    st.header("Medicaments Prescrits")
    
    st.subheader("Top Medicaments")
    
    med_query = """
    SELECT 
        medication_name as Medicament,
        COUNT(*) as "Nombre Prescriptions"
    FROM staging.stg_medications
    GROUP BY medication_name
    ORDER BY COUNT(*) DESC
    LIMIT 10;
    """
    med_df = get_query(med_query)
    
    if not med_df.empty:
        fig = px.bar(med_df, x='Medicament', y='Nombre Prescriptions')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(med_df, use_container_width=True)

# ===== PAGE 5 : RENDEZ-VOUS =====
elif page == "Rendez-vous":
    st.header("Rendez-vous Medicaux")
    
    st.subheader("Par Specialite")
    
    appt_query = """
    SELECT 
        specialty as Specialite,
        COUNT(*) as "Nombre RDV"
    FROM staging.stg_appointments
    GROUP BY specialty
    ORDER BY COUNT(*) DESC;
    """
    appt_df = get_query(appt_query)
    
    if not appt_df.empty:
        fig = px.bar(appt_df, x='Specialite', y='Nombre RDV')
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(appt_df, use_container_width=True)

# ===== PAGE 6 : RECHERCHE =====
elif page == "Recherche":
    st.header("Recherche Avancee")
    
    st.subheader("Trouver un Patient")
    
    search_name = st.text_input("Entrez le nom du patient :")
    
    if search_name:
        search_query = f"""
        SELECT 
            patient_id as ID,
            first_name || ' ' || last_name as Nom,
            age as Age,
            gender as Genre,
            blood_type as "Groupe Sanguin"
        FROM staging.stg_patients
        WHERE LOWER(first_name || ' ' || last_name) LIKE LOWER('%{search_name}%')
        LIMIT 10;
        """
        results_df = get_query(search_query)
        
        if not results_df.empty:
            st.success(f"{len(results_df)} resultat(s) trouve(s)")
            st.dataframe(results_df, use_container_width=True)
        else:
            st.warning("Aucun patient trouve")
    
    st.markdown("---")
    st.subheader("Recherche par Criteres")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_age = st.slider("Age minimum", 20, 80, 20)
    
    with col2:
        max_age = st.slider("Age maximum", 20, 80, 80)
    
    criteria_query = f"""
    SELECT 
        patient_id as ID,
        first_name || ' ' || last_name as Nom,
        age as Age,
        gender as Genre
    FROM staging.stg_patients
    WHERE age BETWEEN {min_age} AND {max_age}
    ORDER BY age;
    """
    
    criteria_df = get_query(criteria_query)
    
    if not criteria_df.empty:
        st.dataframe(criteria_df, use_container_width=True)
        st.info(f"{len(criteria_df)} patients correspondent a ces criteres")

# ===== FOOTER =====
st.markdown("---")
st.markdown("<div style='text-align: center; color: gray;'><small>Dashboard Sante | PostgreSQL | Streamlit</small></div>", unsafe_allow_html=True)
