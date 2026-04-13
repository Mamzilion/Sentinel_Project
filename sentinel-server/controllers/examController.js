const Examen = require('../models/Examen');
const Copie = require('../models/Copie');
const User = require('../models/User');

// --- 1. RÉCUPÉRATION DES EXAMENS (Dashboard) ---
exports.getTeacherExams = async (req, res) => {
    try {
        const { enseignantId } = req.query;
        if (!enseignantId) {
            return res.status(400).json({ message: "ID Enseignant manquant." });
        }
        const examens = await Examen.find({ enseignantId }).sort({ dateCreation: -1 });
        res.status(200).json(examens);
    } catch (err) {
        res.status(500).json({ message: "Erreur récupération sujets.", error: err.message });
    }
};

// --- 2. RÉCUPÉRATION DES COPIES D'UN EXAMEN ---
exports.getExamenCopies = async (req, res) => {
    try {
        const { id } = req.params;
        const copies = await Copie.find({ examenId: id }).sort({ dateSoumission: -1 });
        if (!copies || copies.length === 0) {
            return res.status(404).json({ message: "Aucune copie trouvée." });
        }
        res.status(200).json(copies);
    } catch (err) {
        res.status(500).json({ message: "Erreur récupération copies." });
    }
};

// --- 3. BASCULER LE STATUT ---
exports.toggleStatus = async (req, res) => {
    try {
        const ex = await Examen.findById(req.params.id);
        if (!ex) return res.status(404).json({ message: "Examen introuvable" });
        ex.statut = (ex.statut === 'Actif') ? 'Brouillon' : 'Actif';
        await ex.save();
        res.json({ message: "Statut mis à jour", status: ex.statut });
    } catch (err) {
        res.status(500).json({ message: "Erreur toggle", error: err.message });
    }
};

// --- 4. CRÉATION D'UN EXAMEN ---
exports.createExamen = async (req, res) => {
    try {
        const nouvelExamen = new Examen(req.body);
        await nouvelExamen.save();
        res.status(201).json(nouvelExamen);
    } catch (err) {
        res.status(400).json({ message: "Données invalides", error: err.message });
    }
};

// --- 5. SOUMISSION D'UNE COPIE (Version Corrigée) ---
exports.submitCopie = async (req, res) => {
    try {
        let { matricule, responses, macAddress, examenId } = req.body;
        
        if (!matricule) {
            return res.status(400).json({ message: "Le matricule est requis." });
        }

        // Nettoyage strict pour éviter les erreurs de saisie
        const matriculeClean = matricule.trim().toUpperCase();
        
        console.log(`🔍 Liaison en cours pour le matricule : [${matriculeClean}]`);

        // On cherche l'étudiant (on retire le regex si ton schéma force déjà l'uppercase pour plus de rapidité)
        const studentInfo = await User.findOne({ matricule: matriculeClean });

        if (studentInfo) {
            console.log(`✅ MATCH : ${studentInfo.nom} ${studentInfo.prenom} associé à la copie.`);
        } else {
            console.log(`❌ FAIL : Matricule [${matriculeClean}] non trouvé dans la collection User.`);
        }
        
        const nouvelleCopie = new Copie({
            examenId,
            matricule: matriculeClean,
            // Si studentInfo existe, on prend ses données, sinon on met "Inconnu"
            nom: studentInfo ? studentInfo.nom : "Inconnu",
            prenom: studentInfo ? studentInfo.prenom : "N/A",
            responses,
            macAddress,
            dateSoumission: new Date()
        });

        await nouvelleCopie.save();
        
        res.status(201).json({ 
            message: "Copie soumise avec succès !", 
            etudiant: studentInfo ? `${studentInfo.nom} ${studentInfo.prenom}` : "Anonyme"
        });

    } catch (error) {
        if (error.code === 11000) {
            return res.status(400).json({ message: "Vous avez déjà soumis une copie pour cet examen." });
        }
        console.error("❌ Erreur lors de la sauvegarde de la copie:", error);
        res.status(500).json({ message: "Erreur serveur lors de la soumission." });
    }
};

// --- 6. CLÔTURE DE SESSION ---
exports.cloturerExamen = async (req, res) => {
    try {
        const result = await User.updateMany(
            { role: 'Etudiant' }, 
            { $set: { macAddress: null } }
        );
        res.status(200).json({ message: "Postes libérés.", count: result.modifiedCount });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};