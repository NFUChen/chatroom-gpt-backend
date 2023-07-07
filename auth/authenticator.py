import bcrypt

class Authenticator:
    @staticmethod
    def hash_password(password: str) -> str:
        # Generate a random salt
        salt = bcrypt.gensalt()
        
        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        
        # Return the hashed password as a string
        return hashed_password.decode()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        # Verify if the provided password matches the stored hashed password
        return bcrypt.checkpw(password.encode(), hashed_password.encode())