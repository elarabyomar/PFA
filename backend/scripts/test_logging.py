#!/usr/bin/env python3
"""
Script de test pour vérifier le système de logging
"""

import os
import logging
from datetime import datetime

def setup_logging():
    """Configure le système de logging complet avec fichiers et console"""
    # Créer le dossier logs dans le répertoire racine du projet (local)
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Nom du fichier de log avec timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_filename = f'test_logging_{timestamp}.log'
    log_filepath = os.path.join(logs_dir, log_filename)
    
    # Configuration du logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            # Handler pour fichier (niveau DEBUG - tout)
            logging.FileHandler(log_filepath, encoding='utf-8'),
            # Handler pour console (niveau INFO - moins verbeux)
            logging.StreamHandler()
        ]
    )
    
    # Logger principal
    logger = logging.getLogger(__name__)
    
    # Log de début
    logger.info("=" * 80)
    logger.info("🧪 TEST DU SYSTÈME DE LOGGING")
    logger.info(f"📁 Fichier de log LOCAL: {log_filepath}")
    logger.info(f"📂 Dossier logs: {logs_dir}")
    logger.info(f"⏰ Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 80)
    
    return logger, log_filepath

if __name__ == "__main__":
    # Configuration du logging
    logger, log_filepath = setup_logging()
    
    # Test des différents niveaux de logging
    logger.debug("🔍 Message DEBUG - très détaillé")
    logger.info("ℹ️ Message INFO - information générale")
    logger.warning("⚠️ Message WARNING - avertissement")
    logger.error("❌ Message ERROR - erreur")
    
    # Test avec des données
    logger.info("📊 Test avec des données:")
    logger.info("   • Table: users")
    logger.info("   • Colonnes: id, nom, prenom")
    logger.info("   • Type: MASTER")
    
    # Test d'erreur avec traceback
    try:
        # Simuler une erreur
        result = 1 / 0
    except Exception as e:
        logger.error("❌ Erreur simulée pour tester le logging", exc_info=True)
    
    logger.info("✅ Test de logging terminé")
    logger.info(f"📁 Vérifiez le fichier: {log_filepath}")
    
    print(f"\n✅ Test terminé! Vérifiez le fichier: {log_filepath}")
