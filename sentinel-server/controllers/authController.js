const User = require('../models/User');

// --- 1. CONNEXION PRINCIPALE ---
exports.login = async (req, res) => {
    try {
        const { matricule, password, macAddress } = req.body;

        // 1. Recherche de l'utilisateur
        const user = await User.findOne({ matricule: matricule.toUpperCase() });

        // 2. Vérification existence et mot de passe
        if (!user || user.password !== password) {
            return res.status(401).json({ message: "Identifiants invalides (Matricule ou Mot de passe)." });
        }

        // 3. Logique spécifique aux Étudiants (Verrouillage de session par MAC)
        if (user.role === 'Etudiant') {
            if (!macAddress) {
                return res.status(400).json({ message: "L'adresse MAC est requise pour sécuriser votre session." });
            }

            const currentMac = macAddress.toLowerCase().trim();

            if (!user.macAddress) {
                user.macAddress = currentMac;
                await user.save();
                console.log(`🔒 Session verrouillée : Étudiant ${user.matricule} assigné au poste ${currentMac}`);
            } 
            else if (user.macAddress !== currentMac) {
                console.log(`⚠️ Tentative de fraude : ${user.matricule} essaie de changer de poste`);
                return res.status(403).json({ 
                    message: "Tricherie suspectée : Ce compte est déjà utilisé sur un autre poste." 
                });
            }
        }

        // 4. Succès : On renvoie l'ID (_) pour le filtrage Enseignant
        res.status(200).json({ 
            message: "Connexion autorisée", 
            user: { 
                _id: user._id, // INDISPENSABLE pour filtrer les examens
                matricule: user.matricule,
                nom: user.nom, 
                prenom: user.prenom,
                role: user.role,
                isFirstLogin: user.isFirstLogin 
            } 
        });

    } catch (err) {
        console.error("❌ Erreur AuthController Login:", err.message);
        res.status(500).json({ message: "Erreur serveur", error: err.message });
    }
};

// --- 2. CHANGEMENT DE MOT DE PASSE ---
exports.changePassword = async (req, res) => {
    try {
        const { matricule, newPassword } = req.body;

        if (!newPassword || newPassword.length < 4) {
            return res.status(400).json({ message: "Le mot de passe est trop court." });
        }

        const user = await User.findOneAndUpdate(
            { matricule: matricule.toUpperCase() },
            { 
                password: newPassword, 
                isFirstLogin: false 
            },
            { new: true }
        );

        if (!user) return res.status(404).json({ message: "Utilisateur non trouvé." });

        console.log(`🔑 Mot de passe mis à jour pour : ${user.matricule}`);
        res.status(200).json({ message: "Mot de passe modifié avec succès !" });

    } catch (err) {
        res.status(500).json({ message: "Erreur serveur", error: err.message });
    }
};