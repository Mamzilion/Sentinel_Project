const mongoose = require('mongoose');

const CopieSchema = new mongoose.Schema({
    matricule: { type: String, required: true },
    examenId: { type: mongoose.Schema.Types.ObjectId, ref: 'Examen', required: true },
    
    // Champs ajoutés pour le Dashboard Enseignant
    nom: { type: String },    
    prenom: { type: String }, 
    
    // Contenu de la copie
    responses: { type: Object, required: true }, // Stocke le dictionnaire {q_id: valeur}
    macAddress: { type: String },
    
    // --- NOUVEAU : SYSTÈME DE SURVEILLANCE ---
    evidences: [{
        type: { type: String }, // ex: "PERTE_FOCUS", "IDENTIFICATION", "OBJET_INTERDIT"
        timestamp: { type: Date, default: Date.now },
        imagePath: { type: String } // Chemin du fichier sur le serveur (uploads/...)
    }],
    
    dateSoumission: { type: Date, default: Date.now }
});

// SÉCURITÉ : Empêche un étudiant de soumettre deux fois le même examen
CopieSchema.index({ matricule: 1, examenId: 1 }, { unique: true });

module.exports = mongoose.model('Copie', CopieSchema);