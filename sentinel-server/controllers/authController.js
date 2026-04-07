const User = require('../models/User');

exports.login = async (req, res) => {
    const { matricule, password, macAddress } = req.body;

    try {
        const user = await User.findOne({ matricule: matricule.toUpperCase() });

        if (!user || user.mot_de_pass !== password) {
            return res.status(401).json({ message: "Identifiants invalides" });
        }

        // --- SÉCURITÉ RÉSEAU ---
        if (user.role === 'Etudiant') {
            if (user.adresse_mac_autorisee !== macAddress.toLowerCase()) {
                return res.status(403).json({ message: "Poste non autorisé pour ce matricule" });
            }
        }

        res.status(200).json({ 
            message: "Succès", 
            user: { nom: user.nom, role: user.role } 
        });
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
};