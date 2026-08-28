"""
Password generator module for creating strong, random passwords.
"""

import secrets
import string
from typing import List


class PasswordGenerator:
    """
    Generates strong, random passwords with customizable options.
    """

    def __init__(self):
        """Initialize the password generator."""
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.special = string.punctuation

    def generate(self, length: int = 16, use_uppercase: bool = True,
                use_digits: bool = True, use_special: bool = True,
                use_lowercase: bool = True) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Length of the password (minimum 4)
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            use_special: Include special characters
            
        Returns:
            Generated password
            
        Raises:
            ValueError: If length is too short or no character types selected
        """
        if length < 4:
            raise ValueError("Password length must be at least 4 characters")
        
        character_sets = []
        if use_lowercase:
            character_sets.append(self.lowercase)
        if use_uppercase:
            character_sets.append(self.uppercase)
        if use_digits:
            character_sets.append(self.digits)
        if use_special:
            character_sets.append(self.special)

        if not character_sets:
            raise ValueError("At least one character type must be selected")

        if length < len(character_sets):
            raise ValueError("Password length must fit all selected character types")

        character_pool = ''.join(character_sets)
        password_list = [secrets.choice(character_set) for character_set in character_sets]
        password_list.extend(
            secrets.choice(character_pool) for _ in range(length - len(password_list))
        )
        secrets.SystemRandom().shuffle(password_list)
        return ''.join(password_list)

    def generate_multiple(self, count: int = 5, length: int = 16,
                         use_uppercase: bool = True, use_digits: bool = True,
                         use_special: bool = True,
                         use_lowercase: bool = True) -> List[str]:
        """
        Generate multiple passwords.
        
        Args:
            count: Number of passwords to generate
            length: Length of each password
            use_uppercase: Include uppercase letters
            use_digits: Include digits
            use_special: Include special characters
            
        Returns:
            List of generated passwords
        """
        return [self.generate(length, use_uppercase, use_digits, use_special,
                      use_lowercase)
                for _ in range(count)]

    def evaluate_strength(self, password: str) -> tuple:
        """
        Evaluate password strength.
        
        Args:
            password: Password to evaluate
            
        Returns:
            Tuple of (strength_score, strength_level, feedback)
            - strength_score: 0-100
            - strength_level: 'Weak', 'Fair', 'Good', 'Strong', 'Very Strong'
            - feedback: List of suggestions
        """
        score = 0
        feedback = []
        
        # Length checks
        if len(password) >= 8:
            score += 10
        if len(password) >= 12:
            score += 10
        if len(password) >= 16:
            score += 10
        else:
            feedback.append("Use at least 16 characters for better security")
        
        # Character type checks
        if any(c in self.lowercase for c in password):
            score += 10
        else:
            feedback.append("Add lowercase letters")
        
        if any(c in self.uppercase for c in password):
            score += 10
        else:
            feedback.append("Add uppercase letters")
        
        if any(c in self.digits for c in password):
            score += 10
        else:
            feedback.append("Add numbers")
        
        if any(c in self.special for c in password):
            score += 10
        else:
            feedback.append("Add special characters for maximum strength")
        
        # Check for common patterns
        common_patterns = ['password', '123456', 'qwerty', 'admin', 'letmein']
        if password.lower() in common_patterns:
            score = 0
            feedback = ["This password is too common. Choose something unique."]
        
        # Determine strength level
        if score >= 90:
            strength_level = "Very Strong"
        elif score >= 70:
            strength_level = "Strong"
        elif score >= 50:
            strength_level = "Good"
        elif score >= 30:
            strength_level = "Fair"
        else:
            strength_level = "Weak"
        
        return score, strength_level, feedback
