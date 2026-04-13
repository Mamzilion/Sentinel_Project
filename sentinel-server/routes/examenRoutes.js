const express = require('express');
const router = express.Router();
const Examen = require('../models/Examen');
const Copie = require('../models/Copie'); // Assure-toi que ce modèle existe
const examController = require('../controllers/examController');

// ==========================================
//   ROUTES ENSEIGNANT (DASHBOARD WEB)
// ==========================================

// 1. Récupérer les sujets (Filtré par enseignantId pour l'isolation)
router.get('/all', async (req, res) => {
    try {
        const { enseignantId } = req.query;
        // Crucial : on filtre pour que le prof ne voit pas les sujets des autres
        const filter = enseignantId ? { enseignantId: enseignantId } : {};
        const examens = await Examen.find(filter).sort({ dateCreation: -1 });
        res.json(examens);
    } catch (err) {
        res.status(500).json({ message: "Erreur lors de la récupération des sujets." });
    }
});

// 2. Créer un examen
router.post('/create', async (req, res) => {
    try {
        const nouvelExamen = new Examen(req.body);
        await nouvelExamen.save();
        res.status(201).json(nouvelExamen);
    } catch (err) {
        res.status(400).json({ message: "Erreur de création", details: err.message });
    }
});

// 3. Modifier un examen (Utilisé par prepEdit)
router.put('/update/:id', async (req, res) => {
    try {
        const updated = await Examen.findByIdAndUpdate(req.params.id, req.body, { new: true });
        res.json(updated);
    } catch (err) {
        res.status(400).json({ message: "Erreur de mise à jour" });
    }
});

// 4. Toggle Status (Actif/Brouillon)
router.patch('/:id/toggle-status', async (req, res) => {
    try {
        const ex = await Examen.findById(req.params.id);
        if(!ex) return res.status(404).json({ message: "Examen non trouvé" });
        
        ex.statut = (ex.statut === 'Actif') ? 'Brouillon' : 'Actif';
        await ex.save();
        res.json(ex);
    } catch (err) {
        res.status(400).json({ message: "Erreur de changement de statut" });
    }
});

// 5. Récupérer les copies reçues pour un examen
router.get('/:id/copies', async (req, res) => {
    try {
        // On cherche toutes les copies liées à l'ID de l'examen
        const copies = await Copie.find({ examenId: req.params.id });
        if (copies.length === 0) return res.status(404).json({ message: "Aucune copie" });
        res.json(copies);
    } catch (err) {
        res.status(500).json({ message: "Erreur lors de la récupération des copies" });
    }
});

// ==========================================
//   ROUTES ÉTUDIANT (AGENT PYTHON / FLUTTER)
// ==========================================

// 6. Liste des examens disponibles (ceux que l'étudiant n'a pas encore fait)
router.get('/liste-actifs/:matricule', async (req, res) => {
    try {
        const { matricule } = req.params;
        const examensActifs = await Examen.find({ statut: 'Actif' }).select('titre codeMatiere _id duree');
        
        // On récupère les IDs des examens déjà soumis par cet étudiant
        const copiesFaites = await Copie.find({ matricule: matricule.toUpperCase() }).select('examenId');
        const idsFaits = copiesFaites.map(c => c.examenId.toString());

        // On ne garde que ceux qui n'ont pas de copie correspondante
        const dispo = examensActifs.filter(e => !idsFaits.includes(e._id.toString()));
        res.json(dispo);
    } catch (err) {
        res.status(500).json({ message: "Erreur serveur liste-actifs" });
    }
});

// 7. Récupérer le contenu complet d'un sujet (Questions) - GARDÉ TEL QUEL POUR LE LANCEMENT
router.get('/:id', async (req, res) => {
    try {
        const examen = await Examen.findById(req.params.id);
        if (!examen || examen.statut !== 'Actif') {
            return res.status(403).json({ message: "Ce sujet n'est pas accessible." });
        }
        res.json(examen);
    } catch (err) {
        res.status(500).json({ message: "Erreur de récupération du sujet" });
    }
});

// 8. Soumission de la copie finale (APPLIQUÉ ICI UNIQUEMENT)
router.post('/soumettre', examController.submitCopie);

module.exports = router;