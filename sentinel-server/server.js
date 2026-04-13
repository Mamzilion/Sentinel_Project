/**
 * SENTINEL - Backend Server v2.1
 * Centralise l'authentification et la gestion des examens.
 */

require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const path = require('path'); // Ajouté pour gérer les chemins proprement

const app = express();

// --- MIDDLEWARES ---
app.use(cors()); // Autorise le Dashboard Web et l'Agent Python
app.use(express.json({ limit: '10mb' })); // Augmenté pour supporter les JSON lourds si besoin

// --- ACCÈS AUX FICHIERS (STATIC) ---
// Cette ligne rend le dossier "uploads" accessible publiquement via l'URL /uploads
app.use('/uploads', express.static(path.join(__dirname, 'uploads')));

// --- CONNEXION MONGODB ---
const mongoURI = process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/sentinel_db';

mongoose.connect(mongoURI)
    .then(() => console.log("🌐 MongoDB Connecté : sentinel_db"))
    .catch(err => console.error("❌ Erreur Mongo:", err));

// --- ROUTES ---
// Authentification & Verrouillage MAC
app.use('/api/auth', require('./routes/authRoutes'));

// Gestion des examens (Sujets et Copies)
app.use('/api/examen', require('./routes/examenRoutes'));

// --- GESTION DES ERREURS ---
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ message: "Erreur interne Sentinel." });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`🚀 SENTINEL v2.1 sur le port ${PORT}`);
});