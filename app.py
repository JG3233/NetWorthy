from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime
import os
from dotenv import load_dotenv
from models import db, NetWorthYear

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL',
    'postgresql://networthy:networthy@localhost:5432/networthy'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)


def init_db():
    """Initialize database with tables"""
    with app.app_context():
        db.create_all()
        # Create current year if no data exists
        if NetWorthYear.query.count() == 0:
            current_year = datetime.now().year
            year_data = NetWorthYear(current_year, birth_year=1990)
            db.session.add(year_data)
            db.session.commit()


def get_all_data_as_dict():
    """Get all years data as dictionary (matching old JSON format)"""
    years = NetWorthYear.query.all()
    return {str(year.year): year.to_dict() for year in years}


@app.route('/', methods=['GET'])
def index():
    net_worth_history = get_all_data_as_dict()

    # Ensure all years have the income field
    for year in net_worth_history:
        if 'income' not in net_worth_history[year]:
            net_worth_history[year]['income'] = {}
        if 'total_income' not in net_worth_history[year]:
            net_worth_history[year]['total_income'] = 0

    print(net_worth_history)
    return render_template('index.html', data=net_worth_history)


@app.route('/input', methods=['GET', 'POST'])
def input_page():
    current_year = datetime.now().year

    # Get all years
    all_years = NetWorthYear.query.order_by(NetWorthYear.year.desc()).all()
    years = [str(year.year) for year in all_years]

    # Get selected year from query parameter or use latest year
    selected_year = request.args.get('year', years[0] if years else str(current_year))

    if request.method == 'POST':
        if 'new_year' in request.form:
            new_year = request.form.get('new_year')
            if new_year and new_year.isdigit() and len(new_year) == 4:
                new_year_int = int(new_year)
                # Check if year already exists
                existing_year = NetWorthYear.query.filter_by(year=new_year_int).first()
                if not existing_year:
                    new_year_data = NetWorthYear(new_year_int)
                    db.session.add(new_year_data)
                    db.session.commit()
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

        # Process all form fields (same logic as before)
        for key, value in request.form.items():
            if not value.strip():
                continue

            try:
                value = float(value)
            except (ValueError, AttributeError):
                continue

            if key.startswith('asset_'):
                parts = key.split('_')
                if len(parts) < 3:
                    continue

                category = parts[1]
                if category == 'cash' or category == 'business' or category == 'property':
                    name = '_'.join(parts[2:])
                    if category == 'business':
                        category = 'business_interests'
                        name = '_'.join(parts[3:])
                    if name.endswith('_name'):
                        continue
                    print(f"Processing {category}: {name} = {value}")
                    clean_name = name.replace('_name', '')
                    if category not in assets:
                        assets[category] = {'total': 0, 'list': {}}
                    assets[category]['list'][clean_name] = value
                    assets[category]['total'] = sum(assets[category]['list'].values())
                    print(f"Updated {category} structure:", assets[category])
                elif category == 'investments':
                    if len(parts) < 4:
                        continue
                    inv_type = parts[2]
                    name = '_'.join(parts[4:])
                    if name.endswith('_name'):
                        continue

                    if inv_type == 'after':
                        inv_type = 'after_tax'
                    elif inv_type == 'pre':
                        inv_type = 'pre_tax'
                    elif inv_type == 'tax':
                        inv_type = 'tax_free'

                    if inv_type not in assets['investments']:
                        assets['investments'][inv_type] = {'total': 0, 'list': {}}

                    assets['investments'][inv_type]['list'][name] = value
                    assets['investments'][inv_type]['total'] = sum(
                        assets['investments'][inv_type]['list'].values()
                    )
                    assets['investments']['total'] = sum(
                        assets['investments'][key]['total']
                        for key in ['pre_tax', 'tax_free', 'after_tax']
                    )

            elif key.startswith('liabilities_'):
                liability_name = key.replace('liabilities_', '')
                if liability_name.endswith('_name'):
                    continue
                liabilities[liability_name] = value
            elif key.startswith('income_'):
                income_name = key.replace('income_', '')
                if income_name.endswith('_name'):
                    continue
                income[income_name] = value

        # Debug prints
        print("Processed assets:", assets)
        print("Processed liabilities:", liabilities)
        print("Processed income:", income)

        # Calculate totals
        total_assets = sum(
            category['total']
            for name, category in assets.items()
            if name != 'investments'
        ) + assets['investments']['total']
        total_liabilities = sum(liabilities.values())
        total_income = sum(income.values())
        net_worth = total_assets - total_liabilities

        # Update database
        selected_year_int = int(selected_year)
        year_record = NetWorthYear.query.filter_by(year=selected_year_int).first()

        if not year_record:
            year_record = NetWorthYear(selected_year_int)
            db.session.add(year_record)

        year_record.total_assets = total_assets
        year_record.total_liabilities = total_liabilities
        year_record.total_income = total_income
        year_record.net_worth = net_worth
        year_record.last_updated = datetime.now().strftime('%Y-%m-%d')
        year_record.assets = assets
        year_record.liabilities = liabilities
        year_record.income = income

        db.session.commit()

        print("Updated database")

        return redirect(url_for('index'))

    # Get year data
    selected_year_int = int(selected_year)
    year_record = NetWorthYear.query.filter_by(year=selected_year_int).first()

    if year_record:
        year_data = year_record.to_dict()
    else:
        # Create default data
        year_data = {
            'total_assets': 0,
            'total_liabilities': 0,
            'total_income': 0,
            'net_worth': 0,
            'last_updated': datetime.now().strftime('%Y-%m-%d'),
            'assets': NetWorthYear._get_default_assets(),
            'liabilities': {},
            'income': {}
        }

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
    year_int = int(year)
    year_record = NetWorthYear.query.filter_by(year=year_int).first()

    if year_record:
        db.session.delete(year_record)
        db.session.commit()

        # If we deleted the last year, create a new current year
        if NetWorthYear.query.count() == 0:
            current_year = datetime.now().year
            new_year_data = NetWorthYear(current_year)
            db.session.add(new_year_data)
            db.session.commit()
            return redirect(url_for('input_page'))

        # Redirect to input page with the most recent year
        latest_year_record = NetWorthYear.query.order_by(NetWorthYear.year.desc()).first()
        return redirect(url_for('input_page', year=str(latest_year_record.year)))

    return redirect(url_for('input_page'))


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    # Get latest year
    latest_year_record = NetWorthYear.query.order_by(NetWorthYear.year.desc()).first()

    if not latest_year_record:
        # Create default year if none exists
        current_year = datetime.now().year
        latest_year_record = NetWorthYear(current_year)
        db.session.add(latest_year_record)
        db.session.commit()

    latest_data = latest_year_record.to_dict()

    # Handle birth year form submission
    if request.method == 'POST':
        birth_year = request.form.get('birth_year')
        if birth_year and birth_year.isdigit():
            birth_year = int(birth_year)
            current_year = datetime.now().year
            # Validate birth year is reasonable
            if 1900 <= birth_year <= current_year:
                # Update birth_year in all years
                all_years = NetWorthYear.query.all()
                for year_record in all_years:
                    year_record.birth_year = birth_year
                db.session.commit()
                latest_data['birth_year'] = birth_year

    # Get birth_year from data or use default
    birth_year = latest_data.get('birth_year', 1990)
    current_year = datetime.now().year
    age = current_year - birth_year

    # Calculate 3-year average income
    recent_years = NetWorthYear.query.order_by(NetWorthYear.year.desc()).limit(3).all()
    income_values = []
    for year_record in recent_years:
        year_income = year_record.total_income
        if year_income > 0:
            income_values.append(year_income)

    # Calculate average income
    if income_values:
        total_income = sum(income_values) / len(income_values)
    else:
        total_income = latest_data.get('total_income', 0)

    # Add safety check for zero income
    if total_income <= 0:
        total_income = 1

    # Calculate years until 40
    years_until_40 = max(0, 40 - age)

    # Calculate MND metrics
    total_assets = latest_data.get('total_assets', 0)
    total_liabilities = latest_data.get('total_liabilities', 0)
    net_worth = total_assets - total_liabilities

    # Formula: (Age × Income) ÷ (10 + years until 40)
    expected_net_worth = (age * total_income) / (10 + years_until_40)
    target_net_worth = expected_net_worth * 2

    expected_net_worth = max(expected_net_worth, 1)
    target_net_worth = max(target_net_worth, 1)

    # Thresholds
    paw_threshold = target_net_worth
    aaw_min = expected_net_worth
    aaw_max = target_net_worth
    uaw_threshold = expected_net_worth

    current_net_worth = net_worth

    # Determine category
    if current_net_worth >= paw_threshold:
        category = 'PAW'
    elif current_net_worth >= aaw_min:
        category = 'AAW'
    else:
        category = 'UAW'

    return render_template('analysis.html',
                         age=age,
                         birth_year=birth_year,
                         total_income=total_income,
                         income_values=income_values,
                         current_net_worth=current_net_worth,
                         expected_net_worth=expected_net_worth,
                         paw_threshold=paw_threshold,
                         aaw_min=aaw_min,
                         aaw_max=aaw_max,
                         uaw_threshold=uaw_threshold,
                         category=category,
                         years_until_40=years_until_40,
                         min_birth_year=1900,
                         max_birth_year=current_year)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0')
