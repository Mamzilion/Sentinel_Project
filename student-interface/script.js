document.getElementById('loginForm').addEventListener('submit', function(e) {
    e.preventDefault(); // Empêche le rechargement de la page

    const matricule = document.getElementById('matricule').value;
    const password = document.getElementById('password').value;

    console.log("Tentative de connexion pour :", matricule);
    
    // Ici, on ajoutera plus tard l'appel à ton API : /api/exams/fetch/
    alert("Connexion en cours pour le matricule : " + matricule);
    
    // Simulation de redirection vers l'écran du sujet
    // window.location.href = "sujet.html";
});