const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
    matricule: { 
        type: String, 
        required: true, 
        unique: true, 
        uppercase: true,
        trim: true 
    },
    nom: { 
        type: String, 
        required: true,
        trim: true
    },
    prenom: { 
        type: String, 
        required: true,
        trim: true
    },
    password: { 
        type: String, 
        required: true 
    },
    role: { 
        type: String, 
        enum: ['Admin', 'Enseignant', 'Etudiant'], 
        default: 'Etudiant' 
    },
    // Stocke la MAC du ProBook lors de la première connexion à l'examen
    macAddress: { 
        type: String, 
        lowercase: true, 
        default: null 
    },
    // Force l'étudiant à changer son mot de passe IUT2026 dès l'entrée
    isFirstLogin: { 
        type: Boolean, 
        default: true 
    }
}, { timestamps: true });

module.exports = mongoose.model('User', userSchema);