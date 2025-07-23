from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from passlib.context import CryptContext
from fastapi import HTTPException, status
import re
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Caractères spéciaux autorisés
SPECIAL_CHARS = "~!@#$%^&*_-+=`|\\(){}[]:;\"\"'<>,.?/"

# Mots de dictionnaire communs à éviter
COMMON_WORDS = [
    "password", "admin", "user", "login", "welcome", "hello", "test", "demo",
    "123456", "qwerty", "abc123", "password123", "admin123", "user123",
    "welcome123", "hello123", "test123", "demo123", "123456789", "qwerty123",
    "password1", "admin1", "user1", "login1", "welcome1", "hello1", "test1",
    "demo1", "12345678", "qwerty1", "abc1234", "password12", "admin12",
    "user12", "login12", "welcome12", "hello12", "test12", "demo12"
]

async def change_admin_default_password(
    session: AsyncSession, 
    current_password: str, 
    new_password: str
) -> bool:
    """
    Change le mot de passe admin par défaut après le premier lancement
    """
    try:
        # Vérifier que l'utilisateur admin existe
        result = await session.execute(
            text("SELECT password FROM users WHERE email = 'admin@gmail.com' AND role = 'admin'")
        )
        admin_user = result.fetchone()
        
        if not admin_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Utilisateur admin non trouvé"
            )
        
        # Vérifier l'ancien mot de passe
        if not pwd_context.verify(current_password, admin_user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Mot de passe admin actuel incorrect"
            )
        
        # Hasher le nouveau mot de passe
        hashed_new_password = pwd_context.hash(new_password)
        
        # Mettre à jour le mot de passe
        await session.execute(
            text("UPDATE users SET password = :password WHERE email = 'admin@gmail.com'"),
            {"password": hashed_new_password}
        )
        
        await session.commit()
        
        return True
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erreur lors du changement de mot de passe admin"
        )

def verify_admin_password_strength(password: str) -> tuple[bool, str]:
    """
    Vérifie la force du mot de passe admin selon les nouvelles règles strictes
    Retourne (is_valid, error_message)
    """
    # 1. Vérifier la longueur minimum
    if len(password) < 12:
        return False, "Le mot de passe doit contenir au moins 12 caractères"
    
    # 2. Définir les catégories de caractères
    categories = {
        'uppercase': string.ascii_uppercase,  # A-Z
        'lowercase': string.ascii_lowercase,  # a-z
        'digits': string.digits,              # 0-9
        'special': SPECIAL_CHARS              # Caractères spéciaux
    }
    
    # 3. Vérifier qu'au moins 3 catégories sont présentes
    present_categories = 0
    for category_name, category_chars in categories.items():
        if any(char in category_chars for char in password):
            present_categories += 1
    
    if present_categories < 3:
        return False, "Le mot de passe doit contenir au moins 3 catégories parmi : majuscules, minuscules, chiffres, caractères spéciaux"
    
    # 4. Vérifier qu'aucun caractère n'est répété plus de 2 fois consécutivement
    for i in range(len(password) - 2):
        if password[i] == password[i+1] == password[i+2]:
            return False, "Le mot de passe ne doit pas contenir plus de 2 caractères identiques consécutifs"
    
    # 5. Vérifier qu'il ne contient pas de mots du dictionnaire commun
    password_lower = password.lower()
    for word in COMMON_WORDS:
        if word in password_lower:
            return False, f"Le mot de passe ne doit pas contenir de mots facilement devinables comme '{word}'"
    
    # 6. Vérifier qu'il ne contient pas de séquences communes
    common_sequences = [
        "123", "234", "345", "456", "567", "678", "789", "012",
        "abc", "bcd", "cde", "def", "efg", "fgh", "ghi", "hij",
        "qwe", "wer", "ert", "rty", "tyu", "yui", "uio", "iop",
        "asd", "sdf", "dfg", "fgh", "ghj", "hjk", "jkl", "klz"
    ]
    
    for seq in common_sequences:
        if seq in password_lower:
            return False, f"Le mot de passe ne doit pas contenir de séquences communes comme '{seq}'"
    
    # 7. Vérifier qu'il ne contient pas de répétitions de caractères simples
    simple_repeats = ["aa", "bb", "cc", "dd", "ee", "ff", "gg", "hh", "ii", "jj", "kk", "ll", "mm", "nn", "oo", "pp", "qq", "rr", "ss", "tt", "uu", "vv", "ww", "xx", "yy", "zz"]
    for repeat in simple_repeats:
        if repeat * 2 in password_lower:  # Plus de 2 répétitions
            return False, f"Le mot de passe ne doit pas contenir de répétitions excessives comme '{repeat}'"
    
    # 8. Vérifier qu'il n'est pas trop simple (trop de caractères identiques)
    char_counts = {}
    for char in password:
        char_counts[char] = char_counts.get(char, 0) + 1
    
    # Si plus de 30% des caractères sont identiques, c'est suspect
    max_repetition = max(char_counts.values()) if char_counts else 0
    if max_repetition > len(password) * 0.3:
        return False, "Le mot de passe contient trop de caractères identiques"
    
    return True, "Mot de passe valide"

async def verify_admin_password_strength_async(password: str) -> bool:
    """
    Version async de la vérification pour compatibilité avec l'ancien code
    """
    is_valid, _ = verify_admin_password_strength(password)
    return is_valid 