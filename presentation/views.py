from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from datetime import date, timedelta
from controller.consumo_controller import ConsumoController
from controller.imagen import subir_imagen_controller
from controller.fat_secret import reconocer_imagen, procesar_datos_fasecret
from controller.generador_titulo import extraer_nombres_de_fatsecret, generar_titulo_con_openai
from controller.comida import crear_comida
from data.repositories.comida_repository import ComidaRepository
from controller.user_controller import registrar_usuario, obtener_historial_comidas
from controller.login_controller import login_usuario
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

views_bp = Blueprint('views', __name__)

load_dotenv()


@views_bp.route('/')
def index():
    api_url = os.getenv('API_URL')
    usuario = session.get('usuario')
    ultimas_comidas = []
    if usuario:
        try:
            ultimas_comidas = ComidaRepository.traer_ultimas_tres_comidas(
                usuario['id']) or []
        except Exception:
            ultimas_comidas = []
    return render_template('index.html', api_url=api_url, usuario=usuario, ultimas_comidas=ultimas_comidas)


@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']

        try:
            login_usuario(email, contrasena)
            return redirect(url_for('views.index'))
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", 'error')
    return render_template('login.html')


@views_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contrasena = request.form['contrasena']

        resultado = registrar_usuario(nombre, apellido, email, contrasena)

        if resultado['success']:
            flash('Usuario registrado exitosamente. Por favor, inicie sesión.', 'success')
            return redirect(url_for('views.login'))
        else:
            flash(f"Error al registrar usuario: {resultado['error']}", 'error')
            return render_template('register.html')

    return render_template('register.html')


@views_bp.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ninguna imagen"}), 400

    file = request.files['imagen']

    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401

    id_usuario = usuario['id']

    resultado_subida = subir_imagen_controller(file, id_usuario)

    if resultado_subida['success']:
        try:
            reconocimiento = reconocer_imagen(resultado_subida['url'])

            nombres_alimentos = extraer_nombres_de_fatsecret(reconocimiento)
            titulo_atractivo = generar_titulo_con_openai(
                nombres_alimentos, resultado_subida['url'])

            analisis_nutricion = procesar_datos_fasecret(reconocimiento)

            food_db = crear_comida({
                "nombre": titulo_atractivo,
                "descripcion": f"Comida reconocida: {', '.join(nombres_alimentos)}",
                "calorias": analisis_nutricion.get("calorias", 0),
                "grasas": analisis_nutricion.get("grasas", 0),
                "proteinas": analisis_nutricion.get("proteinas", 0),
                "carbohidratos": analisis_nutricion.get("carbohidratos", 0),
                "colesterol": analisis_nutricion.get("colesterol", 0),
                "imagen_url": resultado_subida['url'],
                "usuario_id": id_usuario
            })

            return jsonify({
                "success": True,
                "url": resultado_subida['url'],
                "public_id": resultado_subida['public_id'],
                "message": resultado_subida['message'],
                "titulo_atractivo": titulo_atractivo,
                "alimentos_identificadoos": nombres_alimentos,
                "reconocimiento": reconocimiento,
                "comida_id": food_db.get("comida_id")
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Error al reconocer la imagen: {str(e)}"
            }), 500
    else:
        return jsonify({
            "success": False,
            "error": resultado_subida['error']
        }), 500



@views_bp.route('/historial_comidas', methods=['GET'])
def historial_comidas():
    usuario_sesion = session.get('usuario')
    if not usuario_sesion:
        return redirect(url_for('views.index'))  # usuario no logueado

    try:
        user = obtener_historial_comidas(usuario_sesion["id"])
        # Evitar error si no hay comidas
        comidas = user.comidas if user.comidas else []
        return render_template('historial_comidas.html', usuario=user, comidas=comidas)
    except ValueError as ve:
        return render_template('historial_comidas.html', error=str(ve))


@views_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('views.login'))


@views_bp.route('/obtener-historial-html')
def obtener_historial_html():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401

    try:
        ultimas_comidas = ComidaRepository.traer_ultimas_tres_comidas(
            usuario['id']) or []
        return render_template('partials/historial_partial.html', ultimas_comidas=ultimas_comidas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views_bp.route('/inicializar-historial')
def inicializar_historial():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401

    try:
        # ✅ INICIALIZAR TODO EL HISTORIAL DEL USUARIO
        semanas = ConsumoController.inicializar_consumos_historicos(
            usuario['id'])

        print(f'✅ Historial inicializado: {len(semanas)} semanas procesadas')
        return redirect(url_for('views.index'))

    except Exception as e:
        print(f'❌ Error al inicializar historial: {str(e)}')
        return redirect(url_for('views.index'))


@views_bp.route('/consumos')
def consumos():
    api_url = os.getenv('API_URL')
    usuario = session.get('usuario')

    # cada vez que entramos a consumos que se actualice el consumo semanal
    ConsumoController.actualizar_consumo_semanal(usuario['id'])

    comidas_usuario = ConsumoController.todas_las_comidas(usuario['id'])
    semana = ConsumoController.obtener_consumo_semanal(
        usuario['id'], date.today())
    hoy = ConsumoController.obtener_consumo_diario(usuario['id'], date.today())

    # Convertir semana a dict (es un solo objeto)
    semana_dict = getattr(semana, "__dict__", {})
    semana_dict.pop('_sa_instance_state', None)
    df = pd.DataFrame([semana_dict]) if semana_dict else pd.DataFrame()

    # Convertir hoy a dataframe
    hoy_dict = getattr(hoy, "__dict__", {})
    hoy_dict.pop('_sa_instance_state', None)
    df_hoy = pd.DataFrame([hoy_dict]) if hoy_dict else pd.DataFrame()

    if comidas_usuario:
        comidas_list = []
        for comida in comidas_usuario:
            comida_dict = getattr(comida, "__dict__", {})
            comida_dict.pop('_sa_instance_state', None)
            comidas_list.append(comida_dict)
        comidas_usuario_df = pd.DataFrame(comidas_list)
    else:
        comidas_usuario_df = pd.DataFrame()

    columnas_totales = {
        'calorias_total': 'Calorías (kcal)',
        'proteinas_total': 'Proteínas (g)',
        'carbohidratos_total': 'Carbohidratos (g)',
        'grasas_total': 'Grasas (g)',
        'colesterol_total': 'Colesterol (mg)'
    }

    labels = []
    values = []
    if not df.empty:
        for col, label in columnas_totales.items():
            if col in df.columns:
                labels.append(label)
                values.append(float(df.iloc[0][col] or 0))

    labels_hoy = []
    values_hoy = []
    # Mapeo específico para consumo diario (sin sufijo _total)
    columnas_diarias = {
        'calorias': 'Calorías (kcal)',
        'proteinas': 'Proteínas (g)',
        'carbohidratos': 'Carbohidratos (g)',
        'grasas': 'Grasas (g)',
        'colesterol': 'Colesterol (mg)'
    }
    if not df_hoy.empty:
        for col, label in columnas_diarias.items():
            if col in df_hoy.columns:
                labels_hoy.append(label)
                values_hoy.append(float(df_hoy.iloc[0][col] or 0))

    graphJSON = None
    graphPieJSON = None
    graphHoyJSON = None
    graphLineJSON = None

    if labels and values:
        df_plot = pd.DataFrame({
            'Nutriente': labels,
            'Cantidad': values
        })

        colores_nutrientes = ['#15a349', '#4285f4','#fbbc04', '#ea4335', '#9c27b0']

        # Gráfico de barras
        fig_bar = px.bar(
            df_plot,
            x='Nutriente',
            y='Cantidad',
            title='Consumo de nutrientes la semana',
            color='Nutriente',
            color_discrete_sequence=colores_nutrientes
        )

        fig_bar.update_layout(
            margin=dict(t=40, r=20, b=40, l=40),
            xaxis_title='Nutrientes',
            yaxis_title='Cantidad',
            showlegend=False
        )
        graphJSON = fig_bar.to_json()

        # Grafico torta
        fig_pie = px.pie(
            df_plot,
            values='Cantidad',
            names='Nutriente',
            title='Porcentajes de nutrientes consumido en la semana',
            color='Nutriente',
            color_discrete_sequence=colores_nutrientes,
            hole=0.4
        )

        fig_pie.update_layout(
            margin=dict(t=35, r=0, b=0, l=0)
        )
        graphPieJSON = fig_pie.to_json()

    if labels_hoy and values_hoy:
        df_plot_hoy = pd.DataFrame({
            'Nutriente': labels_hoy,
            'Cantidad': values_hoy
        })

        colores_nutrientes_hoy = ['#ff5733','#33c1ff', '#75ff33', '#ff33d4', '#ffbd33']
        # Gráfico de barras diario
        fig_bar_hoy = px.bar(
            df_plot_hoy,
            x='Nutriente',
            y='Cantidad',
            title='Consumo de nutrientes del día',
            color='Nutriente',
            color_discrete_sequence=colores_nutrientes_hoy
        )

        fig_bar_hoy.update_layout(
            margin=dict(t=40, r=20, b=40, l=40),
            xaxis_title='Nutrientes',
            yaxis_title='Cantidad',
            showlegend=False
        )
        graphHoyJSON = fig_bar_hoy.to_json()

    # Gráfico de líneas: evolución diaria de macros (últimos 30 días)
    if not comidas_usuario_df.empty:
        df_line = comidas_usuario_df.copy()
        df_line['fecha_consumo'] = pd.to_datetime(df_line['fecha_consumo'])
        start_date = pd.to_datetime(date.today() - timedelta(days=29))
        end_date = pd.to_datetime(date.today())
        mask = (df_line['fecha_consumo'] >= start_date) & (df_line['fecha_consumo'] <= end_date)
        df_line = df_line[mask]

        if not df_line.empty:
            df_line['fecha'] = df_line['fecha_consumo'].dt.normalize()
            # Asegurar columnas de macros
            macro_cols = ['calorias', 'proteinas', 'carbohidratos', 'grasas']
            for c in macro_cols:
                if c not in df_line.columns:
                    df_line[c] = 0
            df_line[macro_cols] = df_line[macro_cols].fillna(0)

            agg = df_line.groupby('fecha')[macro_cols].sum().reset_index()
            # Completar fechas faltantes con 0
            full_idx = pd.date_range(start=start_date.normalize(), end=end_date.normalize(), freq='D')
            df_full = pd.DataFrame({'fecha': full_idx})
            agg = df_full.merge(agg, on='fecha', how='left')
            agg[macro_cols] = agg[macro_cols].fillna(0)

            # Renombrar a etiquetas amigables y pasar a formato largo
            rename_map = {
                'calorias': 'Calorías (kcal)',
                'proteinas': 'Proteínas (g)',
                'carbohidratos': 'Carbohidratos (g)',
                'grasas': 'Grasas (g)'
            }
            agg_ren = agg.rename(columns=rename_map)
            long_df = agg_ren.melt(id_vars='fecha', value_vars=list(rename_map.values()), var_name='Nutriente', value_name='Cantidad')

            colores_linea = ['#15a349', '#4285f4', '#fbbc04', '#ea4335']
            fig_line = px.line(
                long_df,
                x='fecha',
                y='Cantidad',
                color='Nutriente',
                title='Evolución diaria de macros (últimos 30 días)',
                color_discrete_sequence=colores_linea
            )
            fig_line.update_traces(mode='lines+markers')
            fig_line.update_layout(
                margin=dict(t=40, r=20, b=40, l=40),
                xaxis_title='Fecha',
                yaxis_title='Cantidad',
                hovermode='x unified'
            )
            graphLineJSON = fig_line.to_json()

    carrousel_info = ConsumoController.calculoNutrientesMax(df, comidas_usuario_df)

    datita = ConsumoController.obtener_ultimos_consumos_semanales(usuario['id'])

    filas = []
    for semana_obj in datita:
        d = getattr(semana_obj, "__dict__", {}).copy()
        d.pop('_sa_instance_state', None)
        filas.append(d)
    df_semsems = pd.DataFrame(filas)

    df_semsems['fecha_inicio'] = pd.to_datetime(df_semsems['fecha_inicio'])
    df_semsems['fecha_fin'] = pd.to_datetime(df_semsems['fecha_fin'])

    if not comidas_usuario_df.empty:
        comidas_usuario_df['fecha_consumo'] = pd.to_datetime(comidas_usuario_df['fecha_consumo'])

        merged_list = []
        for _, semana_row in df_semsems.iterrows():
            mask = (
                (comidas_usuario_df['fecha_consumo'] >= semana_row['fecha_inicio']) &
                (comidas_usuario_df['fecha_consumo'] <= semana_row['fecha_fin'])
            )
            comidas_semana = comidas_usuario_df[mask].copy()

            if not comidas_semana.empty:
                comidas_semana['fecha_inicio'] = semana_row['fecha_inicio']
                comidas_semana['fecha_fin'] = semana_row['fecha_fin']
                merged_list.append(comidas_semana)
            else:
                semana_vacia = pd.DataFrame([{
                    'fecha_inicio': semana_row['fecha_inicio'],
                    'fecha_fin': semana_row['fecha_fin'],
                    'fecha_consumo': None
                }])
                merged_list.append(semana_vacia)

        df_merged = pd.concat(merged_list, ignore_index=True) if merged_list else pd.DataFrame()
    else:
        df_merged = df_semsems[['fecha_inicio', 'fecha_fin']].copy()
        df_merged['fecha_consumo'] = None

    semanas_unicas = df_merged[['fecha_inicio', 'fecha_fin']].drop_duplicates().head(2)
    df_final = df_merged[
        df_merged['fecha_inicio'].isin(semanas_unicas['fecha_inicio'])
    ].sort_values('fecha_inicio', ascending=False)


    # Mapeo de día de semana (0=Lunes, 6=Domingo)
    dias_semana = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']

    df_final_copy = df_final.copy()
    # Filtrar filas donde fecha_consumo no es None y convertir a datetime
    df_final_copy = df_final_copy[df_final_copy['fecha_consumo'].notna()].copy()
    
    if not df_final_copy.empty:
        df_final_copy['fecha_consumo'] = pd.to_datetime(df_final_copy['fecha_consumo'])
        df_final_copy['dia_semana'] = df_final_copy['fecha_consumo'].dt.dayofweek
        conteo = df_final_copy.groupby(['fecha_inicio', 'dia_semana']).size().reset_index(name='cantidad')
    else:
        # Si no hay datos, crear un DataFrame vacío con las columnas correctas
        conteo = pd.DataFrame(columns=['fecha_inicio', 'dia_semana', 'cantidad'])

    semanas_list = sorted(semanas_unicas['fecha_inicio'].unique(), reverse=True)

    import itertools
    combinaciones = list(itertools.product(semanas_list, range(7)))
    df_completo = pd.DataFrame(combinaciones, columns=['fecha_inicio', 'dia_semana'])

    df_completo = df_completo.merge(conteo, on=['fecha_inicio', 'dia_semana'], how='left')
    df_completo['cantidad'] = df_completo['cantidad'].fillna(0).astype(int)

    df_completo['nombre_dia'] = df_completo['dia_semana'].apply(lambda x: dias_semana[x])

    fig = go.Figure()

    for i, semana_inicio in enumerate(semanas_list):
        df_semana = df_completo[df_completo['fecha_inicio'] == semana_inicio]

        fig.add_trace(go.Bar(
            x=df_semana['nombre_dia'],
            y=df_semana['cantidad'],
            name=f"Semana {semana_inicio.strftime('%d/%m')}",
            text=df_semana['cantidad'],
            textposition='outside'
        ))

    fig.update_layout(
        title='Comparacion subidas semana actual vs anterior',
        xaxis_title='Día de la semana',
        yaxis_title='Cantidad de comidas',
        barmode='group',
        xaxis={'categoryorder': 'array', 'categoryarray': dias_semana},
        margin=dict(t=40, r=20, b=40, l=40)
    )

    graphHistJSON = fig.to_json()
    
    #calculo para tabla html
    comida_usuario_semana_elegida = None
    if not df_semsems.empty and not comidas_usuario_df.empty:
        limites_fecha = df_semsems[['fecha_inicio', 'fecha_fin']].head(1)
        comida_usuario_semana_elegida = comidas_usuario_df[
            comidas_usuario_df['fecha_consumo'].between(
                limites_fecha['fecha_inicio'].values[0], 
                limites_fecha['fecha_fin'].values[0]
            )
        ].copy()
        
        if not comida_usuario_semana_elegida.empty:
            comida_usuario_semana_elegida = comida_usuario_semana_elegida.sort_values('fecha_consumo', ascending=False)
            
            columnas_tabla = ['nombre', 'fecha_consumo', 'calorias', 'proteinas', 'carbohidratos', 'grasas', 'colesterol']
            comida_usuario_semana_elegida = comida_usuario_semana_elegida[columnas_tabla]

    return render_template(
        'consumos.html',
        api_url=api_url,
        usuario=usuario,
        graphJSON=graphJSON,
        graphPieJSON=graphPieJSON,
        graphHoyJSON=graphHoyJSON,
        graphLineJSON=graphLineJSON,
        graphHistJSON=graphHistJSON,
        carrousel_info=carrousel_info,
        comida_usuario_semana_elegida=comida_usuario_semana_elegida
    )


@views_bp.route('/api/consumos/filtrar', methods=['POST'])
def filtrar_consumos_api():
    """Endpoint API que devuelve datos filtrados por rango de fechas en formato JSON"""
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401
    
    try:
        data = request.get_json()
        fecha_inicio_str = data.get('fecha_inicio')
        fecha_fin_str = data.get('fecha_fin')
        
        if not fecha_inicio_str or not fecha_fin_str:
            return jsonify({"success": False, "error": "Faltan fechas de inicio o fin"}), 400
        
        # Convertir strings a objetos date
        fecha_inicio = pd.to_datetime(fecha_inicio_str).date()
        fecha_fin = pd.to_datetime(fecha_fin_str).date()
        
        # Obtener comidas en el rango
        comidas_usuario = ConsumoController.todas_las_comidas(usuario['id'])
        
        if comidas_usuario:
            comidas_list = []
            for comida in comidas_usuario:
                comida_dict = getattr(comida, "__dict__", {})
                comida_dict.pop('_sa_instance_state', None)
                comidas_list.append(comida_dict)
            comidas_df = pd.DataFrame(comidas_list)
            comidas_df['fecha_consumo'] = pd.to_datetime(comidas_df['fecha_consumo'])
            
            # Filtrar por rango de fechas
            mask = (comidas_df['fecha_consumo'].dt.date >= fecha_inicio) & (comidas_df['fecha_consumo'].dt.date <= fecha_fin)
            comidas_filtradas = comidas_df[mask].copy()
            
            if comidas_filtradas.empty:
                return jsonify({"success": False, "error": "No hay datos en el rango seleccionado"}), 404
            
            # Calcular totales para gráfico de barras
            macro_cols = ['calorias', 'proteinas', 'carbohidratos', 'grasas', 'colesterol']
            totales = comidas_filtradas[macro_cols].sum()
            
            # Gráfico de barras
            labels = ['Calorías (kcal)', 'Proteínas (g)', 'Carbohidratos (g)', 'Grasas (g)', 'Colesterol (mg)']
            values = [float(totales[col]) for col in macro_cols]
            
            df_plot = pd.DataFrame({'Nutriente': labels, 'Cantidad': values})
            colores_nutrientes = ['#15a349', '#4285f4', '#fbbc04', '#ea4335', '#9c27b0']
            
            fig_bar = px.bar(df_plot, x='Nutriente', y='Cantidad',
                            title=f'Consumo de nutrientes ({fecha_inicio_str} a {fecha_fin_str})',
                            color='Nutriente', color_discrete_sequence=colores_nutrientes)
            fig_bar.update_layout(margin=dict(t=40, r=20, b=40, l=40), showlegend=False)
            graphJSON = fig_bar.to_json()
            
            # Gráfico de torta
            fig_pie = px.pie(df_plot, values='Cantidad', names='Nutriente',
                            title='Porcentajes de nutrientes consumidos',
                            color='Nutriente', color_discrete_sequence=colores_nutrientes, hole=0.4)
            fig_pie.update_layout(margin=dict(t=35, r=0, b=0, l=0))
            graphPieJSON = fig_pie.to_json()
            
            # Tabla de comidas
            comidas_filtradas = comidas_filtradas.sort_values('fecha_consumo', ascending=False)
            tabla_data = comidas_filtradas[['nombre', 'fecha_consumo', 'calorias', 'proteinas', 'carbohidratos', 'grasas', 'colesterol']].to_dict('records')
            
            # Convertir fechas a string para JSON
            for row in tabla_data:
                row['fecha_consumo'] = row['fecha_consumo'].strftime('%Y-%m-%d')
            
            return jsonify({
                "success": True,
                "graphJSON": graphJSON,
                "graphPieJSON": graphPieJSON,
                "tabla_data": tabla_data,
                "fecha_inicio": fecha_inicio_str,
                "fecha_fin": fecha_fin_str
            })
        else:
            return jsonify({"success": False, "error": "No hay comidas registradas"}), 404
            
    except Exception as e:
        return jsonify({"success": False, "error": f"Error al filtrar datos: {str(e)}"}), 500
