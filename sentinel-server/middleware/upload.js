const multer = require('multer');
const path = require('path');
const fs = require('fs');

const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        // Si c'est une alerte, on range dans storage/alerts, sinon dans storage/copies
        const folder = req.originalUrl.includes('alert') ? 'alerts' : 'copies';
        const dir = `./storage/${folder}`;
        
        // Créer le dossier s'il n'existe pas
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir, { recursive: true });
        }
        cb(null, dir);
    },
    filename: (req, file, cb) => {
        // Nom du fichier : matricule_timestamp.extension
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({ storage: storage });
module.exports = upload;