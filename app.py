from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)

# File path for storing data
DATA_FILE = 'net_worth_history.json'

def load_data():
    """Load data from JSON file, create if doesn't exist"""
    if not os.path.exists(DATA_FILE):
        current_year = str(datetime.now().year)
        default_data = {
            current_year: {
                'total_assets': 0,
                'total_liabilities': 0,
                'total_income': 0,
                'net_worth': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'assets': {
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
                },
                'liabilities': {},
                'income': {}
            }
        }
        save_data(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # If file is corrupted, return empty data
        return {}

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/', methods=['GET'])
def index():
    net_worth_history = load_data()
    
    # Ensure all years have the income field
    for year in net_worth_history:
        if 'income' not in net_worth_history[year]:
            net_worth_history[year]['income'] = {}
        if 'total_income' not in net_worth_history[year]:
            net_worth_history[year]['total_income'] = 0
    
    save_data(net_worth_history)
    print(net_worth_history)
    return render_template('index.html', data=net_worth_history)

@app.route('/input', methods=['GET', 'POST'])
def input_page():
    net_worth_history = load_data()
    current_year = str(datetime.now().year)
    
    # Get selected year from query parameter or use latest year
    years = sorted(list(net_worth_history.keys()), reverse=True)
    selected_year = request.args.get('year', years[0] if years else current_year)
    
    if request.method == 'POST':
        if 'new_year' in request.form:
            new_year = request.form.get('new_year')
            if new_year and new_year.isdigit() and len(new_year) == 4:
                # Initialize the new year with default structure if it doesn't exist
                if new_year not in net_worth_history:
                    net_worth_history[new_year] = {
                        'total_assets': 0,
                        'total_liabilities': 0,
                        'total_income': 0,
                        'net_worth': 0,
                        'last_updated': datetime.now().strftime('%Y-%m-%d'),
                        'assets': {
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
                        },
                        'liabilities': {},
                        'income': {}
                    }
                    save_data(net_worth_history)
                return redirect(url_for('input_page', year=new_year))
            return redirect(url_for('input_page', year=selected_year))
        
        print("Form data received:", dict(request.form))
        
        # Handle form submission
        assets = {
            'cash': {'total': 0, 'list': {}},
            'investments': {
                'total': 0,
                'pre_tax': {'total': 0, 'list': {}},
                'tax_free': {'total': 0, 'list': {}},
                'after_tax': {'total': 0, 'list': {}}
            },
            'business_interests': {'total': 0, 'list': {}},
            'property': {'total': 0, 'list': {}}
        }
        liabilities = {}
        income = {}
        
        # Process all form fields
        for key, value in request.form.items():
            if not value.strip():
                continue
                
            try:
                value = float(value)
            except (ValueError, AttributeError):
                continue

            if key.startswith('asset_'):
                # Parse the asset hierarchy from the form field name
                # Format expected: asset_category_subcategory_name
                # Example: asset_investments_pre_tax_401k
                parts = key.split('_')
                if len(parts) < 3:
                    continue
                
                category = parts[1]
                if category == 'cash' or category == 'business' or category == 'property':
                    name = '_'.join(parts[2:])
                    if category == 'business':
                        category = 'business_interests'
                        name = '_'.join(parts[3:])
                    if name.endswith('_name'):  # Skip the name fields
                        continue
                    print(f"Processing {category}: {name} = {value}")  # Debug print
                    # Fix: Ensure we're using the correct name without _name suffix
                    clean_name = name.replace('_name', '')
                    # Ensure the category exists in the structure
                    if category not in assets:
                        assets[category] = {'total': 0, 'list': {}}
                    # Add the value to the list
                    assets[category]['list'][clean_name] = value
                    # Update the category total
                    assets[category]['total'] = sum(assets[category]['list'].values())
                    print(f"Updated {category} structure:", assets[category])  # Debug print
                elif category == 'investments':
                    if len(parts) < 4:
                        continue
                    inv_type = parts[2]  # pre_tax, tax_free, or after_tax
                    name = '_'.join(parts[4:])
                    if name.endswith('_name'):  # Skip the name fields
                        continue
                    
                    # Map 'after' to 'after_tax' if needed
                    if inv_type == 'after':
                        inv_type = 'after_tax'
                    elif inv_type == 'pre':
                        inv_type = 'pre_tax'
                    elif inv_type == 'tax':
                        inv_type = 'tax_free'
                    
                    # Ensure the investment type exists in the structure
                    if inv_type not in assets['investments']:
                        assets['investments'][inv_type] = {'total': 0, 'list': {}}
                    
                    # Add the value to the list
                    assets['investments'][inv_type]['list'][name] = value
                    # Update the subcategory total
                    assets['investments'][inv_type]['total'] = sum(
                        assets['investments'][inv_type]['list'].values()
                    )
                    # Update total investments (excluding the 'total' key itself)
                    assets['investments']['total'] = sum(
                        assets['investments'][key]['total']
                        for key in ['pre_tax', 'tax_free', 'after_tax']
                    )
                    
            elif key.startswith('liabilities_'):
                liability_name = key.replace('liabilities_', '')
                if liability_name.endswith('_name'):  # Skip the name fields
                    continue
                liabilities[liability_name] = value
            elif key.startswith('income_'):
                income_name = key.replace('income_', '')
                if income_name.endswith('_name'):  # Skip the name fields
                    continue
                income[income_name] = value
        
        # Debug prints
        print("Processed assets:", assets)
        print("Processed liabilities:", liabilities)
        print("Processed income:", income)
        
        # Calculate total assets including all subcategories
        total_assets = sum(
            category['total'] 
            for name, category in assets.items() 
            if name != 'investments'  # Exclude investments from this sum
        ) + assets['investments']['total']  # Add investments total once
        total_liabilities = sum(liabilities.values())
        total_income = sum(income.values())
        net_worth = total_assets - total_liabilities
        
        # Update the year data
        net_worth_history[selected_year] = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_income': total_income,
            'net_worth': net_worth,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'assets': assets,
            'liabilities': liabilities,
            'income': income
        }
        
        # Debug print final state
        print("Updated net worth history:", net_worth_history)
        
        save_data(net_worth_history)
        return redirect(url_for('index'))
    
    # Update the default structure for new years
    default_data = {
        'total_assets': 0,
        'total_liabilities': 0,
        'total_income': 0,
        'net_worth': 0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'assets': {
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
        },
        'liabilities': {},
        'income': {}
    }
    
    # Also ensure existing years have the proper structure
    for year in net_worth_history:
        if 'assets' not in net_worth_history[year]:
            net_worth_history[year]['assets'] = default_data['assets']
        else:
            assets = net_worth_history[year]['assets']
            if 'cash' not in assets:
                assets['cash'] = {'total': 0, 'list': {}}
            if 'investments' not in assets:
                assets['investments'] = {
                    'total': 0,
                    'pre_tax': {'total': 0, 'list': {}},
                    'tax_free': {'total': 0, 'list': {}},
                    'after_tax': {'total': 0, 'list': {}}
                }
            if 'business_interests' not in assets:
                assets['business_interests'] = {'total': 0, 'list': {}}
            if 'property' not in assets:
                assets['property'] = {'total': 0, 'list': {}}
    
    year_data = net_worth_history.get(selected_year, default_data)
    
    # Ensure the year data has all required fields
    if 'income' not in year_data:
        year_data['income'] = {}
    if 'total_income' not in year_data:
        year_data['total_income'] = 0
    
    return render_template('input.html', 
                         years=years, 
                         current_year=selected_year,
                         data=year_data,
                         min_year=1900,
                         max_year=int(current_year))

@app.route('/delete_year/<year>', methods=['POST'])
def delete_year(year):
    net_worth_history = load_data()
    if year in net_worth_history:
        del net_worth_history[year]
        save_data(net_worth_history)
        
        # If we deleted the last year, create a new current year
        if not net_worth_history:
            current_year = str(datetime.now().year)
            net_worth_history[current_year] = {
                'total_assets': 0,
                'total_liabilities': 0,
                'total_income': 0,
                'net_worth': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'assets': {
                    'cash': {'total': 0, 'list': {}},
                    'investments': {
                        'total': 0,
                        'pre_tax': {'total': 0, 'list': {}},
                        'tax_free': {'total': 0, 'list': {}},
                        'after_tax': {'total': 0, 'list': {}}
                    },
                    'business_interests': {'total': 0, 'list': {}},
                    'property': {'total': 0, 'list': {}}
                },
                'liabilities': {},
                'income': {}
            }
            save_data(net_worth_history)
            return redirect(url_for('input_page'))
        
        # Redirect to input page with the most recent year
        latest_year = max(net_worth_history.keys())
        return redirect(url_for('input_page', year=latest_year))
    
    # If year doesn't exist, just redirect to input page
    return redirect(url_for('input_page'))

if __name__ == '__main__':
    app.run(debug=True) 