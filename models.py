"""
Database models for NetWorthy application using SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class NetWorthYear(db.Model):
    """Model representing net worth data for a specific year"""
    __tablename__ = 'net_worth_years'

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False, index=True)
    birth_year = db.Column(db.Integer, nullable=True)
    total_assets = db.Column(db.Float, default=0.0)
    total_liabilities = db.Column(db.Float, default=0.0)
    total_income = db.Column(db.Float, default=0.0)
    net_worth = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.String(20), default=lambda: datetime.now().strftime('%Y-%m-%d'))

    # JSON fields for complex nested data
    assets_data = db.Column(db.Text, default='{}')  # Store as JSON string
    liabilities_data = db.Column(db.Text, default='{}')  # Store as JSON string
    income_data = db.Column(db.Text, default='{}')  # Store as JSON string

    def __init__(self, year, birth_year=None):
        self.year = year
        self.birth_year = birth_year
        self.total_assets = 0.0
        self.total_liabilities = 0.0
        self.total_income = 0.0
        self.net_worth = 0.0
        self.last_updated = datetime.now().strftime('%Y-%m-%d')
        self.assets_data = json.dumps(self._get_default_assets())
        self.liabilities_data = json.dumps({})
        self.income_data = json.dumps({})

    @staticmethod
    def _get_default_assets():
        """Return default assets structure"""
        return {
            'cash': {
                'total': 0,
                'list': {}
            },
            'investments': {
                'total': 0,
                'pre_tax': {
                    'total': 0,
                    'list': {}
                },
                'tax_free': {
                    'total': 0,
                    'list': {}
                },
                'after_tax': {
                    'total': 0,
                    'list': {}
                }
            },
            'business_interests': {
                'total': 0,
                'list': {}
            },
            'property': {
                'total': 0,
                'list': {}
            }
        }

    @property
    def assets(self):
        """Get assets as Python dict"""
        try:
            return json.loads(self.assets_data)
        except (json.JSONDecodeError, TypeError):
            return self._get_default_assets()

    @assets.setter
    def assets(self, value):
        """Set assets from Python dict"""
        self.assets_data = json.dumps(value)

    @property
    def liabilities(self):
        """Get liabilities as Python dict"""
        try:
            return json.loads(self.liabilities_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    @liabilities.setter
    def liabilities(self, value):
        """Set liabilities from Python dict"""
        self.liabilities_data = json.dumps(value)

    @property
    def income(self):
        """Get income as Python dict"""
        try:
            return json.loads(self.income_data)
        except (json.JSONDecodeError, TypeError):
            return {}

    @income.setter
    def income(self, value):
        """Set income from Python dict"""
        self.income_data = json.dumps(value)

    def to_dict(self):
        """Convert to dictionary matching the old JSON format"""
        return {
            'birth_year': self.birth_year,
            'total_assets': self.total_assets,
            'total_liabilities': self.total_liabilities,
            'total_income': self.total_income,
            'net_worth': self.net_worth,
            'last_updated': self.last_updated,
            'assets': self.assets,
            'liabilities': self.liabilities,
            'income': self.income
        }

    @classmethod
    def from_dict(cls, year, data):
        """Create instance from dictionary (old JSON format)"""
        instance = cls(year, birth_year=data.get('birth_year'))
        instance.total_assets = data.get('total_assets', 0.0)
        instance.total_liabilities = data.get('total_liabilities', 0.0)
        instance.total_income = data.get('total_income', 0.0)
        instance.net_worth = data.get('net_worth', 0.0)
        instance.last_updated = data.get('last_updated', datetime.now().strftime('%Y-%m-%d'))
        instance.assets = data.get('assets', cls._get_default_assets())
        instance.liabilities = data.get('liabilities', {})
        instance.income = data.get('income', {})
        return instance

    def __repr__(self):
        return f'<NetWorthYear {self.year}: ${self.net_worth:,.2f}>'
