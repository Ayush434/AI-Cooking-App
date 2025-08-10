from ..database import db

class RecipeIngredient(db.Model):
    """Association table for Recipe-Ingredient many-to-many relationship with quantity"""
    
    __tablename__ = 'recipe_ingredients'
    
    id = db.Column(db.Integer, primary_key=True)
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipes.id'), nullable=False)
    ingredient_id = db.Column(db.Integer, db.ForeignKey('ingredients.id'), nullable=False)
    
    # Quantity information
    quantity = db.Column(db.Float)  # Amount needed
    unit = db.Column(db.String(20))  # 'cup', 'tbsp', 'piece', 'gram', etc.
    preparation = db.Column(db.String(100))  # 'diced', 'chopped', 'sliced', etc.
    
    # Optional notes
    notes = db.Column(db.String(200))  # 'optional', 'to taste', etc.
    is_optional = db.Column(db.Boolean, default=False)
    
    # Order in the recipe
    order_index = db.Column(db.Integer, default=0)
    
    # Relationships
    recipe = db.relationship('Recipe', back_populates='recipe_ingredients')
    ingredient = db.relationship('Ingredient', back_populates='recipe_ingredients')
    
    # Unique constraint to prevent duplicate ingredient entries in same recipe
    __table_args__ = (db.UniqueConstraint('recipe_id', 'ingredient_id', name='_recipe_ingredient_uc'),)
    
    def __repr__(self):
        return f'<RecipeIngredient {self.quantity} {self.unit} {self.ingredient.name if self.ingredient else "Unknown"}>'
    
    def to_dict(self):
        """Convert recipe ingredient object to dictionary"""
        return {
            'id': self.id,
            'recipe_id': self.recipe_id,
            'ingredient_id': self.ingredient_id,
            'ingredient_name': self.ingredient.name if self.ingredient else None,
            'quantity': self.quantity,
            'unit': self.unit,
            'preparation': self.preparation,
            'notes': self.notes,
            'is_optional': self.is_optional,
            'order_index': self.order_index
        }