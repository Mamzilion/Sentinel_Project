require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const helmet = require('helmet');
const path = require('path');

// --- IMPORT DES MODULES & ROUTES ---
const upload = require('./middleware/upload');
const Alert = require('./models/Alert');
const authController = require('./controllers/authController');
const examRoutes = require('./routes/examRoutes'); // Route pour les sujets

const app = express();

// --- MIDDLEWARES ---
app.use(express.json());
app.use(cors());
app.use(helmet());

// Accès public aux fichiers (Photos d'alertes / Copies)
app.use('/storage', express.static(path.join(__dirname, 'storage')));

// --- CONNEXION MONGODB ---
mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/sentinel_db')
    .then(() => console.log('✅ MongoDB Connecté (Sentinel)'))
    .catch(err => console.log('❌ Erreur de connexion MongoDB:', err));

// --- ROUTES ---

// 1. Authentification (Login + Vérification MAC via le contrôleur)
app.post('/api/auth/login', authController.login);

// 2. Gestion des Examens (Récupération des sujets par l'Agent)
app.use('/api/exams', examRoutes);

// 3. Réception des Alertes (Capture Webcam + Logs de triche)
app.post('/api/alerts/upload', upload.single('photo'), async (req, res) => {
    try {
        const { matricule, type_incident } = req.body;
        
        const newAlert = new Alert({
            matricule,
            type_incident: type_incident,
            photo_url: req.file ? req.file.path : null
        });

        await newAlert.save();
        
        console.log(`⚠️ ALERTE : [${type_incident}] enregistrée pour l'étudiant ${matricule}`);
        res.status(201).json({ 
            message: "Alerte et preuve visuelle sauvegardées avec succès",
            alertId: newAlert._id 
        });
    } catch (err) {
        console.error("❌ Erreur lors de l'enregistrement de l'alerte:", err);
        res.status(500).json({ error: err.message });
    }
});

// --- LANCEMENT DU SERVEUR ---
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 Serveur Sentinel démarré sur le port ${PORT}`);
    console.log(`📂 Dossier de stockage : ${path.join(__dirname, 'storage')}`);
});