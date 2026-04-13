const mongoose = require('mongoose');
const fs = require('fs');
const csv = require('csv-parser');
const User = require('./models/User');
require('dotenv').config();

const FILE_ETUDIANTS = './etudiants.csv';
const FILE_ENSEIGNANTS = './enseignants.csv';
const PASS_ETUDIANT = 'IUT2026';
const PASS_PROFS = 'SENTINEL2026';

const processCSV = (filePath, role, password) => {
    return new Promise((resolve, reject) => {
        const results = [];
        if (!fs.existsSync(filePath)) {
            console.log(`⚠️ Fichier ${filePath} non trouvé, passage...`);
            return resolve([]);
        }
        fs.createReadStream(filePath)
            .pipe(csv())
            .on('data', (data) => {
                results.push({
                    matricule: data.matricule.trim().toUpperCase(),
                    nom: data.nom.trim(),
                    prenom: data.prenom.trim(),
                    password: password,
                    role: role,
                    macAddress: null
                });
            })
            .on('end', () => resolve(results))
            .on('error', (err) => reject(err));
    });
};

const importAll = async () => {
    try {
        await mongoose.connect(process.env.MONGO_URI || 'mongodb://127.0.0.1:27017/sentinel_db');
        console.log("📡 Connexion MongoDB OK.");

        // 1. Nettoyage des anciens comptes (sauf Admin)
        await User.deleteMany({ role: { $ne: 'Admin' } });

        // 2. Importation Étudiants
        const etudiants = await processCSV(FILE_ETUDIANTS, 'Etudiant', PASS_ETUDIANT);
        if (etudiants.length > 0) await User.insertMany(etudiants);

        // 3. Importation Enseignants
        const profs = await processCSV(FILE_ENSEIGNANTS, 'Enseignant', PASS_PROFS);
        if (profs.length > 0) await User.insertMany(profs);

        // 4. Création manuelle des Admins (Daniel et un backup)
        const admins = [
            { matricule: "ADMIN01", nom: "MAMA", prenom: "Daniel", password: "admin123", role: "Admin" },
            { matricule: "ADMIN02", nom: "SYSTEM", prenom: "Root", password: "root_sentinel", role: "Admin" }
        ];

        for (const admin of admins) {
            await User.findOneAndUpdate(
                { matricule: admin.matricule },
                admin,
                { upsert: true, new: true }
            );
        }

        console.log(`✅ Importation terminée :`);
        console.log(`- ${etudiants.length} Étudiants`);
        console.log(`- ${profs.length} Enseignants`);
        console.log(`- 2 Admins (Daniel & Root)`);
        
        process.exit();
    } catch (err) {
        console.error("❌ Erreur :", err);
        process.exit(1);
    }
};

importAll();