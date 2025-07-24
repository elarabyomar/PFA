#!/usr/bin/env python3
"""
Script de test pour vérifier l'authentification admin
"""

from passlib.context import CryptContext
from datetime import datetime

# Créer le contexte de hachage
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hash du mot de passe "admin" dans la base
admin_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.i8mO"

# Test avec le mot de passe "admin"
password = "admin"
is_valid = pwd_context.verify(password, admin_hash)

print(f"Test d'authentification admin:")
print(f"Mot de passe: {password}")
print(f"Hash en base: {admin_hash}")
print(f"Vérification bcrypt: {is_valid}")

# Test de génération d'un nouveau hash
new_hash = pwd_context.hash(password)
print(f"\nNouveau hash généré: {new_hash}")
print(f"Vérification nouveau hash: {pwd_context.verify(password, new_hash)}")

# Test avec la date de naissance au format YYYYMMDD
birth_date = datetime(2003, 11, 25)
birth_date_str = birth_date.strftime("%Y%m%d")  # Format YYYYMMDD
print(f"\nTest avec date de naissance:")
print(f"Date de naissance: {birth_date.strftime('%Y-%m-%d')}")
print(f"Format mot de passe: {birth_date_str}")
print(f"Hash en base: {admin_hash}")
print(f"Vérification bcrypt: {pwd_context.verify(birth_date_str, admin_hash)}")

# Test de la fonction is_default_password
def is_default_password_test(user_date, password: str) -> bool:
    """Test de la fonction is_default_password"""
    if password == "admin":
        return True
    
    if user_date:
        date_str = user_date.strftime("%Y%m%d")  # Format YYYYMMDD sans tirets
        if password == date_str:
            return True
    
    return False

print(f"\nTest de la fonction is_default_password:")
print(f"Mot de passe 'admin': {is_default_password_test(birth_date, 'admin')}")
print(f"Mot de passe '{birth_date_str}': {is_default_password_test(birth_date, birth_date_str)}")
print(f"Mot de passe '2003-11-25': {is_default_password_test(birth_date, '2003-11-25')}")
print(f"Mot de passe 'wrong': {is_default_password_test(birth_date, 'wrong')}") 