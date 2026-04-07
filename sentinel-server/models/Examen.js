const mongoose = require('mongoose');

const questionSchema = new mongoose.Schema({
    enonce: { type: String, required: true },
    points: { type: Number, default: 1 },
    type: { type: String, enum: ['QCM', 'COURT', 'CODE'], default: 'COURT' },
    options: [String], // Uniquement pour les QCM
    reponse_correcte: { type: String } // Optionnel (pour l'auto-correction plus tard)
});

const examenSchema = new mongoose.Schema({
    titre: { type: String, required: true },
    code_matiere: { type: String, required: true, uppercase: true },
    enseignant_id: { type: mongoose.Schema.Types.ObjectId, ref: 'User' },
    duree_minutes: { type: Number, required: true, default: 60 },
    questions: [questionSchema], // Liste des questions imbriquées
    date_creation: { type: Date, default: Date.now },
    est_actif: { type: Boolean, default: false } // Pour lancer l'examen au bon moment
});

module.exports = mongoose.model('Examen', examenSchema);