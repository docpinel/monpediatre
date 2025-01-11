from flask import Flask, render_template, jsonify, request, redirect, url_for
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import os

app = Flask(__name__, static_url_path='/static', static_folder='static')

# Les données ne seront plus stockées, donc nous supprimons la partie liée au fichier JSON

# Routes Flask
@app.route('/')
def splash():
    return render_template('splash.html')

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/mon_blog')
def mon_blog():
    return redirect('https://unpediatre.wordpress.com/')

@app.route('/enter_birth_date', methods=['GET', 'POST'])
def enter_birth_date():
    if request.method == 'POST':
        birth_date_str = request.form.get('birth_date')
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            # Redirection vers la page de détails avec la date de naissance
            return redirect(url_for('child_details', birth_date=birth_date_str))
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    return render_template('enter_birth_date.html')

@app.route('/child_details')
def calculate_age(birth_date):
    today = date.today()
    age = relativedelta(today, birth_date)
    
    # Si la date de naissance est dans le futur, on ajuste à 0
    if age.years < 0:
        return "0 ans, 0 mois et 0 jours"
    
    # Calcul de l'âge en ans, mois et jours
    years = age.years
    months = age.months
    days = age.days
    
    # Formatage de l'affichage
    return f"{years} ans, {months} mois et {days} jours"
def get_age_in_months(birth_date):
    today = date.today()
    age = relativedelta(today, birth_date)
    return age.months + age.years * 12

def child_details():
    birth_date_str = request.args.get('birth_date')
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            age_display = calculate_age(birth_date)
            age_in_months = get_age_in_months(birth_date)
            
            next_vaccine = get_next_vaccine(age_in_months)
            diversification_info = get_diversification_details(age_in_months)
            
            return render_template('child_details.html', 
                                   birth_date=birth_date_str, 
                                   age=age_display, 
                                   next_vaccine=next_vaccine,
                                   diversification_info=diversification_info)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return "Aucune date de naissance fournie", 400




@app.route('/diversification_alimentaire')
def diversification_alimentaire():
    birth_date_str = request.args.get('birth_date')
    if birth_date_str:
        try:
            birth_date = datetime.strptime(birth_date_str, "%d/%m/%Y").date()
            age_display = calculate_age(birth_date)
            age_in_months = get_age_in_months(birth_date)
            
            diversification_info = get_diversification_details(age_in_months)
            
            return render_template('diversification.html', 
                                   birth_date=birth_date_str, 
                                   age=age_display, 
                                   diversification_info=diversification_info)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return "Aucune date de naissance fournie", 400
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

@app.route('/a_propos')
def about():
    return render_template('about.html')

@app.route('/prochain_vaccin')
def get_prochain_vaccin():
    birth_date_str = request.args.get('birth_date')
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
                                   next_vaccine=next_vaccine)
        except ValueError:
            return "Format de date invalide. Utilisez jj/mm/aaaa.", 400
    else:
        return render_template('prochain_vaccin.html', 
                               birth_date=None, 
                               age=None,
                               vaccine_history=None,
                               next_vaccine=None)

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
    
    # Formatage de l'âge pour l'affichage
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

# La fonction save_data n'est plus nécessaire car nous ne stockons plus les données des utilisateurs

if __name__ == "__main__":
    app.run(debug=True)