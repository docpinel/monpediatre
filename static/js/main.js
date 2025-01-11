document.addEventListener('DOMContentLoaded', function() {
    // Fonction pour afficher la diversification alimentaire
    function showDiversification() {
        var datePicker = document.getElementById('birthDatePicker');
        var birthDate = datePicker.value;
        if (birthDate) {
            window.location.href = '/diversification_alimentaire?birth_date=' + encodeURIComponent(birthDate);
        } else {
            alert("Veuillez sélectionner une date de naissance valide.");
        }
    }

    // Fonction pour afficher le calendrier vaccinal
    function showVaccineSchedule() {
        window.location.href = "/calendrier_vaccinal";
    }

    // Fonction pour montrer le prochain vaccin
    function showNextVaccine() {
        var datePicker = document.getElementById('birthDatePicker');
        var birthDate = datePicker.value;
        if (birthDate) {
            window.location.href = '/prochain_vaccin?birth_date=' + encodeURIComponent(birthDate);
        } else {
            alert("Veuillez sélectionner une date de naissance valide.");
        }
    }

    // Fonction pour afficher les informations "À propos"
    function showAbout() {
        window.location.href = "/a_propos";
    }

    // Fonction pour ouvrir le blog
    function openBlog() {
        window.open('https://unpediatre.wordpress.com/', '_blank');
    }

    // Attacher les fonctions aux boutons existants
    document.getElementById('diversificationBtn').addEventListener('click', showDiversification);
    document.getElementById('vaccineScheduleBtn').addEventListener('click', showVaccineSchedule);
    document.getElementById('nextVaccineBtn').addEventListener('click', showNextVaccine);
    document.getElementById('aboutBtn').addEventListener('click', showAbout);
    document.getElementById('blogButton').addEventListener('click', openBlog);
});