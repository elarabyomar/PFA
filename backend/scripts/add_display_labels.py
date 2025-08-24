#!/usr/bin/env python3
"""
Script pour ajouter automatiquement les libellés d'affichage manquants
dans le fichier DBTABLES.csv
"""

import csv
import os

def add_display_labels():
    """Ajoute les libellés d'affichage manquants dans le CSV"""
    
    csv_path = os.path.join(os.path.dirname(__file__), 'DBTABLES.csv')
    temp_path = csv_path + '.tmp'
    
    # Dictionnaire de mapping pour les libellés d'affichage
    display_labels = {
        # Tables de référence
        'usage': {
            'id': 'ID',
            'codeUsage': 'Code Usage',
            'libelle': 'Libellé Usage'
        },
        'rdv': {
            'id': 'ID',
            'codeRDV': 'Code RDV',
            'libelle': 'Libellé RDV'
        },
        'droits': {
            'id': 'ID',
            'codeDroits': 'Code Droits',
            'libelle': 'Libellé Droits'
        },
        'profiles': {
            'id': 'ID',
            'codeDroits': 'Code Droits',
            'libelle': 'Libellé Profile'
        },
        'marques': {
            'id': 'ID',
            'codeMarques': 'Code Marque',
            'libelle': 'Libellé Marque'
        },
        'carrosseries': {
            'id': 'ID',
            'codeCarrosseries': 'Code Carrosserie',
            'libelle': 'Libellé Carrosserie'
        },
        'villes': {
            'id': 'ID',
            'codeVilles': 'Code Ville',
            'libelle': 'Libellé Ville'
        },
        'banques': {
            'id': 'ID',
            'codeBanques': 'Code Banque',
            'libelle': 'Libellé Banque'
        },
        'bonus_auto': {
            'id': 'ID',
            'codeBonus': 'Code Bonus',
            'libelle': 'Libellé Bonus',
            'coeff': 'Coefficient',
            'taux': 'Taux'
        },
        'paiment': {
            'id': 'ID',
            'codePaiment': 'Code Paiement',
            'libelle': 'Mode de Paiement'
        },
        'taxe': {
            'id': 'ID'
        },
        'commission_forfait': {
            'idCommissionType': 'ID Type Commission'
        },
        
        # Tables transactionnelles
        'devis': {
            'id': 'ID',
            'idClient': 'Client',
            'idUser': 'Utilisateur',
            'idProduit': 'Produit',
            'dateCreation': 'Date Création',
            'etat': 'État',
            'montantEstime': 'Montant Estimé',
            'observations': 'Observations'
        },
        'production': {
            'id': 'ID',
            'idQuittance': 'Quittance',
            'idClient': 'Client',
            'idCIE': 'Compagnie',
            'idProduit': 'Produit',
            'idBranche': 'Branche',
            'idGarantie': 'Garantie',
            'idSousGarantie': 'Sous-Garantie',
            'idUsage': 'Usage',
            'idAvenant': 'Avenant',
            'idSousTypeAvenant': 'Sous-Type Avenant',
            'numPolice': 'Numéro Police',
            'dateDebut': 'Date Début',
            'dateFin': 'Date Fin',
            'dateEmis': 'Date Émission',
            'dateEncaissement': 'Date Encaissement',
            'typeEncaissement': 'Type Encaissement',
            'primeTotale': 'Prime Totale',
            'idComission': 'Commission',
            'idTaxes': 'Taxes'
        },
        'sinistre': {
            'id': 'ID',
            'idProduction': 'Production',
            'dateDeclaration': 'Date Déclaration',
            'dateSurvenance': 'Date Survenance',
            'dateVue': 'Date Vue',
            'idSousGarantie': 'Sous-Garantie',
            'etat': 'État'
        },
        'sinistre_vue': {
            'id': 'ID',
            'idSinistre': 'Sinistre',
            'dateMouvement': 'Date Mouvement',
            'typeMouvement': 'Type Mouvement',
            'montant': 'Montant'
        },
        'attestation': {
            'id': 'ID',
            'idCIE': 'Compagnie',
            'idUser': 'Utilisateur',
            'dateLivraison': 'Date Livraison',
            'codeUsage': 'Type Usage'
        },
        'reglement': {
            'id': 'ID',
            'idProduction': 'Production',
            'idPaiment': 'Mode Paiement',
            'dateReglement': 'Date Règlement',
            'ref': 'Référence',
            'mode': 'Mode'
        },
        'agenda': {
            'id': 'ID',
            'idUser': 'Utilisateur',
            'idRDV': 'RDV',
            'objet': 'Objet',
            'description': 'Description',
            'dateDebut': 'Date Début',
            'dateFin': 'Date Fin'
        },
        'userProfiles': {
            'idUser': 'ID Utilisateur',
            'idProfile': 'ID Profile'
        },
        'avenant_soustype': {
            'id': 'ID',
            'idAvenant': 'Avenant',
            'description': 'Description'
        },
        'opportunites': {
            'id': 'ID',
            'idClient': 'Client',
            'idUser': 'Utilisateur',
            'idProduit': 'Produit',
            'budgetEstime': 'Budget Estimé',
            'origine': 'Origine',
            'etape': 'Étape',
            'dateCreation': 'Date Création',
            'dateEcheance': 'Date Échéance',
            'description': 'Description'
        },
        'reclamations': {
            'id': 'ID',
            'idClient': 'Client',
            'idProduction': 'Production',
            'idUser': 'Utilisateur',
            'objet': 'Objet',
            'description': 'Description',
            'dateOuverture': 'Date Ouverture',
            'dateCloture': 'Date Clôture',
            'etat': 'État',
            'solution': 'Solution'
        },
        'recommandations': {
            'id': 'ID',
            'idClientRecommande': 'Client Recommandé',
            'sourceType': 'Type Source',
            'sourceId': 'ID Source',
            'dateRecommandation': 'Date Recommandation',
            'statut': 'Statut'
        },
        
        # Tables de log
        'historique_modifications': {
            'id': 'ID',
            'nomTable': 'Nom Table',
            'idEnregistrement': 'ID Enregistrement',
            'nomColonne': 'Nom Colonne',
            'ancienneValeur': 'Ancienne Valeur',
            'nouvelleValeur': 'Nouvelle Valeur',
            'idUser': 'Utilisateur',
            'instantModification': 'Date Modification'
        }
    }
    
    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as infile, \
             open(temp_path, 'w', encoding='utf-8', newline='') as outfile:
            
            reader = csv.DictReader(infile)
            
            # Vérifier si la colonne Libellé Affichage existe déjà
            fieldnames = reader.fieldnames
            if 'Libellé Affichage' not in fieldnames:
                fieldnames = list(fieldnames) + ['Libellé Affichage']
            
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in reader:
                table_name = row['Table'].strip()
                column_name = row['Colonne'].strip()
                
                # Ajouter le libellé d'affichage
                if table_name in display_labels and column_name in display_labels[table_name]:
                    row['Libellé Affichage'] = display_labels[table_name][column_name]
                else:
                    # Générer un libellé par défaut basé sur la description
                    description = row.get('Description', '')
                    if description:
                        # Prendre les premiers mots de la description
                        words = description.split()
                        if len(words) >= 2:
                            row['Libellé Affichage'] = ' '.join(words[:2]).title()
                        else:
                            row['Libellé Affichage'] = description.title()
                    else:
                        # Utiliser le nom de la colonne comme fallback
                        row['Libellé Affichage'] = column_name.replace('_', ' ').title()
                
                writer.writerow(row)
        
        # Remplacer le fichier original
        os.replace(temp_path, csv_path)
        print("✅ Libellés d'affichage ajoutés avec succès !")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des libellés: {e}")
        if os.path.exists(temp_path):
            os.remove(temp_path)

if __name__ == "__main__":
    print("🚀 Ajout des libellés d'affichage dans DBTABLES.csv...")
    add_display_labels()
