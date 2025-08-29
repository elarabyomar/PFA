import csv
import os
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class CSVService:
    def __init__(self):
        self.scripts_dir = os.path.join(os.path.dirname(__file__), '..', 'scripts')
    
    def load_flotte_auto_data(self) -> List[Dict[str, Any]]:
        """Load flotte_auto data from CSV file"""
        try:
            csv_path = os.path.join(self.scripts_dir, 'adherents_data.csv')
            if not os.path.exists(csv_path):
                logger.warning(f"CSV file not found: {csv_path}")
                return []
            
            data = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    # Convert numeric values
                    if row.get('valeurNeuve'):
                        try:
                            row['valeurNeuve'] = float(row['valeurNeuve'])
                        except ValueError:
                            row['valeurNeuve'] = None
                    
                    if row.get('valeurVenale'):
                        try:
                            row['valeurVenale'] = float(row['valeurVenale'])
                        except ValueError:
                            row['valeurVenale'] = None
                    
                    data.append(row)
            
            logger.info(f"Loaded {len(data)} flotte_auto records from CSV")
            return data
            
        except Exception as e:
            logger.error(f"Error loading flotte_auto CSV data: {e}")
            return []
    
    def load_assure_sante_data(self) -> List[Dict[str, Any]]:
        """Load assure_sante data from CSV file"""
        try:
            csv_path = os.path.join(self.scripts_dir, 'assure_sante_data.csv')
            if not os.path.exists(csv_path):
                logger.warning(f"CSV file not found: {csv_path}")
                return []
            
            data = []
            with open(csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    data.append(row)
            
            logger.info(f"Loaded {len(data)} assure_sante records from CSV")
            return data
            
        except Exception as e:
            logger.error(f"Error loading assure_sante CSV data: {e}")
            return []
    
    def get_flotte_auto_by_client(self, client_societe_id: int) -> List[Dict[str, Any]]:
        """Get flotte_auto data filtered by client societe ID"""
        all_data = self.load_flotte_auto_data()
        return [item for item in all_data if int(item.get('idClientSociete', 0)) == client_societe_id]
    
    def get_assure_sante_by_client(self, client_societe_id: int) -> List[Dict[str, Any]]:
        """Get assure_sante data filtered by client societe ID"""
        all_data = self.load_assure_sante_data()
        return [item for item in all_data if int(item.get('idClientSociete', 0)) == client_societe_id]
