from flask import Blueprint, request, jsonify
import requests
import logging
import os
import re
from urllib.parse import quote

icd11 = Blueprint('icd11', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL base del contenedor ICD-11 API
# En Docker, usamos el nombre del servicio como hostname
ICD11_API_BASE_URL = os.environ.get('ICD11_API_URL', 'http://icd11-api')

# Endpoint de búsqueda de ICD-11 (versión 2025-01 en español)
ICD11_SEARCH_ENDPOINT = "/icd/release/11/2025-01/mms/search"
ICD11_CODEINFO_ENDPOINT = "/icd/release/11/2025-01/mms/codeinfo"
ICD11_ENTITY_ENDPOINT = "/icd/release/11/2025-01/mms"

# Patrón para detectar códigos CIE-11 (ej: 1A00, MG3Z, 8C21.0)
CIE11_CODE_PATTERN = re.compile(r'^[A-Z0-9]{2,}(\.[A-Z0-9]+)?$', re.IGNORECASE)

# Patrón estricto para validar códigos CIE-11 (solo alfanuméricos y puntos)
CIE11_CODE_STRICT_PATTERN = re.compile(r'^[A-Z0-9]{1,7}(\.[A-Z0-9]{1,5})?$', re.IGNORECASE)

# Patrón para validar entity IDs (solo números)
ENTITY_ID_PATTERN = re.compile(r'^[0-9]+$')


def get_icd11_headers():
    """Retorna los headers estándar para las peticiones a ICD-11 API"""
    return {
        'Accept': 'application/json',
        'Accept-Language': 'es',
        'API-Version': 'v2'
    }


def make_cors_response():
    """Crea una respuesta OPTIONS con headers CORS"""
    response = jsonify({'success': True})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
    return response


def clean_icd11_title(title):
    """Limpia el título de etiquetas HTML de resaltado"""
    if not title:
        return title
    return (title
            .replace('<em class="found">', '')
            .replace("<em class='found'>", '')
            .replace('</em>', ''))


def get_entity_by_code(code):
    """
    Busca una entidad por su código CIE-11 exacto.
    Retorna dict con code y title, o None si no se encuentra.
    """
    try:
        # Validar que el código tenga un formato CIE-11 válido
        if not code or not CIE11_CODE_STRICT_PATTERN.match(code):
            logger.warning(f"Código CIE-11 inválido rechazado: {code[:50] if code else 'None'}")
            return None
        
        # Sanitizar el código (ya validado, pero encoding adicional por seguridad)
        safe_code = quote(code.upper(), safe='')
        
        headers = get_icd11_headers()
        
        # Primero obtener el stemId del código
        codeinfo_url = f"{ICD11_API_BASE_URL}{ICD11_CODEINFO_ENDPOINT}/{safe_code}"
        response = requests.get(codeinfo_url, headers=headers, timeout=5)
        
        if response.status_code != 200:
            return None
        
        codeinfo = response.json()
        stem_id = codeinfo.get('stemId', '')
        
        if not stem_id:
            return None
        
        # Usar el stemId directamente como URL (ya es una URL completa)
        # Reemplazar el host por nuestro contenedor local
        entity_url = stem_id.replace('http://id.who.int', ICD11_API_BASE_URL)
        
        # Obtener la entidad completa para el título
        entity_response = requests.get(entity_url, headers=headers, timeout=5)
        
        if entity_response.status_code != 200:
            return None
        
        entity = entity_response.json()
        title = entity.get('title', {})
        
        # El título puede ser un objeto con @value o un string
        if isinstance(title, dict):
            title_text = title.get('@value', '')
        else:
            title_text = str(title)
        
        return {
            'code': code.upper(),
            'title': title_text
        }
    except Exception as e:
        logger.error(f"Error buscando código {code}: {str(e)}")
        return None

@icd11.route('/icd11/search', methods=['GET', 'OPTIONS'])
def search_icd11():
    """
    Busca diagnósticos en la API de CIE-11.
    
    Query Parameters:
        q: Término de búsqueda (requerido)
        max_results: Número máximo de resultados (opcional, default: 10)
    
    Returns:
        JSON con lista de diagnósticos encontrados
    """
    if request.method == 'OPTIONS':
        return make_cors_response()
    
    try:
        search_term = request.args.get('q', '').strip()
        max_results = request.args.get('max_results', 10, type=int)
        
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'El parámetro de búsqueda "q" es requerido'
            }), 400
        
        if len(search_term) < 2:
            return jsonify({
                'success': True,
                'data': [],
                'message': 'Se requieren al menos 2 caracteres para buscar'
            })
        
        # Llamar a la API de ICD-11 (endpoint de búsqueda)
        # La API de ICD-11 usa el endpoint /icd/release/11/2025-01/mms/search
        search_url = f"{ICD11_API_BASE_URL}{ICD11_SEARCH_ENDPOINT}"
        
        params = {
            'q': search_term,
            'useFlexisearch': 'true',
            'flatResults': 'true',
            'highlightingEnabled': 'false'
        }
        
        headers = get_icd11_headers()
        
        response = requests.get(search_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Procesar los resultados para un formato más simple
            results = []
            destination_entities = data.get('destinationEntities', [])
            
            for entity in destination_entities[:max_results]:
                # Extraer el código CIE-11 del theCode o del ID
                code = entity.get('theCode', '')
                title = clean_icd11_title(entity.get('title', ''))
                
                # Solo agregar si tiene código y título
                if code and title:
                    results.append({
                        'code': code,
                        'title': title,
                        'id': entity.get('id', ''),
                        'score': entity.get('score', 0)
                    })
            
            return jsonify({
                'success': True,
                'data': results,
                'total': len(results)
            })
        else:
            logger.error(f"Error from ICD-11 API: {response.status_code} - {response.text}")
            return jsonify({
                'success': False,
                'error': f'Error al consultar la API de CIE-11: {response.status_code}'
            }), 500
            
    except requests.exceptions.ConnectionError:
        logger.error("No se puede conectar con el servicio ICD-11 API")
        return jsonify({
            'success': False,
            'error': 'No se puede conectar con el servicio de CIE-11. Verifique que el contenedor esté en ejecución.'
        }), 503
    except requests.exceptions.Timeout:
        logger.error("Timeout al consultar ICD-11 API")
        return jsonify({
            'success': False,
            'error': 'Tiempo de espera agotado al consultar CIE-11'
        }), 504
    except Exception as e:
        logger.error(f"Error inesperado en búsqueda ICD-11: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error inesperado: {str(e)}'
        }), 500


@icd11.route('/icd11/entity/<path:entity_id>', methods=['GET', 'OPTIONS'])
def get_icd11_entity(entity_id):
    """
    Obtiene los detalles de una entidad específica de CIE-11.
    
    Args:
        entity_id: ID de la entidad (puede incluir el path completo)
    
    Returns:
        JSON con los detalles de la entidad
    """
    if request.method == 'OPTIONS':
        return make_cors_response()
    
    try:
        # Validar que el entity_id sea un número válido
        if not entity_id or not ENTITY_ID_PATTERN.match(entity_id):
            logger.warning(f"Entity ID inválido rechazado: {entity_id[:50] if entity_id else 'None'}")
            return jsonify({
                'success': False,
                'error': 'ID de entidad inválido'
            }), 400
        
        # Sanitizar el entity_id (ya validado como numérico)
        safe_entity_id = quote(entity_id, safe='')
        
        # Construir la URL para obtener la entidad
        entity_url = f"{ICD11_API_BASE_URL}/icd/entity/{safe_entity_id}"
        
        headers = get_icd11_headers()
        
        response = requests.get(entity_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return jsonify({
                'success': True,
                'data': data
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Entidad no encontrada: {response.status_code}'
            }), 404
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'error': 'No se puede conectar con el servicio de CIE-11'
        }), 503
    except Exception as e:
        logger.error(f"Error al obtener entidad ICD-11: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Error: {str(e)}'
        }), 500


@icd11.route('/icd11/autocomplete/code', methods=['GET', 'OPTIONS'])
def autocomplete_by_code():
    """
    Endpoint para autocompletado por código CIE-11.
    Busca el código exacto y devuelve su información.
    
    Query Parameters:
        q: Código CIE-11 exacto a buscar (requerido)
        limit: No usado, se mantiene por compatibilidad
    """
    if request.method == 'OPTIONS':
        return make_cors_response()
    
    try:
        search_term = request.args.get('q', '').strip().upper()
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        suggestions = []
        
        # Buscar solo el código exacto
        exact_match = get_entity_by_code(search_term)
        if exact_match:
            suggestions.append(exact_match)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
            
    except Exception as e:
        logger.error(f"Error en autocompletado por código ICD-11: {str(e)}")
        return jsonify({
            'success': True,
            'suggestions': []
        })


@icd11.route('/icd11/autocomplete/disease', methods=['GET', 'OPTIONS'])
def autocomplete_by_disease():
    """
    Endpoint para autocompletado por nombre de enfermedad.
    Busca enfermedades cuyo nombre contenga el término de búsqueda.
    
    Query Parameters:
        q: Nombre de enfermedad a buscar (requerido)
        limit: Número máximo de sugerencias (opcional, default: 8)
    """
    if request.method == 'OPTIONS':
        return make_cors_response()
    
    try:
        search_term = request.args.get('q', '').strip()
        limit = request.args.get('limit', 8, type=int)
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        suggestions = []
        
        # Usar búsqueda flexible para nombres de enfermedades
        search_url = f"{ICD11_API_BASE_URL}{ICD11_SEARCH_ENDPOINT}"
        
        params = {
            'q': search_term,
            'useFlexisearch': 'true',
            'flatResults': 'true',
            'highlightingEnabled': 'false'
        }
        
        headers = get_icd11_headers()
        
        response = requests.get(search_url, params=params, headers=headers, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            for entity in data.get('destinationEntities', []):
                if len(suggestions) >= limit:
                    break
                    
                code = entity.get('theCode', '')
                title = clean_icd11_title(entity.get('title', ''))
                
                if code and title:
                    suggestions.append({
                        'code': code,
                        'title': title
                    })
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
            
    except Exception as e:
        logger.error(f"Error en autocompletado por enfermedad ICD-11: {str(e)}")
        return jsonify({
            'success': True,
            'suggestions': []
        })


@icd11.route('/icd11/autocomplete', methods=['GET', 'OPTIONS'])
def autocomplete_icd11():
    """
    Endpoint general de autocompletado (mantener para compatibilidad).
    Detecta automáticamente si es código o nombre.
    
    Query Parameters:
        q: Término de búsqueda (requerido)
        limit: Número máximo de sugerencias (opcional, default: 8)
    """
    if request.method == 'OPTIONS':
        return make_cors_response()
    
    try:
        search_term = request.args.get('q', '').strip()
        limit = request.args.get('limit', 8, type=int)
        
        if not search_term or len(search_term) < 2:
            return jsonify({
                'success': True,
                'suggestions': []
            })
        
        suggestions = []
        
        # Verificar si parece un código CIE-11
        if CIE11_CODE_PATTERN.match(search_term):
            # Intentar buscar por código exacto primero
            exact_match = get_entity_by_code(search_term.upper())
            if exact_match:
                suggestions.append(exact_match)
        
        # Si no hay resultados exactos o es una búsqueda por texto, hacer búsqueda general
        if len(suggestions) < limit:
            # Usar el endpoint de búsqueda con parámetros optimizados
            search_url = f"{ICD11_API_BASE_URL}{ICD11_SEARCH_ENDPOINT}"
            
            params = {
                'q': search_term,
                'useFlexisearch': 'true',
                'flatResults': 'true',
                'highlightingEnabled': 'false'
            }
            
            headers = get_icd11_headers()
            
            response = requests.get(search_url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                existing_codes = {s['code'] for s in suggestions}
                
                for entity in data.get('destinationEntities', []):
                    if len(suggestions) >= limit:
                        break
                        
                    code = entity.get('theCode', '')
                    title = clean_icd11_title(entity.get('title', ''))
                    
                    # Evitar duplicados
                    if code and title and code not in existing_codes:
                        suggestions.append({
                            'code': code,
                            'title': title
                        })
                        existing_codes.add(code)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
            
    except Exception as e:
        logger.error(f"Error en autocompletado ICD-11: {str(e)}")
        return jsonify({
            'success': True,
            'suggestions': []
        })


@icd11.route('/icd11/health', methods=['GET'])
def icd11_health():
    """
    Verifica si el servicio ICD-11 está disponible.
    """
    try:
        response = requests.get(f"{ICD11_API_BASE_URL}{ICD11_SEARCH_ENDPOINT}?q=test", timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'success': True,
                'status': 'healthy',
                'message': 'Servicio ICD-11 disponible'
            })
        else:
            return jsonify({
                'success': False,
                'status': 'unhealthy',
                'message': f'Servicio ICD-11 respondió con código {response.status_code}'
            }), 503
            
    except requests.exceptions.ConnectionError:
        return jsonify({
            'success': False,
            'status': 'unavailable',
            'message': 'No se puede conectar con el servicio ICD-11'
        }), 503
    except Exception as e:
        return jsonify({
            'success': False,
            'status': 'error',
            'message': str(e)
        }), 500
