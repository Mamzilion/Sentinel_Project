const express = require('express');
const router = express.Router();
const authController = require('../controllers/authController');
const User = require('../models/User'); // Assure-toi que le chemin vers ton modèle est correct

// --- AUTHENTIFICATION ---
// Utilisé par le dashboard prof et l'agent Python sur les ProBook
router.post('/login', authController.login);

// Sécurité : Pour forcer l'étudiant à changer son mdp par défaut
router.post('/change-password', authController.changePassword);

// --- GESTION DES ÉTUDIANTS (ADMIN / PROF) ---

/**
 * @route   POST /api/auth/import-students
 * @desc    Importation massive d'étudiants via le dashboard prof (CSV)
 */
router.post('/import-students', async (req, res) => {
    try {
        const { students } = req.body;
        
        if (!students || students.length === 0) {
            return res.status(400).json({ message: "La liste des étudiants est vide." });
        }

        // Préparation des objets pour MongoDB
        const usersToInsert = students.map(s => ({
            username: s.matricule, // Le matricule sert d'identifiant unique
            password: "InitialPassword123", // Mot de passe par défaut à changer
            nom: s.nom,
            email: s.email,
            role: 'Etudiant',
            macAddress: null // Verrouillage MAC lors de la première connexion
        }));

        // Bulk Insert : Très efficace pour 300+ étudiants
        await User.insertMany(usersToInsert, { ordered: false }); 
        // { ordered: false } permet de continuer l'insertion même si un doublon échoue

        console.log(`📊 Importation SENTINEL : ${usersToInsert.length} étudiants ajoutés.`);
        res.status(201).json({ 
            message: "Importation réussie", 
            count: usersToInsert.length 
        });
    } catch (err) {
        console.error("❌ Erreur Import Students:", err.message);
        res.status(500).json({ 
            message: "Erreur lors de l'importation (certains matricules existent peut-être déjà).", 
            error: err.message 
        });
    }
});

module.exports = router;