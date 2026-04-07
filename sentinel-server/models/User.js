const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    matricule: { type: String, required: true, unique: true, uppercase: true },
    nom: { type: String, required: true },
    prenom: { type: String, required: true },
    mot_de_pass: { type: String, required: true },
    role: { type: String, enum: ['Admin', 'Enseignant', 'Etudiant'], default: 'Etudiant' },
    // Le verrou de sécurité : l'adresse MAC du poste assigné
    adresse_mac_autorisee: { type: String, lowercase: true }
});

module.exports = mongoose.model('User', userSchema);