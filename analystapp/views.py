import os
import pandas as pd
import numpy as np
import joblib

from word2number import w2n

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor
)

from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression
)

from .models import LoginData


import os
import random
import pandas as pd
import numpy as np
import joblib

from word2number import w2n

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.core.mail import send_mail

from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import (
    RandomForestClassifier,
    RandomForestRegressor
)

from sklearn.linear_model import (
    LogisticRegression,
    LinearRegression
)

from .models import LoginData


# =========================================
# SIGNUP
# =========================================

def signup(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # USERNAME CHECK

        if LoginData.objects.filter(
            username=username
        ).exists():

            return render(
                request,
                'analystapp/signup.html',
                {
                    'error': 'Username already exists'
                }
            )

        # EMAIL CHECK

        if LoginData.objects.filter(
            email=email
        ).exists():

            return render(
                request,
                'analystapp/signup.html',
                {
                    'error': 'Email already exists'
                }
            )

        # CREATE USER

        LoginData.objects.create(
            username=username,
            email=email,
            password=password
        )

        return redirect('login')

    return render(
        request,
        'analystapp/signup.html'
    )


# =========================================
# LOGIN
# =========================================

def login_view(request):

    if request.method == "POST":

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = LoginData.objects.filter(
            username=username,
            password=password
        )

        if user.exists():

            request.session['username'] = username

            return redirect('home')

        return render(
            request,
            'analystapp/login.html',
            {
                'error': 'Invalid Username or Password'
            }
        )

    return render(
        request,
        'analystapp/login.html'
    )


# =========================================
# LOGOUT
# =========================================

def logout_view(request):

    request.session.flush()

    return redirect('login')


# =========================================
# HOME
# =========================================

def home(request):

    username = request.session.get('username')

    return render(
        request,
        'analystapp/home.html',
        {
            'username': username
        }
    )


# =========================================
# FORGOT PASSWORD
# =========================================

# =========================================
# FORGOT PASSWORD
# =========================================

def forgot_password(request):

    if request.method == "POST":

        username = request.POST.get('username')
        email = request.POST.get('email')

        # CHECK USERNAME + EMAIL MATCH

        user = LoginData.objects.filter(
            username=username,
            email=email
        ).first()

        if user:

            otp = random.randint(100000, 999999)

            request.session['otp'] = str(otp)

            request.session['reset_email'] = email

            send_mail(
                subject='Password Reset OTP',

                message=f'''
Hello {username},

Your OTP for password reset is:

{otp}

Do not share this OTP with anyone.
                ''',

                from_email=settings.EMAIL_HOST_USER,

                recipient_list=[email],

                fail_silently=False
            )

            return redirect('verify_otp')

        return render(
            request,
            'analystapp/forgot_password.html',
            {
                'error': 'Username and Email do not match'
            }
        )

    return render(
        request,
        'analystapp/forgot_password.html'
    )
# =========================================
# VERIFY OTP
# =========================================

def verify_otp(request):

    if request.method == "POST":

        entered_otp = request.POST.get('otp')

        session_otp = request.session.get('otp')

        if entered_otp == session_otp:

            return redirect('change_password')

        return render(
            request,
            'analystapp/verify_otp.html',
            {
                'error': 'Invalid OTP'
            }
        )

    return render(
        request,
        'analystapp/verify_otp.html'
    )


# =========================================
# CHANGE PASSWORD
# =========================================

def change_password(request):

    if request.method == "POST":

        new_password = request.POST.get(
            'new_password'
        )

        email = request.session.get(
            'reset_email'
        )

        user = LoginData.objects.get(
            email=email
        )

        user.password = new_password
        user.save()

        request.session.flush()

        return redirect('login')

    return render(
        request,
        'analystapp/change_password.html'
    )

def clean_data(request):

    if request.method == "POST":

        try:

            file = request.FILES['dataset']

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            file_path = os.path.join(
                settings.MEDIA_ROOT,
                file.name
            )

            with open(file_path, 'wb+') as f:

                for chunk in file.chunks():
                    f.write(chunk)

            # READ FILE

            if file.name.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            # REMOVE DUPLICATES

            df = df.drop_duplicates()

            # FILL NULL VALUES

            for col in df.columns:

                if df[col].dtype == 'object':

                    df[col] = df[col].fillna("Unknown")

                else:

                    df[col] = df[col].fillna(0)

            # CONVERT NUMBER WORDS TO NUMBERS

            def convert_words(value):

                try:

                    return w2n.word_to_num(str(value))

                except:

                    return value

            df = df.apply(lambda col: col.map(convert_words))

            # SAVE CLEAN FILE

            cleaned_path = os.path.join(
                settings.MEDIA_ROOT,
                'cleaned_data.xlsx'
            )

            df.to_excel(cleaned_path, index=False)

            response = HttpResponse(
                open(cleaned_path, 'rb').read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

            response['Content-Disposition'] = (
                'attachment; filename=cleaned_data.xlsx'
            )

            return response

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    return render(request, 'analystapp/clean.html')


# =========================================
# VISUALIZATION
# =========================================

def visualize(request):

    # =====================================
    # STEP 1 : UPLOAD DATASET
    # =====================================

    if request.method == "POST" and 'upload' in request.POST:

        try:

            file = request.FILES['dataset']

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            file_path = os.path.join(
                settings.MEDIA_ROOT,
                file.name
            )

            with open(file_path, 'wb+') as f:

                for chunk in file.chunks():
                    f.write(chunk)

            # READ FILE

            if file.name.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            return render(
                request,
                'analystapp/visualize.html',
                {
                    'columns': df.columns.tolist(),
                    'file_path': file_path,
                    'ask_chart_count': True
                }
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    # =====================================
    # STEP 2 : CHART COUNT
    # =====================================

    if request.method == "POST" and 'create' in request.POST:

        try:

            chart_count = int(
                request.POST.get('chart_count')
            )

            file_path = request.POST.get('file_path')

            if file_path.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            return render(
                request,
                'analystapp/visualize.html',
                {
                    'chart_range': range(chart_count),
                    'columns': df.columns.tolist(),
                    'chart_count': chart_count,
                    'file_path': file_path
                }
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    # =====================================
    # STEP 3 : GENERATE CHARTS
    # =====================================

    if request.method == "POST" and 'generate' in request.POST:

        try:

            file_path = request.POST.get('file_path')

            chart_count = int(
                request.POST.get('chart_count')
            )

            if file_path.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            charts = []

            for i in range(chart_count):

                chart_type = request.POST.get(
                    f'chart_type{i}'
                )

                x = request.POST.get(f'x{i}')

                y = request.POST.get(f'y{i}')

                plt.figure(figsize=(7, 5))

                # BAR

                if chart_type == 'bar':

                    plt.bar(
                        df[x].astype(str),
                        pd.to_numeric(
                            df[y],
                            errors='coerce'
                        ).fillna(0)
                    )

                # LINE

                elif chart_type == 'line':

                    plt.plot(
                        df[x],
                        pd.to_numeric(
                            df[y],
                            errors='coerce'
                        ).fillna(0)
                    )

                # SCATTER

                elif chart_type == 'scatter':

                    plt.scatter(
                        pd.to_numeric(
                            df[x],
                            errors='coerce'
                        ).fillna(0),

                        pd.to_numeric(
                            df[y],
                            errors='coerce'
                        ).fillna(0)
                    )

                # PIE

                elif chart_type == 'pie':

                    pie_values = pd.to_numeric(
                        df[y],
                        errors='coerce'
                    ).fillna(0)

                    plt.pie(
                        pie_values,
                        labels=df[x].astype(str),
                        autopct='%1.1f%%'
                    )

                # HISTOGRAM

                elif chart_type == 'hist':

                    plt.hist(
                        pd.to_numeric(
                            df[x],
                            errors='coerce'
                        ).fillna(0)
                    )

                plt.xlabel(x)
                plt.ylabel(y)
                plt.title(f"{chart_type.upper()} CHART")

                chart_name = f'chart_{i}.png'

                chart_path = os.path.join(
                    settings.MEDIA_ROOT,
                    chart_name
                )

                plt.savefig(chart_path)

                plt.close()

                charts.append(
                    '/media/' + chart_name
                )

            return render(
                request,
                'analystapp/result.html',
                {'charts': charts}
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    return render(request, 'analystapp/visualize.html')


# =========================================
# PREDICTION
# =========================================

def predict_page(request):

    # =====================================
    # STEP 1 : UPLOAD FILE
    # =====================================

    if request.method == "POST" and 'upload' in request.POST:

        try:

            file = request.FILES['dataset']

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

            file_path = os.path.join(
                settings.MEDIA_ROOT,
                file.name
            )

            with open(file_path, 'wb+') as f:

                for chunk in file.chunks():
                    f.write(chunk)

            # READ FILE

            if file.name.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            return render(
                request,
                'analystapp/predict.html',
                {
                    'columns': df.columns.tolist(),
                    'file_path': file_path
                }
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    # =====================================
    # STEP 2 : TRAIN MODEL
    # =====================================

    if request.method == "POST" and 'train_model' in request.POST:

        try:

            file_path = request.POST.get('file_path')

            target = request.POST.get('target')

            model_name = request.POST.get('model')

            if file_path.endswith('.csv'):

                df = pd.read_csv(file_path)

            else:

                df = pd.read_excel(file_path)

            df = df.dropna()

            # REMOVE ID COLUMNS

            remove_cols = []

            for col in df.columns:

                if 'id' in col.lower():

                    remove_cols.append(col)

            df = df.drop(columns=remove_cols)

            # FEATURES + TARGET

            X = df.drop(columns=[target])

            y = df[target]

            # IMPORTANT COLUMNS ONLY

            important_columns = X.columns[:4]

            X = X[important_columns]

            encoders = {}

            # ENCODE FEATURES

            for col in X.columns:

                le = LabelEncoder()

                X[col] = le.fit_transform(
                    X[col].astype(str)
                )

                encoders[col] = le

            # ENCODE TARGET

            target_encoder = LabelEncoder()

            y = target_encoder.fit_transform(
                y.astype(str)
            )

            # MODEL SELECTION

            if model_name == 'logistic':

                model = LogisticRegression(
                    max_iter=1000
                )

            elif model_name == 'linear':

                model = LinearRegression()

            else:

                if len(np.unique(y)) < 10:

                    model = RandomForestClassifier()

                else:

                    model = RandomForestRegressor()

            # TRAIN MODEL

            model.fit(X, y)

            # SAVE MODEL

            model_path = os.path.join(
                settings.MEDIA_ROOT,
                'model.pkl'
            )

            joblib.dump(model, model_path)

            # SAVE ENCODERS

            encoder_path = os.path.join(
                settings.MEDIA_ROOT,
                'encoders.pkl'
            )

            joblib.dump(
                {
                    'encoders': encoders,
                    'target_encoder': target_encoder
                },
                encoder_path
            )

            # SAVE SESSION

            request.session['columns'] = (
                important_columns.tolist()
            )

            return render(
                request,
                'analystapp/predict.html',
                {
                    'show_predict_form': True,
                    'columns': important_columns
                }
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    # =====================================
    # STEP 3 : PREDICT
    # =====================================

    if request.method == "POST" and 'predict' in request.POST:

        try:

            columns = request.session.get('columns')

            model_path = os.path.join(
                settings.MEDIA_ROOT,
                'model.pkl'
            )

            encoder_path = os.path.join(
                settings.MEDIA_ROOT,
                'encoders.pkl'
            )

            model = joblib.load(model_path)

            encoder_data = joblib.load(
                encoder_path
            )

            encoders = encoder_data['encoders']

            target_encoder = (
                encoder_data['target_encoder']
            )

            values = []

            for col in columns:

                value = request.POST.get(col)

                # TRANSFORM USING ENCODER

                if col in encoders:

                    try:

                        value = encoders[col].transform(
                            [str(value)]
                        )[0]

                    except:

                        value = 0

                else:

                    value = float(value)

                values.append(value)

            final_input = np.array(values).reshape(1, -1)

            prediction = model.predict(
                final_input
            )[0]

            # DECODE PREDICTION

            try:

                prediction = (
                    target_encoder.inverse_transform(
                        [int(prediction)]
                    )[0]
                )

            except:

                pass

            return render(
                request,
                'analystapp/predict.html',
                {
                    'prediction': prediction,
                    'show_predict_form': True,
                    'columns': columns
                }
            )

        except Exception as e:

            return HttpResponse(f"ERROR : {e}")

    return render(request, 'analystapp/predict.html')