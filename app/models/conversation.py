from app import db
from datetime import datetime

class Conversation(db.Model):
    """Modelo para almacenar el historial de conversaciones con los usuarios"""
    
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    sender_type = db.Column(db.String(10), nullable=False)  # 'user' o 'bot'
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    feedback = db.Column(db.Integer, nullable=True)  # Para calificación de la respuesta (1-5)
    
    # Relación con el cliente
    customer = db.relationship('Customer', backref=db.backref('conversations', lazy=True))
    
    def __repr__(self):
        return f'<Conversation {self.id} - Customer {self.customer_id}>'