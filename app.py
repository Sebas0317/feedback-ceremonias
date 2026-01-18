import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Feedback de Ceremonias Ágiles",
    page_icon="📋",
    layout="centered"
)

# ============================================================================
# ESTILOS CSS PERSONALIZADOS
# ============================================================================

st.markdown("""
    <style>
    /* Fondo general negro */
    .stApp {
        background-color: #000000;
    }
    
    /* Título principal */
    h1 {
        color: #ffffff;
        font-weight: 600;
        padding-bottom: 12px;
        border-bottom: 3px solid #ffffff;
    }
    
    /* Subtítulos */
    h3 {
        color: #ffffff;
        font-weight: 500;
        margin-top: 24px;
    }
    
    /* Labels de campos */
    .stTextInput label, .stTextArea label, .stSelectbox label, .stMultiSelect label {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Inputs con fondo blanco y texto negro */
    .stTextInput input, .stTextArea textarea {
        background-color: #ffffff !important;
        border: 1px solid #cccccc !important;
        color: #000000 !important;
    }
    
    /* Placeholder en inputs */
    .stTextInput input::placeholder, .stTextArea textarea::placeholder {
        color: #666666 !important;
    }
    
    /* Radio buttons - texto blanco */
    .stRadio label, .stRadio div[role="radiogroup"] label {
        color: #ffffff !important;
    }
    
    /* Checkboxes - texto blanco */
    .stCheckbox label, .stCheckbox span {
        color: #ffffff !important;
    }
    
    /* Botón de envío - blanco con texto negro */
    .stButton > button {
        background-color: #ffffff;
        color: #000000;
        font-weight: 600;
        border: none;
        padding: 12px 30px;
        border-radius: 6px;
        width: 100%;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(255,255,255,0.2);
    }
    
    .stButton > button:hover {
        background-color: #e0e0e0;
        box-shadow: 0 4px 8px rgba(255,255,255,0.3);
        transform: translateY(-1px);
    }
    
    /* Mensajes de éxito - fondo blanco con texto negro */
    .stSuccess {
        background-color: #ffffff;
        border-left: 4px solid #4CAF50;
        border-radius: 6px;
        color: #000000 !important;
    }
    
    /* Mensajes de error - fondo blanco con texto negro */
    .stError {
        background-color: #ffffff;
        border-left: 4px solid #f44336;
        border-radius: 6px;
        color: #000000 !important;
    }
    
    /* Contenedor del formulario */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 700px;
    }
    
    /* Texto descriptivo */
    p {
        color: #ffffff;
    }
    
    /* Divisor */
    hr {
        border-color: #ffffff;
    }
    
    /* Help text */
    .stTextInput small, .stTextArea small {
        color: #cccccc !important;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================================
# CONSTANTES
# ============================================================================

CSV_FILE = "responses.csv"
CORPORATE_DOMAIN = "@holatest"

CEREMONY_OPTIONS = [
    "Daily Scrum",
    "Sprint Review",
    "Sprint Planning",
    "Sprint Retrospectiva",
    "Refinamiento Técnico/Negocio"
]

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def initialize_csv():
    """
    Crea el archivo CSV con los encabezados si no existe.
    """
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "timestamp",
            "email",
            "team_id",
            "ceremony_types",
            "value_rating",
            "had_clear_objective",
            "main_affecting_factor",
            "improvement_action"
        ])
        df.to_csv(CSV_FILE, index=False, encoding='utf-8')


def email_exists(email):
    """
    Verifica si un email ya está registrado en el CSV.
    
    Args:
        email (str): Email a verificar
        
    Returns:
        bool: True si el email existe, False en caso contrario
    """
    if not os.path.exists(CSV_FILE):
        return False
    
    df = pd.read_csv(CSV_FILE, encoding='utf-8')
    return email.lower() in df['email'].str.lower().values


def validate_email(email):
    """
    Valida que el email tenga el dominio corporativo correcto.
    
    Args:
        email (str): Email a validar
        
    Returns:
        bool: True si el email es válido, False en caso contrario
    """
    return email.lower().endswith(CORPORATE_DOMAIN.lower())


def save_response(data):
    """
    Guarda una nueva respuesta en el archivo CSV.
    
    Args:
        data (dict): Diccionario con los datos del formulario
        
    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    try:
        # Convertir lista de ceremonias a string separado por comas
        ceremony_types_str = ", ".join(data['ceremony_types'])
        
        # Crear diccionario ordenado con timestamp PRIMERO
        ordered_data = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'email': data['email'],
            'team_id': data['team_id'],
            'ceremony_types': ceremony_types_str,
            'value_rating': data['value_rating'],
            'had_clear_objective': data['had_clear_objective'],
            'main_affecting_factor': data['main_affecting_factor'],
            'improvement_action': data['improvement_action']
        }
        
        # Crear DataFrame con la nueva fila
        df_new = pd.DataFrame([ordered_data])
        
        # Append al CSV existente
        df_new.to_csv(CSV_FILE, mode='a', header=False, index=False, encoding='utf-8')
        return True
    except Exception as e:
        st.error(f"Error al guardar la respuesta: {str(e)}")
        return False


def reset_form():
    """
    Resetea todos los valores del formulario en el estado de sesión.
    """
    st.session_state.email = ""
    st.session_state.team_id = ""
    st.session_state.main_affecting_factor = ""
    st.session_state.improvement_action = ""
    for ceremony in CEREMONY_OPTIONS:
        st.session_state[f"ceremony_{ceremony}"] = False


# ============================================================================
# INTERFAZ DE LA APLICACIÓN
# ============================================================================

def main():
    # Inicializar CSV
    initialize_csv()
    
    # Inicializar estado de sesión para controlar el éxito del envío
    if 'form_submitted' not in st.session_state:
        st.session_state.form_submitted = False
    
    # Inicializar valores por defecto si no existen
    if 'email' not in st.session_state:
        st.session_state.email = ""
    if 'team_id' not in st.session_state:
        st.session_state.team_id = ""
    if 'main_affecting_factor' not in st.session_state:
        st.session_state.main_affecting_factor = ""
    if 'improvement_action' not in st.session_state:
        st.session_state.improvement_action = ""
    
    # Encabezado
    st.title("📋 Feedback de Ceremonias Ágiles")
    st.markdown("""
        <p style='color: #ffffff; font-size: 16px; margin-bottom: 30px;'>
        Tu opinión es fundamental para mejorar nuestras ceremonias Sprint a Sprint.
        Por favor completa todos los campos con sinceridad.
        </p>
    """, unsafe_allow_html=True)
    
    # Separador visual
    st.markdown("---")
    
    # ========================================================================
    # FORMULARIO
    # ========================================================================
    
    with st.form("feedback_form", clear_on_submit=False):
        
        # Campo 1: Email
        email = st.text_input(
            "1. Correo electrónico corporativo *",
            value=st.session_state.email,
            placeholder=f"ejemplo{CORPORATE_DOMAIN}",
            help=f"Solo se aceptan correos con dominio {CORPORATE_DOMAIN}",
            key="email_input"
        )
        
        # Campo 2: Identificación del equipo
        team_id = st.text_input(
            "2. Identificación del equipo *",
            value=st.session_state.team_id,
            placeholder="Nombre del proyecto - célula",
            help="Ejemplo: Proyecto Phoenix - Célula Backend",
            key="team_id_input"
        )
        
        # Campo 3: Tipo de ceremonias
        st.markdown("### 3. Tipo de ceremonias *")
        ceremony_types = []
        for ceremony in CEREMONY_OPTIONS:
            # Inicializar estado de checkbox si no existe
            checkbox_key = f"ceremony_{ceremony}"
            if checkbox_key not in st.session_state:
                st.session_state[checkbox_key] = False
            
            if st.checkbox(ceremony, value=st.session_state[checkbox_key], key=f"check_{ceremony}"):
                ceremony_types.append(ceremony)
        
        # Campo 4: Calificación de valor
        st.markdown("### 4. ¿Cómo calificas el valor obtenido en las ceremonias frente al tiempo dedicado? *")
        value_rating = st.radio(
            "Selecciona tu calificación:",
            options=[1, 2, 3, 4, 5],
            format_func=lambda x: {
                1: "1 - Sin valor / Tiempo perdido",
                2: "2 - Poco valor",
                3: "3 - Valor aceptable",
                4: "4 - Buen valor",
                5: "5 - Excelente valor / Superó expectativas"
            }[x],
            horizontal=False,
            key="rating"
        )
        
        # Campo 5: Objetivo claro y timebox
        st.markdown("### 5. ¿La sesión contó con un objetivo claro, manejo del tiempo (Timebox) y evitó discusiones improductivas? *")
        had_clear_objective = st.radio(
            "Tu respuesta:",
            options=["Sí", "No"],
            horizontal=True,
            key="objective"
        )
        
        # Campo 6: Factor que afectó el valor
        main_affecting_factor = st.text_area(
            "6. ¿Qué factor afectó más el valor de las sesiones? *",
            value=st.session_state.main_affecting_factor,
            placeholder="Describe el principal factor que impactó (positiva o negativamente) el valor de las ceremonias...",
            height=120,
            help="Sé específico: ¿Fue la preparación, la facilitación, la participación del equipo, las herramientas, etc.?",
            key="factor_input"
        )
        
        # Campo 7: Acción de mejora
        improvement_action = st.text_area(
            "7. ¿Qué acción específica debería tomarse para que la próxima sesión sea un '5'? *",
            value=st.session_state.improvement_action,
            placeholder="Propón una acción concreta y accionable...",
            height=120,
            help="Piensa en algo específico que podamos implementar en el próximo sprint",
            key="action_input"
        )
        
        # Separador antes del botón
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón de envío
        submit_button = st.form_submit_button("✨ Enviar Feedback")
        
        # ====================================================================
        # VALIDACIÓN Y ENVÍO
        # ====================================================================
        
        if submit_button:
            # Actualizar session_state con valores actuales
            st.session_state.email = email
            st.session_state.team_id = team_id
            st.session_state.main_affecting_factor = main_affecting_factor
            st.session_state.improvement_action = improvement_action
            
            # Actualizar estado de checkboxes
            for ceremony in CEREMONY_OPTIONS:
                st.session_state[f"ceremony_{ceremony}"] = ceremony in ceremony_types
            
            # Lista de errores
            errors = []
            
            # Validar email
            if not email:
                errors.append("El correo electrónico es obligatorio")
            elif not validate_email(email):
                errors.append(f"El correo debe terminar en {CORPORATE_DOMAIN}")
            elif email_exists(email):
                errors.append("⚠️ Este correo ya ha sido registrado. No puedes enviar el formulario nuevamente.")
            
            # Validar otros campos obligatorios
            if not team_id:
                errors.append("La identificación del equipo es obligatoria")
            
            if not ceremony_types:
                errors.append("Debes seleccionar al menos un tipo de ceremonia")
            
            if not main_affecting_factor:
                errors.append("Debes describir el factor que afectó el valor de las sesiones")
            
            if not improvement_action:
                errors.append("Debes proponer una acción de mejora")
            
            # Mostrar errores o guardar
            if errors:
                st.error("**Por favor corrige los siguientes errores:**")
                for error in errors:
                    st.markdown(f"- {error}")
            else:
                # Preparar datos
                data = {
                    "email": email.lower().strip(),
                    "team_id": team_id.strip(),
                    "ceremony_types": ceremony_types,
                    "value_rating": value_rating,
                    "had_clear_objective": had_clear_objective,
                    "main_affecting_factor": main_affecting_factor.strip(),
                    "improvement_action": improvement_action.strip()
                }
                
                # Guardar
                if save_response(data):
                    st.session_state.form_submitted = True
                    # Limpiar el formulario después del envío exitoso
                    reset_form()
    
    # ========================================================================
    # MENSAJE DE ÉXITO Y BOTÓN DE NUEVA RESPUESTA
    # ========================================================================
    
    if st.session_state.form_submitted:
        st.success("### ¡Gracias por tu feedback! 🚀")
        st.markdown("""
            <div style='background-color: #ffffff; padding: 20px; border-radius: 8px; 
                        border-left: 4px solid #4CAF50; margin-top: 20px;'>
                <p style='color: #000000; margin: 0; font-size: 16px;'>
                    Tu respuesta ha sido registrada exitosamente.<br>
                    <strong>Tu opinión ayudará a mejorar nuestras ceremonias Sprint a Sprint.</strong>
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Confetti visual
        st.balloons()
        
        # Botón para enviar nueva respuesta
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("📝 Enviar nueva respuesta", use_container_width=True):
            st.session_state.form_submitted = False
            st.rerun()


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()