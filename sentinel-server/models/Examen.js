const mongoose = require('mongoose');

// --- SOUS-MODÈLE POUR LES QUESTIONS ---
const questionSchema = new mongoose.Schema({
    type: { 
        type: String, 
        enum: ['QCM', 'REDACTION', 'CODE'], 
        required: true 
    },
    enonce: { type: String, required: true },
    options: [String], // Utilisé uniquement si type === 'QCM'
    points: { type: Number, default: 1 }
});

// --- MODÈLE PRINCIPAL POUR L'EXAMEN ---
const examenSchema = new mongoose.Schema({
    titre: { type: String, required: true },
    
    // NOUVEAU : Identifiant unique de la matière (ex: RSI301)
    codeMatiere: { type: String, required: true }, 
    
    // NOUVEAU : Référence vers l'ID du prof dans la collection 'User'
    enseignantId: { 
        type: mongoose.Schema.Types.ObjectId, 
        ref: 'User',
        required: false 
    },
    
    // Nom affiché du prof (optionnel, pour plus de rapidité d'affichage)
    enseignantNom: { type: String, default: "Professeur" },
    
    duree: { type: Number, required: true }, // Durée en minutes
    
    questions: [questionSchema], // Tableau de questions
    
    // Statuts étendus pour mieux gérer le cycle de vie de l'examen
    statut: { 
        type: String, 
        enum: ['Brouillon', 'Actif', 'Terminé', 'Archives'], 
        default: 'Brouillon' 
    },
    
    dateCreation: { type: Date, default: Date.now }
});

// Ajout d'un index pour accélérer la recherche par matière
examenSchema.index({ codeMatiere: 1, statut: 1 });

module.exports = mongoose.model('Examen', examenSchema);