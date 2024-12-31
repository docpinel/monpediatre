document.addEventListener('DOMContentLoaded', function() {
    // Charge la liste des enfants au chargement de la page
    fetchChildren();

    // Fonction pour ajouter un enfant
    function addChild() {
        const childName = prompt("Nom de l'enfant :");
        const birthDate = prompt("Date de naissance (jj/mm/aaaa) :");
        
        if (childName && birthDate) {
            fetch('/api/ajouter_enfant', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    name: childName,
                    birth_date: birthDate
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "succès") {
                    alert(data.message);
                    fetchChildren();
                } else {
                    alert("Erreur : " + data.message);
                }
            })
            .catch(error => console.error('Erreur:', error));
        } else {
            alert("Veuillez entrer un nom et une date de naissance.");
        }
    }

    // Fonction pour charger la liste des enfants
    function fetchChildren() {
        fetch('/api/enfants')
            .then(response => response.json())
            .then(children => {
                const list = document.getElementById('children');
                list.innerHTML = ''; // Effacer la liste existante
                children.forEach(child => {
                    let li = document.createElement('li');
                    li.textContent = child.name;
                    li.addEventListener('click', () => showChildDetails(child.name));
                    list.appendChild(li);
                });
            });
    }

    // Fonction pour afficher les détails d'un enfant
    function showChildDetails() {
        const name = prompt("Entrez le nom de l'enfant pour voir les détails :");
        if (name) {
            window.location.href = `/child_details?name=${encodeURIComponent(name)}`;
        } else {
            alert("Veuillez entrer un nom valide.");
        }
    }

    // Fonction pour afficher la diversification alimentaire
    function showDiversification() {
        const name = prompt("Nom de l'enfant pour la diversification :");
        if (name) {
            fetch(`/api/diversification/${encodeURIComponent(name)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.details) {
                        alert(`Diversification alimentaire pour ${name}:\n${data.details}`);
                    } else {
                        alert("Aucune information trouvée ou enfant non trouvé.");
                    }
                })
                .catch(error => console.error('Erreur:', error));
        }
    }

    // Fonction pour ajouter une visite
    function addVisit() {
        const name = prompt("Nom de l'enfant pour ajouter une visite :");
        if (name) {
            const date = prompt("Date de la visite (jj/mm/aaaa) :");
            const note = prompt("Note de la visite :");
            if (date && note) {
                fetch('/api/ajouter_visite', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        child_name: name,
                        visit_date: date,
                        note: note
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === "succès") {
                        alert(data.message);
                    } else {
                        alert("Erreur : " + data.message);
                    }
                })
                .catch(error => console.error('Erreur:', error));
            } else {
                alert("Veuillez entrer une date et une note.");
            }
        }
    }

    // Fonction pour afficher les visites d'un enfant
    function showVisits() {
        const name = prompt("Nom de l'enfant pour voir les visites :");
        if (name) {
            window.location.href = `/visites/${encodeURIComponent(name)}`;
        }
    }
    
    // Fonction pour montrer le calendrier vaccinal
    function showVaccine() {
        window.location.href = "/vaccine_schedule"; // Redirection vers la page du calendrier vaccinal
    }

    // Fonction pour montrer le prochain vaccin
    function showNextVaccine() {
        const name = prompt("Nom de l'enfant pour voir le prochain vaccin :");
        if (name) {
            fetch(`/api/prochain_vaccin/${encodeURIComponent(name)}`)
                .then(response => response.json())
                .then(data => {
                    if (data.vaccin) {
                        alert(`Prochain vaccin pour ${name}: ${data.vaccin}`);
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => console.error('Erreur:', error));
        }
    }

    function deleteChild() {
        const name = prompt("Nom de l'enfant à supprimer :");
        if (name) {
            fetch(`/api/supprimer_enfant/${encodeURIComponent(name)}`, {
                method: 'DELETE'
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "succès") {
                    alert(data.message);
                    fetchChildren(); // Rafraîchir la liste des enfants après suppression
                } else {
                    alert("Erreur : " + data.message);
                }
            })
            .catch(error => console.error('Erreur:', error));
        }
    }
    

    // Fonction pour afficher les informations "À propos"
    function showAbout() {
        window.location.href = "/about";
    }

    // Attacher les fonctions aux boutons
    document.querySelector('button[onclick="addChild()"]').addEventListener('click', addChild);
    document.querySelector('button[onclick="showChildDetails()"]').addEventListener('click', showChildDetails);
    document.querySelector('button[onclick="showDiversification()"]').addEventListener('click', showDiversification);
    document.querySelector('button[onclick="addVisit()"]').addEventListener('click', addVisit);
    document.querySelector('button[onclick="showVisits()"]').addEventListener('click', showVisits);
    document.querySelector('button[onclick="showVaccine()"]').addEventListener('click', showVaccine);
    document.querySelector('button[onclick="showNextVaccine()"]').addEventListener('click', showNextVaccine);
    document.querySelector('button[onclick="deleteChild()"]').addEventListener('click', deleteChild);
    document.querySelector('button[onclick="showAbout()"]').addEventListener('click', showAbout);
    
});