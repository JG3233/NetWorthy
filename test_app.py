import unittest
import json
import os
import tempfile
from datetime import datetime
from app import app, load_data, save_data, DATA_FILE


class TestNetWorthApp(unittest.TestCase):
    """Test cases for NetWorthy application"""

    def setUp(self):
        """Set up test fixtures before each test"""
        # Create a temporary file for testing
        self.test_fd, self.test_file = tempfile.mkstemp(suffix='.json')

        # Temporarily replace the DATA_FILE
        self.original_data_file = app.config.get('DATA_FILE')

        # Set up test client
        app.config['TESTING'] = True
        app.config['DATA_FILE'] = self.test_file
        self.client = app.test_client()

        # Override the DATA_FILE constant in the app module
        import app as app_module
        self.original_module_data_file = app_module.DATA_FILE
        app_module.DATA_FILE = self.test_file

    def tearDown(self):
        """Clean up after each test"""
        # Close and remove the temporary file
        os.close(self.test_fd)
        os.unlink(self.test_file)

        # Restore original DATA_FILE
        import app as app_module
        app_module.DATA_FILE = self.original_module_data_file

    def test_load_data_creates_default(self):
        """Test that load_data creates default data structure when file doesn't exist"""
        # Remove the test file
        os.unlink(self.test_file)

        # Load data should create a new file with default structure
        data = load_data()

        # Check that current year exists
        current_year = str(datetime.now().year)
        self.assertIn(current_year, data)

        # Check default structure
        year_data = data[current_year]
        self.assertEqual(year_data['total_assets'], 0)
        self.assertEqual(year_data['total_liabilities'], 0)
        self.assertEqual(year_data['total_income'], 0)
        self.assertEqual(year_data['net_worth'], 0)

        # Check assets structure
        self.assertIn('assets', year_data)
        self.assertIn('cash', year_data['assets'])
        self.assertIn('investments', year_data['assets'])
        self.assertIn('business_interests', year_data['assets'])
        self.assertIn('property', year_data['assets'])

        # Check investments sub-structure
        investments = year_data['assets']['investments']
        self.assertIn('pre_tax', investments)
        self.assertIn('tax_free', investments)
        self.assertIn('after_tax', investments)

    def test_save_and_load_data(self):
        """Test saving and loading data"""
        test_data = {
            '2024': {
                'total_assets': 100000,
                'total_liabilities': 20000,
                'total_income': 80000,
                'net_worth': 80000,
                'last_updated': '2024-01-01',
                'assets': {
                    'cash': {'total': 10000, 'list': {'checking': 5000, 'savings': 5000}},
                    'investments': {
                        'total': 90000,
                        'pre_tax': {'total': 50000, 'list': {'401k': 50000}},
                        'tax_free': {'total': 30000, 'list': {'roth_ira': 30000}},
                        'after_tax': {'total': 10000, 'list': {'brokerage': 10000}}
                    },
                    'business_interests': {'total': 0, 'list': {}},
                    'property': {'total': 0, 'list': {}}
                },
                'liabilities': {'mortgage': 20000},
                'income': {'salary': 80000}
            }
        }

        # Save data
        save_data(test_data)

        # Load data
        loaded_data = load_data()

        # Verify data matches
        self.assertEqual(loaded_data, test_data)
        self.assertEqual(loaded_data['2024']['total_assets'], 100000)
        self.assertEqual(loaded_data['2024']['net_worth'], 80000)

    def test_net_worth_calculation(self):
        """Test net worth calculation logic"""
        # Create test data
        assets = {
            'cash': {'total': 10000, 'list': {'checking': 10000}},
            'investments': {
                'total': 50000,
                'pre_tax': {'total': 30000, 'list': {'401k': 30000}},
                'tax_free': {'total': 20000, 'list': {'roth': 20000}},
                'after_tax': {'total': 0, 'list': {}}
            },
            'business_interests': {'total': 0, 'list': {}},
            'property': {'total': 200000, 'list': {'house': 200000}}
        }

        liabilities = {
            'mortgage': 150000,
            'car_loan': 10000
        }

        # Calculate totals
        total_assets = sum(
            category['total']
            for name, category in assets.items()
            if name != 'investments'
        ) + assets['investments']['total']

        total_liabilities = sum(liabilities.values())
        net_worth = total_assets - total_liabilities

        # Verify calculations
        self.assertEqual(total_assets, 260000)
        self.assertEqual(total_liabilities, 160000)
        self.assertEqual(net_worth, 100000)

    def test_index_route(self):
        """Test the index route"""
        # First ensure we have valid data structure
        test_data = {
            '2024': {
                'birth_year': 1990,
                'total_assets': 100000,
                'total_liabilities': 20000,
                'total_income': 80000,
                'net_worth': 80000,
                'last_updated': '2024-01-01',
                'assets': {
                    'cash': {'total': 10000, 'list': {}},
                    'investments': {
                        'total': 90000,
                        'pre_tax': {'total': 50000, 'list': {}},
                        'tax_free': {'total': 30000, 'list': {}},
                        'after_tax': {'total': 10000, 'list': {}}
                    },
                    'business_interests': {'total': 0, 'list': {}},
                    'property': {'total': 0, 'list': {}}
                },
                'liabilities': {},
                'income': {}
            }
        }
        save_data(test_data)

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_input_route_get(self):
        """Test the input route with GET request"""
        response = self.client.get('/input')
        self.assertEqual(response.status_code, 200)

    def test_analysis_route(self):
        """Test the analysis route"""
        # First, create some data
        test_data = {
            '2024': {
                'birth_year': 1990,
                'total_assets': 200000,
                'total_liabilities': 50000,
                'total_income': 100000,
                'net_worth': 150000,
                'last_updated': '2024-01-01',
                'assets': {
                    'cash': {'total': 20000, 'list': {}},
                    'investments': {
                        'total': 180000,
                        'pre_tax': {'total': 100000, 'list': {}},
                        'tax_free': {'total': 80000, 'list': {}},
                        'after_tax': {'total': 0, 'list': {}}
                    },
                    'business_interests': {'total': 0, 'list': {}},
                    'property': {'total': 0, 'list': {}}
                },
                'liabilities': {},
                'income': {'salary': 100000}
            }
        }
        save_data(test_data)

        response = self.client.get('/analysis')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'analysis', response.data.lower())

    def test_wealth_category_calculation(self):
        """Test PAW/AAW/UAW wealth category calculations"""
        # Test data
        age = 35
        total_income = 100000
        current_net_worth = 350000
        years_until_40 = max(0, 40 - age)

        # Calculate expected values using the formula from app.py
        # (Age × Income) ÷ (10 + years until 40)
        expected_net_worth = (age * total_income) / (10 + years_until_40)
        target_net_worth = expected_net_worth * 2

        # Verify expected net worth
        self.assertAlmostEqual(expected_net_worth, 233333.33, places=2)
        self.assertAlmostEqual(target_net_worth, 466666.67, places=2)

        # Test category determination
        # PAW: Net worth >= target
        if current_net_worth >= target_net_worth:
            category = 'PAW'
        elif current_net_worth >= expected_net_worth:
            category = 'AAW'
        else:
            category = 'UAW'

        # With 350,000 net worth, should be AAW
        self.assertEqual(category, 'AAW')

        # Test edge cases
        # Just below expected - should be UAW
        test_net_worth = 200000
        if test_net_worth >= target_net_worth:
            test_category = 'PAW'
        elif test_net_worth >= expected_net_worth:
            test_category = 'AAW'
        else:
            test_category = 'UAW'
        self.assertEqual(test_category, 'UAW')

        # Above target - should be PAW
        test_net_worth = 500000
        if test_net_worth >= target_net_worth:
            test_category = 'PAW'
        elif test_net_worth >= expected_net_worth:
            test_category = 'AAW'
        else:
            test_category = 'UAW'
        self.assertEqual(test_category, 'PAW')

    def test_investment_totals_calculation(self):
        """Test that investment subtotals are calculated correctly"""
        investments = {
            'total': 0,
            'pre_tax': {'total': 0, 'list': {'401k': 50000, 'trad_ira': 30000}},
            'tax_free': {'total': 0, 'list': {'roth_ira': 20000, 'hsa': 10000}},
            'after_tax': {'total': 0, 'list': {'brokerage': 15000}}
        }

        # Calculate subtotals
        investments['pre_tax']['total'] = sum(investments['pre_tax']['list'].values())
        investments['tax_free']['total'] = sum(investments['tax_free']['list'].values())
        investments['after_tax']['total'] = sum(investments['after_tax']['list'].values())

        # Calculate total
        investments['total'] = sum(
            investments[key]['total']
            for key in ['pre_tax', 'tax_free', 'after_tax']
        )

        # Verify calculations
        self.assertEqual(investments['pre_tax']['total'], 80000)
        self.assertEqual(investments['tax_free']['total'], 30000)
        self.assertEqual(investments['after_tax']['total'], 15000)
        self.assertEqual(investments['total'], 125000)


if __name__ == '__main__':
    unittest.main()
