from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os
import json
from functools import wraps

app = Flask(__name__, static_url_path='/static', static_folder='static')
app.secret_key = '12345'  # Note: Utilisez une clé secrète plus sécurisée en production.

# Fonction d'aide pour lire et écrire dans le fichier JSON
def load_data():
    try:
        with open('data.json', 'r') as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"users": {}, "children": {}}

def save_data(data):
    with open('data.json', 'w') as file:
        json.dump(data, file, indent=4)

# Fonction pour vérifier si l'utilisateur est connecté
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Routes Flask

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        data = load_data()
        if username in data['users'] and check_password_hash(data['users'][username]['password'], password):
            session['user'] = username
            return redirect(url_for('index'))
        return "Nom d'utilisateur ou mot de passe incorrect.", 401
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)
        data = load_data()
        if username not in data['users']:
            data['users'][username] = {'password': hashed_password, 'children': []}
            save_data(data)
            return redirect(url_for('login'))
        return "Ce nom d'utilisateur existe déjà.", 400
    return render_template('register.html')

@app.route('/')
def splash():
    if 'user' in session:
        return redirect(url_for('index'))
    return redirect(url_for('login'))

# Suppression de la logique de gestion des enfants ici, car elle doit être dans une route ou une fonction de vue
@app.route('/language_selection')
def language_selection():
    if 'user' in session:
        return redirect(url_for('index'))
    return render_template('language_selection.html')

@app.route('/arabe')
def arabe():
    return render_template('arabe.html')

@app.route('/francais')
def francais():
    return redirect(url_for('index'))


@app.route('/index')
@login_required
def index():
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    return render_template('index.html', user_children=user_children)



@app.route('/enter_birth_date', methods=['GET', 'POST'])
@login_required
def enter_birth_date():
    if request.method == 'POST':
        birth_date_str = request.form.get('birth_date')
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            return redirect(url_for('child_details', birth_date=birth_date_str))
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    return render_template('enter_birth_date.html')

@app.route('/add_child', methods=['GET', 'POST'])
@login_required
def add_child():
    if request.method == 'POST':
        initials = request.form.get('child_initials')
        birth_date_str = request.form.get('birth_date')
        if initials and birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
                data = load_data()
                user_children = data['users'][session['user']]['children']
                user_children.append({'initials': initials, 'birth_date': birth_date_str})
                save_data(data)
                return redirect(url_for('children_list'))
            except ValueError:
                return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    return render_template('add_child.html')
@app.route('/delete_child/<initials>', methods=['GET', 'POST'])
@login_required
def delete_child(initials):
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    
    # Chercher l'enfant parmi les enfants de l'utilisateur
    child_to_delete = next((child for child in user_children if child['initials'] == initials), None)
    
    if not child_to_delete:
        return "Enfant non trouvé pour ces initiales.", 404

    if request.method == 'POST':
        # Supprimer l'enfant de la liste des enfants
        user_children.remove(child_to_delete)
        
        # Sauvegarder les données mises à jour
        data['users'][session['user']]['children'] = user_children
        save_data(data)
        return redirect(url_for('children_list'))  # Redirige vers la liste des enfants après suppression
    else:  # Méthode GET
        return render_template('delete_child.html', initials=initials)
@app.route('/children_list')
@login_required
def children_list():
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    return render_template('children_list.html', children=user_children)

@app.route('/manage_children', methods=['GET', 'POST'])
@login_required
def manage_children():
    if request.method == 'POST':
        initials = request.form.get('initials')
        data = load_data()
        user_children = data['users'].get(session['user'], {}).get('children', [])
        user_children.append({'initials': initials})
        save_data(data)
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    return render_template('manage_children.html', children=user_children)

@app.route('/child_details')
@login_required
def child_details():
    birth_date_str = request.args.get('birth_date')
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            age_display = calculate_age(birth_date)
            age_in_months = get_age_in_months(birth_date)
            
            next_vaccine = get_next_vaccine(age_in_months)
            diversification_info = get_diversification_details(age_in_months)
            
            data = load_data()
            user_children = data['users'].get(session['user'], {}).get('children', [])
            
            return render_template('child_details.html', 
                                   birth_date=birth_date_str, 
                                   age=age_display, 
                                   next_vaccine=next_vaccine,
                                   diversification_info=diversification_info,
                                   children=user_children)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return "Aucune date de naissance fournie", 400

# Aide fonctions pour l'âge, vaccination, et diversification restent les mêmes, mais assurez-vous qu'elles sont définies correctement
def calculate_age(birth_date):
    today = date.today()
    age = relativedelta(today, birth_date)
    
    if age.years < 0:
        return "0 ans, 0 mois et 0 jours"
    
    years = age.years
    months = age.months
    days = age.days
    return f"{years} ans, {months} mois et {days} jours"

def get_age_in_months(birth_date):
    today = date.today()
    age = relativedelta(today, birth_date)
    return age.months + age.years * 12

# Assurez-vous que ces fonctions existent et sont correctement définies:
# get_next_vaccine(age_in_months)
# get_diversification_details(age_in_months)

@app.route('/diversification_alimentaire/<initials>', methods=['GET'])
@login_required
def diversification_alimentaire(initials):
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    # Recherche insensible à la casse
    child = next((c for c in user_children if c['initials'].lower() == initials.lower()), None)
    
    if not child:
        return "Enfant non trouvé pour ces initiales.", 404
    
    # Utiliser la date de naissance de l'enfant si elle n'est pas fournie dans les paramètres
    birth_date_str = request.args.get('birth_date', child['birth_date'])  # Si birth_date n'est pas dans les params, utilisez celle de l'enfant
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            age_display = calculate_age(birth_date)
            age_in_months = get_age_in_months(birth_date)
            
            diversification_info = get_diversification_details(age_in_months)
            
            return render_template('diversification.html', 
                                   birth_date=birth_date_str, 
                                   age=age_display, 
                                   diversification_info=diversification_info,
                                   initials=initials)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return "Aucune date de naissance trouvée pour cet enfant.", 400
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

@app.route('/calendrier_vaccinal')
def vaccine_schedule():
    return render_template('vaccine_schedule.html')
@app.route('/mon_blog')
def mon_blog():
    return redirect('https://unpediatre.wordpress.com/')

@app.route('/a_propos')
def about():
    return render_template('about.html')

@app.route('/prochain_vaccin/<initials>', methods=['GET'])
@login_required
def get_prochain_vaccin(initials):
    data = load_data()
    user_children = data['users'].get(session['user'], {}).get('children', [])
    # Recherche insensible à la casse
    child = next((c for c in user_children if c['initials'].lower() == initials.lower()), None)
    if not child:
        return "Enfant non trouvé pour ces initiales.", 404
    
    # Utiliser la date de naissance de l'enfant si elle n'est pas fournie dans les paramètres
    birth_date_str = request.args.get('birth_date', child['birth_date'])
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            age_display = calculate_age(birth_date)
            age_in_months = get_age_in_months(birth_date)
            
            vaccine_history, next_vaccine = get_vaccine_history_and_next(age_in_months)
            
            return render_template('prochain_vaccin.html', 
                                   birth_date=birth_date_str, 
                                   age=age_display,
                                   vaccine_history=vaccine_history,
                                   next_vaccine=next_vaccine,
                                   initials=initials)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return "Aucune date de naissance trouvée pour cet enfant.", 400
    
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


def get_vaccine_history_and_next(age_in_months):
    vaccine_schedule = [
        {"age": 0, "vaccine": "BCG, Vaccin de l'hépatite B"},
        {"age": 2, "vaccine": "Pentavalent + Vaccin polio injectable + vaccin anti-pneumococcique"},
        {"age": 3, "vaccine": "Pentavalent deuxième dose + Vaccin polio injectable"},
        {"age": 4, "vaccine": "Vaccin anti-pneumococcique deuxième dose"},
        {"age": 6, "vaccine": "Pentavalent troisième dose + Vaccin polio injectable"},
        {"age": 11, "vaccine": "Vaccin anti-pneumococcique troisième dose"},
        {"age": 12, "vaccine": "Vaccin contre la rougeole et la rubéole + Vaccin contre l'hépatite A"},
        {"age": 18, "vaccine": "Vaccin contre la diphtérie, le tétanos et la coqueluche + Vaccin polio oral + Vaccin contre la rougeole et la rubéole"},
        {"age": 72, "vaccine": "Vaccin contre la diphtérie, le tétanos, la coqueluche et la poliomyélite + Vaccin contre l'hépatite A"},
        {"age": 144, "vaccine": "Vaccin contre la diphtérie et le tétanos + Vaccin Polio oral"},
        {"age": 216, "vaccine": "Vaccin contre la diphtérie et le tétanos + Vaccin Polio oral"}
    ]
    
    history = []
    next_vaccine = None
    
    for vaccine in vaccine_schedule:
        if age_in_months >= vaccine['age']:
            history.append({"name": vaccine['vaccine'], "age": vaccine['age']})
        else:
            next_vaccine = {"name": vaccine['vaccine'], "age": vaccine['age']}
            break
    
    for item in history:
        if item['age'] > 24:
            item['display_age'] = f"{item['age'] // 12} ans"
        else:
            item['display_age'] = f"{item['age']} mois"
    
    if next_vaccine:
        if next_vaccine['age'] > 24:
            next_vaccine['display_age'] = f"{next_vaccine['age'] // 12} ans"
        else:
            next_vaccine['display_age'] = f"{next_vaccine['age']} mois"
    
    return history, next_vaccine

# La fonction save_data est toujours nécessaire pour sauvegarder les modifications dans le fichier JSON

if __name__ == "__main__":
    app.run(debug=True)