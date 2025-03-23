import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import uuid
import json
import os
from PIL import Image
import io
import base64

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Journal de Bord du Jardin",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fonctions utilitaires
def load_data():
    """Charger les données depuis les fichiers JSON"""
    if os.path.exists('garden_plants.json'):
        with open('garden_plants.json', 'r', encoding='utf-8') as f:
            plants = json.load(f)
    else:
        plants = []
    
    if os.path.exists('garden_notes.json'):
        with open('garden_notes.json', 'r', encoding='utf-8') as f:
            notes = json.load(f)
    else:
        notes = []
    
    return plants, notes

def save_data(plants, notes):
    """Sauvegarder les données dans des fichiers JSON"""
    with open('garden_plants.json', 'w', encoding='utf-8') as f:
        json.dump(plants, f, ensure_ascii=False, indent=4)
    
    with open('garden_notes.json', 'w', encoding='utf-8') as f:
        json.dump(notes, f, ensure_ascii=False, indent=4)

def format_date(date_string):
    """Formater une date pour l'affichage"""
    if isinstance(date_string, str):
        dt = datetime.strptime(date_string, '%Y-%m-%d')
        return dt.strftime('%d %B %Y')
    return ''

def get_plant_by_id(plants, plant_id):
    """Récupérer une plante par son ID"""
    for plant in plants:
        if plant['id'] == plant_id:
            return plant
    return None

def get_notes_for_plant(notes, plant_id):
    """Récupérer les notes pour une plante spécifique"""
    return [note for note in notes if note['plantId'] == plant_id]

def get_container_name(container_id):
    """Obtenir le nom du contenant"""
    containers = {
        'carton-12x12': 'Carton 12x12',
        'pot-petit': 'Petit pot',
        'pot-moyen': 'Pot moyen',
        'pot-grand': 'Grand pot',
        'pleine-terre': 'Pleine terre'
    }
    return containers.get(container_id, container_id)

def days_from_planting(planting_date):
    """Calculer le nombre de jours depuis la plantation"""
    planted = datetime.strptime(planting_date, '%Y-%m-%d')
    today = datetime.now()
    return (today - planted).days

def generate_unique_id():
    """Générer un ID unique"""
    return str(uuid.uuid4())

def handle_image_upload(uploaded_file):
    """Gérer l'upload d'une image et la convertir en base64"""
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        encoded = base64.b64encode(bytes_data).decode()
        return f"data:{uploaded_file.type};base64,{encoded}"
    return None

def display_image(image_data):
    """Afficher une image depuis des données base64"""
    if image_data:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            st.image(image_data)
        else:
            st.image(image_data)

# Initialisation de l'état de session
if 'plants' not in st.session_state:
    plants, notes = load_data()
    st.session_state['plants'] = plants
    st.session_state['notes'] = notes
else:
    plants = st.session_state['plants']
    notes = st.session_state['notes']

# Styles CSS personnalisés
st.markdown("""
<style>
    .main-header {
        color: #2E7D32;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .plant-card {
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .card-header {
        background-color: #8BC34A;
        color: white;
        padding: 0.7rem;
        border-radius: 8px 8px 0 0;
        margin: -1rem -1rem 1rem -1rem;
        font-weight: bold;
    }
    
    .plant-details strong {
        color: #2E7D32;
    }
    
    .stat-tag {
        background-color: #E8F5E9;
        padding: 0.3rem 0.6rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin-right: 0.5rem;
    }
    
    .note-entry {
        border-left: 3px solid #8BC34A;
        padding-left: 1rem;
        margin-bottom: 1.5rem;
    }
    
    .note-date {
        color: #666;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .centered {
        text-align: center;
    }
    
    hr {
        margin: 2rem 0;
        border-color: #E8F5E9;
    }
</style>
""", unsafe_allow_html=True)

# Entête de la page
st.markdown("<h1 class='main-header'>Journal de Bord du Jardin</h1>", unsafe_allow_html=True)
st.markdown("<p class='centered'>Suivez toutes vos plantations et leur progression</p>", unsafe_allow_html=True)

# Navigation principale
nav_option = st.sidebar.radio(
    "Navigation",
    ["Tableau de bord", "Mes Plantes", "Ajouter une Plante", "Notes", "Statistiques"]
)

# Section Tableau de bord
if nav_option == "Tableau de bord":
    st.header("Tableau de Bord")
    
    # Alerte du tableau de bord
    if len(plants) == 0:
        st.info("Bienvenue dans votre journal de bord du jardin. Commencez par ajouter vos premières plantations.")
    else:
        st.success(f"Vous avez {len(plants)} plantes enregistrées dans votre journal.")
    
    # Plantations récentes
    st.subheader("Plantations récentes")
    
    if len(plants) == 0:
        st.write("Aucune plante enregistrée pour le moment.")
    else:
        # Trier les plantes par date (les plus récentes d'abord)
        sorted_plants = sorted(plants, key=lambda x: x['date'], reverse=True)
        recent_plants = sorted_plants[:3]
        
        cols = st.columns(min(len(recent_plants), 3))
        
        for i, plant in enumerate(recent_plants):
            with cols[i]:
                st.markdown(f"<div class='plant-card'>", unsafe_allow_html=True)
                st.markdown(f"<div class='card-header'>{plant['name']} ({plant.get('variety', 'Variété non spécifiée')})</div>", unsafe_allow_html=True)
                
                plant_notes = get_notes_for_plant(notes, plant['id'])
                last_note = None
                
                if plant_notes:
                    last_note = sorted(plant_notes, key=lambda x: x['date'], reverse=True)[0]
                
                if 'image' in plant and plant['image']:
                    display_image(plant['image'])
                elif last_note and 'image' in last_note and last_note['image']:
                    display_image(last_note['image'])
                
                st.markdown(f"""
                <div class='plant-details'>
                    <p><strong>Date de plantation:</strong> {format_date(plant['date'])}</p>
                    <p><strong>Contenant:</strong> {get_container_name(plant['container'])}</p>
                    <p><strong>Terreau:</strong> {plant.get('soil', 'Non spécifié')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if last_note:
                    stats_html = "<div class='plant-stats'>"
                    if 'height' in last_note and last_note['height']:
                        stats_html += f"<span class='stat-tag'>Hauteur: {last_note['height']} cm</span>"
                    if 'leaves' in last_note and last_note['leaves']:
                        stats_html += f"<span class='stat-tag'>Feuilles: {last_note['leaves']}</span>"
                    stats_html += "</div>"
                    st.markdown(stats_html, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
    
    # Notes récentes
    st.subheader("Dernières notes")
    
    if len(notes) == 0:
        st.write("Aucune note enregistrée pour le moment.")
    else:
        # Trier les notes par date (les plus récentes d'abord)
        sorted_notes = sorted(notes, key=lambda x: x['date'], reverse=True)
        recent_notes = sorted_notes[:5]
        
        for note in recent_notes:
            plant = get_plant_by_id(plants, note['plantId'])
            if not plant:
                continue
            
            st.markdown(f"""
            <div class='note-entry'>
                <div class='note-date'>{format_date(note['date'])} - {plant['name']}</div>
                <p>{note['content']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if 'image' in note and note['image']:
                display_image(note['image'])
            
            stats_html = "<div class='plant-stats'>"
            if 'height' in note and note['height']:
                stats_html += f"<span class='stat-tag'>Hauteur: {note['height']} cm</span>"
            if 'leaves' in note and note['leaves']:
                stats_html += f"<span class='stat-tag'>Feuilles: {note['leaves']}</span>"
            stats_html += "</div>"
            st.markdown(stats_html, unsafe_allow_html=True)

# Section Liste des Plantes
elif nav_option == "Mes Plantes":
    st.header("Mes Plantes")
    
    # Barre de recherche
    search_term = st.text_input("Rechercher une plante...", "")
    
    # Filtrer les plantes en fonction de la recherche
    filtered_plants = plants
    if search_term:
        filtered_plants = [
            plant for plant in plants
            if search_term.lower() in plant['name'].lower() or
               (plant.get('variety', "") and search_term.lower() in plant['variety'].lower())
        ]
    
    if not filtered_plants:
        st.write("Aucune plante trouvée.")
    else:
        # Afficher les plantes en grille (2 colonnes)
        for i in range(0, len(filtered_plants), 2):
            cols = st.columns(2)
            
            for j in range(2):
                if i + j < len(filtered_plants):
                    plant = filtered_plants[i + j]
                    
                    with cols[j]:
                        st.markdown(f"<div class='plant-card'>", unsafe_allow_html=True)
                        st.markdown(f"<div class='card-header'>{plant['name']} ({plant.get('variety', 'Variété non spécifiée')})</div>", unsafe_allow_html=True)
                        
                        plant_notes = get_notes_for_plant(notes, plant['id'])
                        last_note = None
                        
                        if plant_notes:
                            last_note = sorted(plant_notes, key=lambda x: x['date'], reverse=True)[0]
                        
                        if 'image' in plant and plant['image']:
                            display_image(plant['image'])
                        elif last_note and 'image' in last_note and last_note['image']:
                            display_image(last_note['image'])
                        
                        st.markdown(f"""
                        <div class='plant-details'>
                            <p><strong>Date de plantation:</strong> {format_date(plant['date'])}</p>
                            <p><strong>Contenant:</strong> {get_container_name(plant['container'])}</p>
                            <p><strong>Terreau:</strong> {plant.get('soil', 'Non spécifié')}</p>
                            <p><strong>Emplacement:</strong> {plant.get('location', 'Non spécifié')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if plant.get('notes'):
                            st.markdown(f"<p><strong>Notes:</strong> {plant['notes']}</p>", unsafe_allow_html=True)
                        
                        if last_note:
                            stats_html = "<div class='plant-stats'>"
                            if 'height' in last_note and last_note['height']:
                                stats_html += f"<span class='stat-tag'>Hauteur: {last_note['height']} cm</span>"
                            if 'leaves' in last_note and last_note['leaves']:
                                stats_html += f"<span class='stat-tag'>Feuilles: {last_note['leaves']}</span>"
                            stats_html += f"<span class='stat-tag'>Âge: {days_from_planting(plant['date'])} jours</span>"
                            stats_html += "</div>"
                            st.markdown(stats_html, unsafe_allow_html=True)
                        
                        # Boutons d'action
                        col1, col2 = st.columns(2)
                        
                        # Bouton pour ajouter une note
                        if col1.button(f"Ajouter une note", key=f"add_note_{plant['id']}"):
                            st.session_state['selected_plant_id'] = plant['id']
                            # Redirection vers la page des notes
                            st.experimental_rerun()
                        
                        # Bouton pour supprimer la plante
                        if col2.button(f"Supprimer", key=f"delete_{plant['id']}"):
                            # Demander confirmation
                            confirm = st.checkbox(f"Confirmer la suppression de {plant['name']}", key=f"confirm_{plant['id']}")
                            
                            if confirm:
                                # Supprimer les notes associées
                                st.session_state['notes'] = [note for note in notes if note['plantId'] != plant['id']]
                                # Supprimer la plante
                                st.session_state['plants'] = [p for p in plants if p['id'] != plant['id']]
                                # Sauvegarder les données
                                save_data(st.session_state['plants'], st.session_state['notes'])
                                st.success(f"Plante {plant['name']} supprimée avec succès !")
                                st.experimental_rerun()
                        
                        st.markdown("</div>", unsafe_allow_html=True)

# Section Ajouter une Plante
elif nav_option == "Ajouter une Plante":
    st.header("Ajouter une Nouvelle Plante")
    
    with st.form("plant_form"):
        # Champs du formulaire
        name = st.text_input("Nom de la Plante", required=True)
        variety = st.text_input("Variété")
        
        container = st.selectbox(
            "Contenant",
            ["carton-12x12", "pot-petit", "pot-moyen", "pot-grand", "pleine-terre"],
            format_func=get_container_name
        )
        
        soil = st.text_input("Type de Terreau")
        date = st.date_input("Date de Plantation", datetime.now())
        location = st.text_input("Emplacement")
        plant_notes = st.text_area("Notes Initiales")
        
        uploaded_file = st.file_uploader("Photo (optionnelle)", type=["jpg", "jpeg", "png"])
        
        if uploaded_file:
            st.image(uploaded_file, caption="Aperçu de l'image")
        
        submitted = st.form_submit_button("Ajouter la Plante")
        
        if submitted:
            # Convertir la date en string
            date_str = date.strftime('%Y-%m-%d')
            
            # Gérer l'image
            image = handle_image_upload(uploaded_file)
            
            # Créer l'objet plante
            plant = {
                'id': generate_unique_id(),
                'name': name,
                'variety': variety,
                'container': container,
                'soil': soil,
                'date': date_str,
                'location': location,
                'notes': plant_notes,
                'image': image
            }
            
            # Ajouter la plante à la liste
            st.session_state['plants'].append(plant)
            
            # Sauvegarder les données
            save_data(st.session_state['plants'], st.session_state['notes'])
            
            st.success(f"Plante {name} ajoutée avec succès !")
            
            # Option pour ajouter une autre plante ou retourner à la liste
            if st.button("Voir la liste des plantes"):
                st.session_state['nav_option'] = "Mes Plantes"
                st.experimental_rerun()

# Section Notes
elif nav_option == "Notes":
    st.header("Notes et Observations")
    
    # Sélecteur de plante
    plant_options = [(p['id'], f"{p['name']} ({p.get('variety', 'Variété non spécifiée')})") for p in plants]
    plant_options.insert(0, ("", "Toutes les plantes"))
    
    # Si une plante a été sélectionnée depuis une autre page
    default_plant_index = 0
    if 'selected_plant_id' in st.session_state:
        for i, (p_id, _) in enumerate(plant_options):
            if p_id == st.session_state['selected_plant_id']:
                default_plant_index = i
                # Réinitialiser la sélection pour les futurs chargements
                st.session_state.pop('selected_plant_id', None)
                break
    
    selected_plant_id = st.selectbox(
        "Sélectionner une plante",
        options=[p[0] for p in plant_options],
        format_func=lambda x: next((p[1] for p in plant_options if p[0] == x), ""),
        index=default_plant_index
    )
    
    # Formulaire pour ajouter une nouvelle note
    st.subheader("Ajouter une observation")
    
    # Vérifier si une plante est sélectionnée pour le formulaire
    if not plants:
        st.warning("Ajoutez d'abord une plante avant de pouvoir ajouter des notes.")
    elif not selected_plant_id:
        st.info("Sélectionnez une plante pour ajouter une note.")
    else:
        with st.form("note_form"):
            date = st.date_input("Date", datetime.now())
            content = st.text_area("Observation", required=True)
            
            col1, col2 = st.columns(2)
            with col1:
                height = st.number_input("Hauteur (cm)", min_value=0.0, step=0.1)
            with col2:
                leaves = st.number_input("Nombre de feuilles", min_value=0, step=1)
            
            uploaded_file = st.file_uploader("Photo", type=["jpg", "jpeg", "png"])
            
            if uploaded_file:
                st.image(uploaded_file, caption="Aperçu de l'image")
            
            submitted = st.form_submit_button("Ajouter l'Observation")
            
            if submitted:
                # Convertir la date en string
                date_str = date.strftime('%Y-%m-%d')
                
                # Gérer l'image
                image = handle_image_upload(uploaded_file)
                
                # Créer l'objet note
                note = {
                    'id': generate_unique_id(),
                    'plantId': selected_plant_id,
                    'date': date_str,
                    'content': content,
                    'height': height if height > 0 else None,
                    'leaves': leaves if leaves > 0 else None,
                    'image': image
                }
                
                # Ajouter la note à la liste
                st.session_state['notes'].append(note)
                
                # Sauvegarder les données
                save_data(st.session_state['plants'], st.session_state['notes'])
                
                st.success("Note ajoutée avec succès !")
                
                # Recharger la page pour afficher la nouvelle note
                st.experimental_rerun()
    
    # Journal d'Observations
    st.subheader("Journal d'Observations")
    
    # Filtrer les notes par plante si une plante est sélectionnée
    filtered_notes = notes
    if selected_plant_id:
        filtered_notes = [note for note in notes if note['plantId'] == selected_plant_id]
    
    # Trier les notes par date (les plus récentes d'abord)
    filtered_notes = sorted(filtered_notes, key=lambda x: x['date'], reverse=True)
    
    if not filtered_notes:
        st.write("Aucune note trouvée.")
    else:
        for note in filtered_notes:
            plant = get_plant_by_id(plants, note['plantId'])
            if not plant:
                continue
            
            col1, col2 = st.columns([5, 1])
            
            with col1:
                st.markdown(f"""
                <div class='note-entry'>
                    <div class='note-date'>{format_date(note['date'])} - {plant['name']}</div>
                    <p>{note['content']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if 'image' in note and note['image']:
                    display_image(note['image'])
                
                stats_html = "<div class='plant-stats'>"
                if 'height' in note and note['height']:
                    stats_html += f"<span class='stat-tag'>Hauteur: {note['height']} cm</span>"
                if 'leaves' in note and note['leaves']:
                    stats_html += f"<span class='stat-tag'>Feuilles: {note['leaves']}</span>"
                stats_html += "</div>"
                st.markdown(stats_html, unsafe_allow_html=True)
            
            with col2:
                # Bouton pour supprimer la note
                if st.button("Supprimer", key=f"delete_note_{note['id']}"):
                    st.session_state['notes'] = [n for n in notes if n['id'] != note['id']]
                    save_data(st.session_state['plants'], st.session_state['notes'])
                    st.success("Note supprimée !")
                    st.experimental_rerun()
            
            st.markdown("<hr>", unsafe_allow_html=True)

# Section Statistiques
elif nav_option == "Statistiques":
    st.header("Statistiques et Progrès")
    
    if not plants:
        st.warning("Ajoutez des plantes pour voir les statistiques.")
    else:
        # Sélecteur de plante
        plant_options = [(p['id'], f"{p['name']} ({p.get('variety', 'Variété non spécifiée')})") for p in plants]
        plant_options.insert(0, ("", "Toutes les plantes"))
        
        selected_plant_id = st.selectbox(
            "Sélectionner une plante",
            options=[p[0] for p in plant_options],
            format_func=lambda x: next((p[1] for p in plant_options if p[0] == x), "")
        )
        
        # Filtrer les notes en fonction de la plante sélectionnée
        filtered_notes = notes
        if selected_plant_id:
            filtered_notes = [note for note in notes if note['plantId'] == selected_plant_id]
        
        # Mise en page deux colonnes pour les graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Croissance des Plantes")
            
            # Préparer les données pour le graphique de croissance
            if selected_plant_id:
                # Si une plante spécifique est sélectionnée
                plant_notes = [note for note in filtered_notes if 'height' in note and note['height']]
                
                if plant_notes:
                    # Trier par date
                    plant_notes.sort(key=lambda x: x['date'])
                    
                    # Créer un DataFrame pour le graphique
                    df = pd.DataFrame({
                        'date': [note['date'] for note in plant_notes],
                        'height': [note['height'] for note in plant_notes]
                    })
                    
                    # Convertir les dates en datetime
                    df['date'] = pd.to_datetime(df['date'])
                    
                    # Créer le graphique avec Plotly
                    fig = px.line(df, x='date', y='height', markers=True,
                                  labels={'date': 'Date', 'height': 'Hauteur (cm)'},
                                  title="Évolution de la hauteur")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données de hauteur pour cette plante.")
            else:
                # Toutes les plantes avec données de hauteur
                plants_with_height = {}
                
                for note in filtered_notes:
                    if 'height' in note and note['height']:
                        plant = get_plant_by_id(plants, note['plantId'])
                        if not plant:
                            continue
                        
                        plant_name = plant['name']
                        
                        if plant_name not in plants_with_height:
                            plants_with_height[plant_name] = {'dates': [], 'heights': []}
                        
                        plants_with_height[plant_name]['dates'].append(note['date'])
                        plants_with_height[plant_name]['heights'].append(note['height'])
                
                if plants_with_height:
                    fig = go.Figure()
                    
                    for plant_name, data in plants_with_height.items():
                        # Trier les données par date
                        sorted_data = sorted(zip(data['dates'], data['heights']), key=lambda x: x[0])
                        dates = [item[0] for item in sorted_data]
                        heights = [item[1] for item in sorted_data]
                        
                        fig.add_trace(go.Scatter(
                            x=dates,
                            y=heights,
                            mode='lines+markers',
                            name=plant_name
                        ))
                    
                    fig.update_layout(
                        title="Évolution de la hauteur par plante",
                        xaxis_title="Date",
                        yaxis_title="Hauteur (cm)"
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données de hauteur disponibles.")
        
        with col2:
            if selected_plant_id:
                st.subheader("Évolution de la plante")
                
                # Données pour la plante sélectionnée
                plant_notes = get_notes_for_plant(notes, selected_plant_id)
                
                if plant_notes and any(('height' in note or 'leaves' in note) for note in plant_notes):
                    # Trier par date
                    plant_notes.sort(key=lambda x: x['date'])
                    
                    # Préparer les données
                    dates = [note['date'] for note in plant_notes]
                    heights = [note.get('height', 0) for note in plant_notes]
                    leaves = [note.get('leaves', 0) for note in plant_notes]
                    
                    # Convertir les dates en format lisible
                    formatted_dates = [format_date(date) for date in dates]
                    
                    # Créer un DataFrame
                    df = pd.DataFrame({
                        'date': formatted_dates,
                        'height': heights,
                        'leaves': leaves
                    })
                    
                    # Créer le graphique avec Plotly
                    fig = px.bar(
                        df,
                        x='date',
                        y=['height', 'leaves'],
                        barmode='group',
                        labels={'date': 'Date', 'value': 'Valeur', 'variable': 'Mesure'},
                        title="Évolution de la hauteur et du nombre de feuilles"
                    )
                    
                    # Personnaliser les noms des séries
                    fig.update_layout(
                        legend=dict(
                            title="",
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        )
                    )
                    
                    # Renommer les séries
                    newnames = {'height': 'Hauteur (cm)', 'leaves': 'Nombre de feuilles'}
                    fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas assez de données pour cette plante.")
            else:
                st.subheader("Distribution par Type")
                
                # Compter les variétés de plantes
                varieties = {}
                for plant in plants:
                    variety = plant.get('variety', 'Non spécifiée')
                    if variety not in varieties:
                        varieties[variety] = 0
                    varieties[variety] += 1
                
                if varieties:
                    # Créer un DataFrame pour le graphique
                    df = pd.DataFrame({
                        'Variété': list(varieties.keys()),
                        'Nombre': list(varieties.values())
                    })
                    
                    # Créer le graphique
                    fig = px.pie(df, values='Nombre', names='Variété', title="Distribution des variétés")
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Pas de données de variété disponibles.")

# Mettre à jour les données automatiquement
save_data(st.session_state['plants'], st.session_state['notes'])
