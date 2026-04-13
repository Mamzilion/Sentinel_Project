const mongoose = require('mongoose');

const alertSchema = new mongoose.Schema({
    matricule: { type: String, required: true },
    type_incident: { 
        type: String, 
        enum: ['USB_DETECT', 'LOGICIEL_INTERDIT', 'FACE_LOST'], 
        required: true 
    },
    photo_url: { type: String },
    timestamp: { type: Date, default: Date.now }
});

module.exports = mongoose.model('Alert', alertSchema);