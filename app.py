from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'

@app.route('/', methods=['GET'])
def index():
    net_worth_history = session.get('net_worth_history', {})
    
    if not net_worth_history:
        current_year = str(datetime.now().year)
        net_worth_history = {
            current_year: {
                'total_assets': 0,
                'total_liabilities': 0,
                'total_income': 0,
                'net_worth': 0,
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'assets': {},
                'liabilities': {},
                'income': {}
            }
        }
        session['net_worth_history'] = net_worth_history
    
    # Ensure all years have the income field
    for year in net_worth_history:
        if 'income' not in net_worth_history[year]:
            net_worth_history[year]['income'] = {}
        if 'total_income' not in net_worth_history[year]:
            net_worth_history[year]['total_income'] = 0
    
    session['net_worth_history'] = net_worth_history
    print(net_worth_history)
    return render_template('index.html', data=net_worth_history)

@app.route('/input/<year>', methods=['GET', 'POST'])
@app.route('/input', defaults={'year': None}, methods=['GET', 'POST'])
def input_page(year):
    net_worth_history = session.get('net_worth_history', {})
    current_year = str(datetime.now().year)
    
    if year is None:
        year = current_year
    
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
                        'assets': {},
                        'liabilities': {},
                        'income': {}
                    }
                    session['net_worth_history'] = net_worth_history
                return redirect(url_for('input_page', year=new_year))
            return redirect(url_for('input_page', year=year))
        
        # Handle form submission
        assets = {}
        liabilities = {}
        income = {}
        
        # Process all form fields
        for key, value in request.form.items():
            if key.startswith('asset_'):
                asset_name = key.replace('asset_', '')
                assets[asset_name] = float(value or 0)
            elif key.startswith('liability_'):
                liability_name = key.replace('liability_', '')
                liabilities[liability_name] = float(value or 0)
            elif key.startswith('income_'):
                income_name = key.replace('income_', '')
                income[income_name] = float(value or 0)
        
        total_assets = sum(assets.values())
        total_liabilities = sum(liabilities.values())
        total_income = sum(income.values())
        net_worth = total_assets - total_liabilities
        
        net_worth_history[year] = {
            'total_assets': total_assets,
            'total_liabilities': total_liabilities,
            'total_income': total_income,
            'net_worth': net_worth,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'assets': assets,
            'liabilities': liabilities,
            'income': income
        }
        
        session['net_worth_history'] = net_worth_history
        return redirect(url_for('index'))
    
    years = sorted(list(net_worth_history.keys()), reverse=True)
    
    # Update the default structure for new years
    default_data = {
        'total_assets': 0,
        'total_liabilities': 0,
        'total_income': 0,
        'net_worth': 0,
        'last_updated': datetime.now().strftime('%Y-%m-%d'),
        'assets': {},
        'liabilities': {},
        'income': {}
    }
    
    year_data = net_worth_history.get(year, default_data)
    
    # Ensure the year data has all required fields
    if 'income' not in year_data:
        year_data['income'] = {}
    if 'total_income' not in year_data:
        year_data['total_income'] = 0
    
    return render_template('input.html', 
                         years=years, 
                         current_year=year,
                         data=year_data,
                         min_year=1900,
                         max_year=int(current_year))

# Add a new route to handle year deletion
@app.route('/delete_year/<year>', methods=['POST'])
def delete_year(year):
    net_worth_history = session.get('net_worth_history', {})
    if year in net_worth_history:
        del net_worth_history[year]
        session['net_worth_history'] = net_worth_history
    return redirect(url_for('input_page'))

if __name__ == '__main__':
    app.run(debug=True) 