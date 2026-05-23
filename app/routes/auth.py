from flask import Blueprint, render_template, request, redirect, url_for, session

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(request.args.get('next') or url_for('index'))

    if request.method == 'POST':
        from app.services.auth_service import AuthService
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        next_url = request.form.get('next', '') or request.args.get('next', '')

        try:
            user = AuthService.verify_password(email, password)
            session['user_id'] = user.get('uid') or user.get('id', '')
            session['email'] = user.get('email', email)
            session['role'] = user.get('role', 'guest')
            session['name'] = user.get('name', '')
            session.permanent = True
            return redirect(next_url or url_for('index'))
        except ValueError as e:
            return render_template('auth/login.html', error=str(e),
                                   next=next_url, email=email)

    return render_template('auth/login.html', next=request.args.get('next', ''))


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        from app.services.auth_service import AuthService
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        name = request.form.get('name', '').strip()
        role = request.form.get('role', 'guest')

        if len(password) < 6:
            return render_template('auth/register.html',
                                   error='Password must be at least 6 characters.',
                                   email=email, name=name)

        result = AuthService.register(email, password, {'name': name, 'role': role})
        if isinstance(result, dict) and 'error' in result:
            return render_template('auth/register.html', error=result['error'],
                                   email=email, name=name)

        session['user_id'] = result.uid
        session['email'] = result.email
        session['role'] = role
        session['name'] = name
        session.permanent = True
        return redirect(url_for('index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    from app.services.auth_service import AuthService
    AuthService.logout()
    return redirect(url_for('index'))
