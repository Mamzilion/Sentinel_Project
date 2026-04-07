const express = require('express');
const router = express.Router();
const Examen = require('../models/Examen');

// Route pour que l'Agent récupère l'examen actif d'une matière
router.get('/fetch/:codeMatiere', async (req, res) => {
    try {
        const examen = await Examen.findOne({ 
            code_matiere: req.params.codeMatiere.toUpperCase(),
            est_actif: true 
        });

        if (!examen) {
            return res.status(404).json({ message: "Aucun examen actif trouvé pour cette matière." });
        }

        res.json(examen);
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

module.exports = router;