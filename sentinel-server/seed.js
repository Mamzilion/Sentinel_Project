const mongoose = require('mongoose');
const User = require('./models/User'); // Vérifie que le chemin est correct
require('dotenv').config();

const seed = async () => {
    try {
        // Connexion
        await mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/sentinel_db');
        
        // Nettoyage (pour éviter les doublons pendant les tests)
        await User.deleteMany({});

        const users = [
            {
                matricule: "ADMIN01",
                nom: "MAMA",
                prenom: "Daniel",
                password: "admin123", // On pourra hacher plus tard
                role: "Admin",
                macAddress: null
            },
            {
                matricule: "21IUT001",
                nom: "ZRA",
                prenom: "Justin",
                password: "password123",
                role: "Etudiant",
                // METS ICI TA VRAIE ADRESSE MAC pour tester le verrouillage plus tard
                macAddress: null 
            }
        ];

        await User.insertMany(users);
        console.log("✅ Utilisateurs de test créés avec succès !");
        process.exit();
    } catch (err) {
        console.error("❌ Erreur de seeding :", err);
        process.exit(1);
    }
};

seed();