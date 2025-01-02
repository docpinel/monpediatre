from flask import Flask, render_template, jsonify, request
import json
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')
routes = Flask(__name__)



# Déterminer le chemin des fichiers JSON
app_path = os.path.dirname(os.path.abspath(__file__))
json_file_path = os.path.join(app_path, "data.json")

# Chargement des données initiales
data = {
    "enfants": [],
    "visites": {}
}
try:
    with open(json_file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    print("Fichier JSON non trouvé, initialisation avec données vides.")

def convert_dates(data_list):
    if isinstance(data_list, dict):
        for child_visits in data_list.values():
            for visit in child_visits:
                if "visit_date" in visit:
                    visit["visit_date"] = datetime.strptime(visit["visit_date"], "%Y-%m-%d").date()
    elif isinstance(data_list, list):
        for item in data_list:
            if "birth_date" in item:
                item["birth_date"] = datetime.strptime(item["birth_date"], "%Y-%m-%d").date()
    return data_list

def convert_to_string(data_list):
    if isinstance(data_list, dict):
        for child_visits in data_list.values():
            for visit in child_visits:
                if "visit_date" in visit:
                    visit["visit_date"] = visit["visit_date"].strftime("%Y-%m-%d")
    elif isinstance(data_list, list):
        for item in data_list:
            if "birth_date" in item:
                item["birth_date"] = item["birth_date"].strftime("%Y-%m-%d")
    return data_list

# Routes Flask
@app.route('/')
def splash():
    return render_template('splash.html')
    
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/api/enfants', methods=['GET'])
def get_enfants():
    return jsonify(data['enfants'])

@app.route('/api/ajouter_enfant', methods=['POST'])
def ajouter_enfant():
    enfant = request.json
    try:
        birth_date = datetime.strptime(enfant['birth_date'], "%d/%m/%Y").date()
        enfant['birth_date'] = birth_date.isoformat()
        data['enfants'].append(enfant)
        save_data()
        return jsonify({"status": "succès", "message": "Enfant ajouté avec succès"}), 201
    except ValueError:
        return jsonify({"status": "erreur", "message": "Format de date invalide"}), 400

@app.route('/api/supprimer_enfant/<nom>', methods=['DELETE'])
def supprimer_enfant(nom):
    global data
    data['enfants'] = [enfant for enfant in data['enfants'] if enfant["name"] != nom]
    if nom in data['visites']:
        del data['visites'][nom]
    save_data()
    return jsonify({"status": "succès", "message": f"L'enfant {nom} a été supprimé."}), 200

@app.route('/child_details')
def child_details():
    name = request.args.get('name')
    if name:
        # Chercher l'enfant par son nom dans la liste 'data'
        child = next((c for c in data['enfants'] if c['name'] == name), None)
        if child:
            # Convertir la date de naissance en objet date pour le calcul d'âge
            birth_date = datetime.strptime(child['birth_date'], "%Y-%m-%d").date()
            
            # Utiliser date.today() correctement
            today = date.today()
            age = relativedelta(today, birth_date)
            
            # Calculer l'âge en mois et années
            age_in_months = age.months + age.years * 12
            
            # Rechercher le prochain vaccin
            next_vaccine = get_next_vaccine(age_in_months)
            if next_vaccine:
                if next_vaccine["age"] > 24:
                    next_vaccine['display_age'] = f"{next_vaccine['age'] // 12} ans"
                else:
                    next_vaccine['display_age'] = f"{next_vaccine['age']} mois"
            
            return render_template('child_details.html', 
                                   name=name, 
                                   birth_date=child['birth_date'], 
                                   age=f"{age.years} ans et {age.months} mois", 
                                   next_vaccine=next_vaccine)
        else:
            return "Enfant non trouvé", 404
    else:
        return "Aucun nom d'enfant fourni", 400
    
@app.route('/api/ajouter_visite', methods=['POST'])
def ajouter_visite():
    visite = request.json
    selected_child_name = visite['child_name']
    if selected_child_name not in data['visites']:
        data['visites'][selected_child_name] = []
    
    try:
        visit_date = datetime.strptime(visite['visit_date'], "%d/%m/%Y").date()
        data['visites'][selected_child_name].append({
            "visit_date": visit_date.isoformat(),
            "note": visite['note']
        })
        save_data()
        return jsonify({"status": "succès", "message": "Visite ajoutée avec succès"}), 201
    except ValueError:
        return jsonify({"status": "erreur", "message": "Format de date invalide"}), 400


@app.route('/visites/<nom>')
def afficher_visites(nom):
    if nom in data['visites']:
        return render_template('visites.html', nom=nom, visites=data['visites'][nom])
    return "Aucune visite trouvée pour cet enfant", 404


@app.route('/api/diversification/<nom>', methods=['GET'])
def get_diversification(nom):
    enfant = next((e for e in data['enfants'] if e['name'] == nom), None)
    if enfant:
        birth_date = datetime.strptime(enfant['birth_date'], "%Y-%m-%d").date()
        age_in_months = relativedelta(date.today(), birth_date).months + relativedelta(date.today(), birth_date).years * 12
        return jsonify({"details": get_diversification_details(age_in_months)})
    return jsonify({"status": "erreur", "message": "Enfant non trouvé"}), 404

def get_diversification_details(age_in_months):
    if age_in_months < 4:
        return "L'alimentation est exclusivement lactée."
    elif 4 <= age_in_months < 6:
        return """- Matin : Apport lacté
- Midi : Purée de légumes et pomme de terre (pomme de terre + carotte ou courgette ou blanc de poireau ou haricots verts ou potiron ou artichaut ou épinard)
- Goûter : Apport lacté  
- Soir : Apport lacté

Introduction :
- Lait maternel ou Biberon PPN
- Des légumes, Des protéines animales, Des fruits, Du gluten
- Quantité de lait par jour:
 à 5 mois : 850 mL (4 biberons d'environ 220 mL)
 Quantité de protéines:
 5 mois : 5 g ou 1 cuillère à café
"""

    elif 6 <= age_in_months < 9:
        return """- Matin : Apport lacté
- Midi : Repas mixé (purée de légumes et pomme de terre maison ou petit pot de légumes environ 130 g + viande 10 g/jour (2 c à c) à 6 mois, 15 g (3 c à c) à 7 mois, 20 g (4 c à c) à 8 mois ou petit pot de légumes avec viande 130 g + 1 cuillère d'huile)
- Goûter : Apport lacté + fruit 
- Soir : Apport lacté
Quantité de lait par jour:
- 8 mois : 650 mL (3 biberons de 220 mL ou 1 biberon de 250 mL + 1 laitage)
Quantité de protéines:
- 8 mois : 20 g ou 4 cuillères à café ou 1/3 d'œuf
"""

    elif 9 <= age_in_months <= 12:
        return """- Matin : Apport lacté
- Midi : Repas mixé à la cuillère (purée de légumes maison ou petit pot de légumes 180 g à 200 g avec une noix de beurre ou 1 cuillère à soupe d'huile, poisson ou œuf dur : 20 g/jour (4 cuillères à café) ou petit pot de légumes avec viande 200-250 g et une cuillère à soupe d'huile)
- Goûter : Apport lacté + fruit
- Soir : Introduction du repas du soir (purée de légumes maison ou soupe épaisse avec petites pâtes ou petit pot de légumes environ 180 g avec une noix de beurre ou 1 cuillère à soupe d'huile)
Quantité de lait par jour:
- 12 mois : 500 mL (2 biberons de 250 mL ou 1 biberon de 250 mL + 2 laitages)
Quantité de protéines:
- 12 mois : 30 g ou 1/3 de steak haché ou 1/2 œuf
"""
    elif 12 < age_in_months <= 36:
        return """- Matin : Apport lacté
- Midi : Repas haché en morceaux (légumes + féculents avec une noisette de beurre ou 1 cuillère à soupe d'huile à varier (noix, colza, olive), viande, poisson (30 g/jour, soit 6 c à c) ou 1/2 œuf)
- Goûter : Apport lacté + fruit
- Soir : Repas à la cuillère (légumes + féculents avec une noisette de beurre ou 1 cuillère à soupe d'huile à varier (noix, colza, olive) + 1 fruit ou compote)

Quantité de lait par jour:
- 12 mois : 500 mL (2 biberons de 250 mL ou 1 biberon de 250 mL + 2 laitages)
- 3 ans : 500 mL (idem)

Quantité de protéines:
- 12 mois : 30 g ou 1/3 de steak haché ou 1/2 œuf
- 3 ans : 50 g ou 1 œuf"""
    elif age_in_months > 36:
        return "Plat familial."
    else:
        return "Âge non valide pour la diversification alimentaire."

@app.route('/vaccine_schedule')
def vaccine_schedule():
    return render_template('vaccine_schedule.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/api/prochain_vaccin/<nom>', methods=['GET'])
def get_prochain_vaccin(nom):
    enfant = next((e for e in data['enfants'] if e['name'] == nom), None)
    if enfant:
        birth_date = datetime.strptime(enfant['birth_date'], "%Y-%m-%d").date()
        age_in_months = relativedelta(date.today(), birth_date).months + relativedelta(date.today(), birth_date).years * 12
        next_vaccine = get_next_vaccine(age_in_months)
        if next_vaccine:
            if next_vaccine["age"] > 24:
                age_display = f"{next_vaccine['age'] // 12} ans"
            else:
                age_display = f"{next_vaccine['age']} mois"
            return jsonify({"vaccin": f"{next_vaccine['vaccine']} à {age_display}"})
        return jsonify({"message": "Aucun vaccin supplémentaire n'est requis selon le calendrier actuel."})
    return jsonify({"status": "erreur", "message": "Enfant non trouvé"}), 404

def get_next_vaccine(age_in_months):
    vaccine_schedule = [
        {"age": 0, "vaccine": "BCG, Vaccin de l'hépatite B"},
        {"age": 2, "vaccine": "Pentavalent + Vaccin polio injectable + vaccin anti-pneumococcique"},
        {"age": 3, "vaccine": "Pentavalent deuxième dose + Vaccin polio injectable"},
        {"age": 4, "vaccine": "Vaccin anti-pneumococcique deuxième dose"},
        {"age": 6, "vaccine": "Pentavalent troisième dose + Vaccin polio injectable"},
        {"age": 11, "vaccine": "Vaccin anti-pneumococcique troisième dose"},
        {"age": 12, "vaccine": "Vaccin contre la rougeole et la rubéole + Vaccin contre l'hépatite A"},
        {"age": 18, "vaccine": "Vaccin contre la diphtérie, le tétanos et la coqueluche + Vaccin polio oral + Vaccin contre la rougeole et la rubéole"},
        {"age": 72, "vaccine": "Vaccin polio oral + Vaccin contre l'hépatite A"},
        {"age": 84, "vaccine": "Vaccin contre la diphtérie et le tétanos"},
        {"age": 144, "vaccine": "Vaccin contre la diphtérie et le tétanos + Vaccin Polio oral"},
        {"age": 216, "vaccine": "Vaccin contre la diphtérie et le tétanos + Vaccin Polio oral"}
    ]
    
    for vaccine in vaccine_schedule:
        if age_in_months < vaccine['age']:
            return vaccine
    return None

def save_data():
    with open(json_file_path, "w", encoding="utf-8") as f:
        json.dump(convert_to_string(data), f, indent=4)

if __name__ == "__main__":
    app.run(debug=True)

