import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
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
    plants = []
    notes = []
    
    try:
        if os.path.exists('garden_plants.json'):
            with open('garden_plants.json', 'r', encoding='utf-8') as f:
                plants = json.load(f)
        
        if os.path.exists('garden_notes.json'):
            with open('garden_notes.json', 'r', encoding='utf-8') as f:
                notes = json.load(f)
    except Exception as e:
        st.error(f"Erreur lors du chargement des données. Création d'un nouveau journal.")
        print(f"Erreur de chargement: {str(e)}")
    
    return plants, notes

def save_data(plants, notes):
    """Sauvegarder les données dans des fichiers JSON"""
    try:
        with open('garden_plants.json', 'w', encoding='utf-8') as f:
            json.dump(plants, f, ensure_ascii=False, indent=4)
        
        with open('garden_notes.json', 'w', encoding='utf-8') as f:
            json.dump(notes, f, ensure_ascii=False, indent=4)
        return True
    except PermissionError:
        st.error("Erreur de permission : l'application n'a pas les droits d'écriture nécessaires.")
        print("Erreur de permission lors de la sauvegarde des données")
        return False
    except Exception as e:
        st.error(f"Erreur lors de la sauvegarde des données: {str(e)}")
        print(f"Erreur lors de la sauvegarde des données: {str(e)}")
        return False

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
    """Gérer l'upload d'une image et la convertir en base64 avec redimensionnement"""
    if uploaded_file is not None:
        try:
            # Ouvrir l'image avec PIL
            img = Image.open(uploaded_file)
            
            # Redimensionner l'image pour réduire sa taille
            max_size = (800, 800)  # Taille maximale
            img.thumbnail(max_size, Image.LANCZOS)
            
            # Convertir en RGB si nécessaire (pour les images PNG avec transparence)
            if img.mode in ('RGBA', 'LA'):
                background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                background.paste(img, img.split()[-1])
                img = background
            
            # Sauvegarder dans un buffer avec une qualité réduite
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=85, optimize=True)
            buffer.seek(0)
            
            # Convertir en base64
            img_str = base64.b64encode(buffer.getvalue()).decode()
            return f"data:image/jpeg;base64,{img_str}"
        except Exception as e:
            st.warning(f"Problème lors du traitement de l'image. L'image ne sera pas enregistrée.")
            return None
    return None

def display_image(image_data):
    """Afficher une image depuis des données base64"""
    if image_data:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            # Pour les images en base64, extraire les données et le type
            content_type = image_data.split(';')[0].split(':')[1]
            image_bytes = base64.b64decode(image_data.split(',')[1])
            image = Image.open(io.BytesIO(image_bytes))
            st.image(image, use_container_width=True)
        else:
            st.image(image_data, use_column_width=True)

# Initialisation de l'état de session
if 'init' not in st.session_state:
    st.session_state['init'] = True
    plants, notes = load_data()
    st.session_state['plants'] = plants
    st.session_state['notes'] = notes
    # Pour gérer la navigation entre sections
    if 'nav_option' not in st.session_state:
        st.session_state['nav_option'] = "Tableau de bord"
else:
    plants = st.session_state['plants']
    notes = st.session_state['notes']

# Entête de la page avec style personnalisé
st.title("Journal de Bord du Jardin")
st.caption("Suivez toutes vos plantations et leur progression")
st.divider()

# Navigation principale
if 'nav_option' in st.session_state:
    nav_option = st.session_state['nav_option']
else:
    nav_option = st.sidebar.radio(
        "Navigation",
        ["Tableau de bord", "Mes Plantes", "Ajouter une Plante", "Notes", "Statistiques"]
    )
    st.session_state['nav_option'] = nav_option

# Boutons de navigation dans la sidebar (toujours visibles)
with st.sidebar:
    st.write("## Navigation")
    
    if st.button("Tableau de bord", use_container_width=True):
        st.session_state['nav_option'] = "Tableau de bord"
        st.rerun()
        
    if st.button("Mes Plantes", use_container_width=True):
        st.session_state['nav_option'] = "Mes Plantes"
        st.rerun()
        
    if st.button("Ajouter une Plante", use_container_width=True):
        st.session_state['nav_option'] = "Ajouter une Plante"
        st.rerun()
        
    if st.button("Notes", use_container_width=True):
        st.session_state['nav_option'] = "Notes"
        st.rerun()
        
    if st.button("Statistiques", use_container_width=True):
        st.session_state['nav_option'] = "Statistiques"
        st.rerun()

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
                with st.container():
                    # Créer un expander pour chaque plante
                    with st.expander(f"{plant['name']} ({plant.get('variety', 'Variété non spécifiée')})", expanded=True):
                        plant_notes = get_notes_for_plant(notes, plant['id'])
                        last_note = None
                        
                        if plant_notes:
                            last_note = sorted(plant_notes, key=lambda x: x['date'], reverse=True)[0]
                        
                        # Afficher l'image de la plante ou de la dernière note
                        if 'image' in plant and plant['image']:
                            display_image(plant['image'])
                        elif last_note and 'image' in last_note and last_note['image']:
                            display_image(last_note['image'])
                        
                        # Informations principales
                        st.write(f"**Date de plantation:** {format_date(plant['date'])}")
                        st.write(f"**Contenant:** {get_container_name(plant['container'])}")
                        st.write(f"**Terreau:** {plant.get('soil', 'Non spécifié')}")
                        
                        # Statistiques de la plante
                        if last_note:
                            st.write("---")
                            stats_cols = st.columns(3)
                            if 'height' in last_note and last_note['height']:
                                stats_cols[0].metric("Hauteur", f"{last_note['height']} cm")
                            if 'leaves' in last_note and last_note['leaves']:
                                stats_cols[1].metric("Feuilles", last_note['leaves'])
                            stats_cols[2].metric("Âge", f"{days_from_planting(plant['date'])} jours")
    
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
            
            with st.container():
                st.caption(f"{format_date(note['date'])} - {plant['name']}")
                st.write(note['content'])
                
                if 'image' in note and note['image']:
                    display_image(note['image'])
                
                # Afficher les métriques
                if 'height' in note and note['height'] or 'leaves' in note and note['leaves']:
                    cols = st.columns([1, 1, 3])
                    if 'height' in note and note['height']:
                        cols[0].metric("Hauteur", f"{note['height']} cm")
                    if 'leaves' in note and note['leaves']:
                        cols[1].metric("Feuilles", note['leaves'])
                
                st.divider()

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
                        with st.container():
                            # En-tête avec fond coloré
                            st.subheader(f"{plant['name']} ({plant.get('variety', 'Variété non spécifiée')})")
                            
                            plant_notes = get_notes_for_plant(notes, plant['id'])
                            last_note = None
                            
                            if plant_notes:
                                last_note = sorted(plant_notes, key=lambda x: x['date'], reverse=True)[0]
                            
                            # Afficher l'image
                            if 'image' in plant and plant['image']:
                                display_image(plant['image'])
                            elif last_note and 'image' in last_note and last_note['image']:
                                display_image(last_note['image'])
                            
                            # Informations de la plante
                            st.write(f"**Date de plantation:** {format_date(plant['date'])}")
                            st.write(f"**Contenant:** {get_container_name(plant['container'])}")
                            st.write(f"**Terreau:** {plant.get('soil', 'Non spécifié')}")
                            st.write(f"**Emplacement:** {plant.get('location', 'Non spécifié')}")
                            
                            if plant.get('notes'):
                                st.write(f"**Notes:** {plant['notes']}")
                            
                            # Statistiques
                            if last_note:
                                st.write("---")
                                stat_cols = st.columns(3)
                                if 'height' in last_note and last_note['height']:
                                    stat_cols[0].metric("Hauteur", f"{last_note['height']} cm")
                                if 'leaves' in last_note and last_note['leaves']:
                                    stat_cols[1].metric("Feuilles", last_note['leaves'])
                                stat_cols[2].metric("Âge", f"{days_from_planting(plant['date'])} jours")
                            
                            # Boutons d'action
                            action_cols = st.columns(2)
                            
                            # Bouton pour ajouter une note
                            if action_cols[0].button(f"Ajouter une note", key=f"add_note_{plant['id']}"):
                                st.session_state['selected_plant_id'] = plant['id']
                                st.session_state['nav_option'] = "Notes"
                                st.rerun()
                            
                            # Bouton pour supprimer la plante
                            if action_cols[1].button(f"Supprimer", key=f"delete_{plant['id']}"):
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
                                    st.rerun()
                            
                            st.divider()

# Section Ajouter une Plante
elif nav_option == "Ajouter une Plante":
    st.header("Ajouter une Nouvelle Plante")
    
    with st.form("plant_form"):
        # Champs du formulaire
        name = st.text_input("Nom de la Plante *")
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
            # Validation manuelle des champs requis
            if not name:
                st.error("Le nom de la plante est obligatoire.")
            else:
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
            content = st.text_area("Observation *")
            
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
                # Validation manuelle des champs requis
                if not content:
                    st.error("L'observation est obligatoire.")
                else:
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
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.caption(f"{format_date(note['date'])} - {plant['name']}")
                    st.write(note['content'])
                    
                    if 'image' in note and note['image']:
                        display_image(note['image'])
                    
                    # Afficher les métriques
                    if 'height' in note and note['height'] or 'leaves' in note and note['leaves']:
                        metric_cols = st.columns([1, 1, 3])
                        if 'height' in note and note['height']:
                            metric_cols[0].metric("Hauteur", f"{note['height']} cm")
                        if 'leaves' in note and note['leaves']:
                            metric_cols[1].metric("Feuilles", note['leaves'])
                
                with col2:
                    # Bouton pour supprimer la note
                    if st.button("Supprimer", key=f"delete_note_{note['id']}"):
                        st.session_state['notes'] = [n for n in notes if n['id'] != note['id']]
                        save_data(st.session_state['plants'], st.session_state['notes'])
                        st.success("Note supprimée !")
                        st.rerun()
                
                st.divider()

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

# Mettre à jour les données automatiquement (à la fin du script)
try:
    if 'plants' in st.session_state and 'notes' in st.session_state:
        save_result = save_data(st.session_state['plants'], st.session_state['notes'])
        if not save_result:
            st.sidebar.warning("⚠️ Problème lors de la sauvegarde automatique des données")
except Exception as e:
    st.sidebar.error("Erreur de sauvegarde")
