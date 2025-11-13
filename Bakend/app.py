from flask import Flask, request, jsonify
from flask_cors import CORS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaLLM
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import re
import json
import uuid

app = Flask(__name__)
CORS(app)

# 1️⃣ Embeddings y carga del índice FAISS
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Variable global para la base de datos FAISS
db = None

# Función para cargar el índice FAISS si existeIngresa ahora
def load_faiss_index():
    global db
    try:
        if os.path.exists("faiss_index"):
            db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
            print("✅ Índice FAISS cargado")
            return True
        else:
            print("⚠️ No se encontró el índice FAISS")
            return False
    except Exception as e:
        print(f"⚠️ Error al cargar el índice FAISS: {e}")
        return False

# Función para guardar el índice FAISS
def save_faiss_index():
    global db
    try:
        if db:
            db.save_local("faiss_index")
            print("✅ Índice FAISS guardado")
            return True
        else:
            print("⚠️ No hay índice para guardar")
            return False
    except Exception as e:
        print(f"⚠️ Error al guardar el índice FAISS: {e}")
        return False

# Función para procesar JSON y crear documentos
def process_json_data(json_data):
    documents = []
    
    # Si es un solo documento JSON
    if isinstance(json_data, dict):
        # Convertir el diccionario a una cadena JSON
        json_str = json.dumps(json_data, ensure_ascii=False)
        # Crear un documento con el contenido JSON
        doc = Document(
            page_content=json_str,
            metadata={"source": "json", "id": str(uuid.uuid4())}
        )
        documents.append(doc)
    
    # Si es una lista de documentos JSON
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            if isinstance(item, dict):
                # Convertir cada diccionario a una cadena JSON
                json_str = json.dumps(item, ensure_ascii=False)
                # Crear un documento con el contenido JSON
                doc = Document(
                    page_content=json_str,
                    metadata={"source": "json", "id": str(uuid.uuid4()), "index": i}
                )
                documents.append(doc)
    
    return documents

# Función para procesar texto y crear documentos
def process_text_data(text, single_document=False):
    documents = []
    
    if single_document:
        # Tratar todo el texto como un solo documento
        doc = Document(
            page_content=text,
            metadata={"source": "text", "id": str(uuid.uuid4())}
        )
        documents.append(doc)
    else:
        # Dividir el texto en líneas o párrafos
        # Primero, dividir por líneas
        lines = text.split('\n')
        
        # Filtrar líneas vacías
        non_empty_lines = [line.strip() for line in lines if line.strip()]
        
        # Si hay muy pocas líneas, tratar como un solo documento
        if len(non_empty_lines) <= 3:
            doc = Document(
                page_content='\n'.join(non_empty_lines),
                metadata={"source": "text", "id": str(uuid.uuid4())}
            )
            documents.append(doc)
        else:
            # Crear un documento por línea
            for i, line in enumerate(non_empty_lines):
                doc = Document(
                    page_content=line,
                    metadata={"source": "text", "id": str(uuid.uuid4()), "line": i}
                )
                documents.append(doc)
    
    return documents

# Función para procesar texto con un divisor más inteligente (por párrafos)
def process_text_with_splitter(text, chunk_size=1000, chunk_overlap=200):
    documents = []
    
    # Crear un divisor de texto
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
    )
    
    # Dividir el texto en fragmentos
    texts = text_splitter.split_text(text)
    
    # Crear un documento por fragmento
    for i, text_chunk in enumerate(texts):
        doc = Document(
            page_content=text_chunk,
            metadata={"source": "text", "id": str(uuid.uuid4()), "chunk": i}
        )
        documents.append(doc)
    
    return documents

# 2️⃣ Modelo via Ollama (asegúrate de haber hecho 'ollama pull llama3')
llm = OllamaLLM(model="llama3:instruct")

# 3️⃣ Prompt base mejorado - SIN mención de documentos
BASE_PROMPT = """Eres un experto en apartamentos y viviendas. Responde a las preguntas del usuario basándote en la siguiente información, pero NUNCA menciones que te basas en documentos, archivos o información proporcionada. Responde como si fuera tu conocimiento natural.

Información:
{context}

Pregunta del usuario:
{question}

Respuesta:"""

# Función para verificar si es un saludo básico
def is_basic_greeting(question):
    basic_greetings = [
        r'^\s*(hola|ola|hello|hi)\s*$',
        r'^\s*(buenos dias|buenas tardes|buenas noches)\s*$',
        r'^\s*(como estas|cómo estás|cómo te va|como te va)\s*$',
        r'^\s*(adios|adiós|bye|hasta luego)\s*$',
        r'^\s*(gracias|muchas gracias|te lo agradezco)\s*$',
        r'^\s*(ok|okay|vale|de acuerdo)\s*$',
        r'^\s*(buen dia|buena tarde|buena noche)\s*$'
    ]
    
    question_lower = question.lower()
    for pattern in basic_greetings:
        if re.match(pattern, question_lower):
            return True
    return False

# Función para obtener respuesta de saludo básico
def get_greeting_response(question):
    question_lower = question.lower()
    
    if "hola" in question_lower or "ola" in question_lower:
        return "¡Hola! ¿En qué puedo ayudarte hoy?"
    elif "adios" in question_lower or "bye" in question_lower:
        return "¡Hasta luego! Si necesitas algo más, estaré aquí para ayudarte."
    elif "gracias" in question_lower:
        return "¡De nada! Estoy aquí para ayudarte cuando lo necesites."
    elif "como estas" in question_lower or "cómo estás" in question_lower:
        return "Estoy bien, gracias por preguntar. ¿En qué puedo asistirte hoy?"
    elif "buenos dias" in question_lower:
        return "¡Buenos días! ¿En qué puedo ayudarte hoy?"
    elif "buenas tardes" in question_lower:
        return "¡Buenas tardes! ¿En qué puedo ayudarte hoy?"
    elif "buenas noches" in question_lower:
        return "¡Buenas noches! ¿En qué puedo ayudarte hoy?"
    else:
        return "¡Hola! ¿Tienes alguna pregunta sobre apartamentos?"

# Función para limpiar la respuesta de frases no deseadas
def clean_response(response):
    unwanted_phrases = [
        "Según los documentos proporcionados, ",
        "Según los documentos, ",
        "Basado en los documentos proporcionados, ",
        "Basado en los documentos, ",
        "De acuerdo con los documentos proporcionados, ",
        "De acuerdo con los documentos, ",
        "Según la información proporcionada, ",
        "Basado en la información proporcionada, ",
        "En los documentos proporcionados, ",
        "En los documentos, ",
        "La información proporcionada indica que, ",
        "Los documentos mencionan que, "
    ]
    
    cleaned_response = response
    for phrase in unwanted_phrases:
        cleaned_response = cleaned_response.replace(phrase, "")
    
    return cleaned_response.strip()

# Función para verificar si la pregunta es válida
def is_valid_question(question):
    # Lista de patrones que indican preguntas no válidas
    invalid_patterns = [
        r'^[jJ]+[aA]+$',
        r'^[aA]+[jJ]+$',
        r'^[hH]+[oO]+$',
        r'^[aA]+$',
        r'^[jJ]+$',
        r'^[sS]+$',
        r'^[dD]+$',
        r'^[pP]+[eE]+$',
        r'^[pP]+[iI]+$',
        r'^[aA]+[sS]+$',
        r'^[aA]+[dD]+$',
        r'^\s*$',
        r'^[^a-zA-ZáéíóúÁÉÍÓÚñÑ]*$',
        r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ]{1,2}$'
    ]
    
    # Verificar si la pregunta coincide con algún patrón inválido
    for pattern in invalid_patterns:
        if re.match(pattern, question):
            return False
    
    # Si la pregunta es muy corta (menos de 3 caracteres)
    if len(question) < 3:
        return False
    
    return True

# Función para verificar si la respuesta es útil
def is_response_useful(response):
    # Lista de frases que indican que la respuesta no es útil
    useless_phrases = [
        "no tengo información",
        "no hay una respuesta específica",
        "no mencionan",
        "no está relacionado",
        "no puedo responder",
        "no tengo datos",
        "no se encuentra",
        "no aparece",
        "lo siento",
        "no hay pregunta real",
        "no tengo suficiente información",
        "podrías reescribir tu pregunta"
    ]
    
    response_lower = response.lower()
    for phrase in useless_phrases:
        if phrase in response_lower:
            return False
    
    # Si la respuesta es muy corta (menos de 50 caracteres) y no contiene información útil
    if len(response) < 50 and "no" in response_lower:
        return False
    
    return True

# Endpoint para cargar documentos JSON
@app.route("/upload-json", methods=["POST"])
def upload_json():
    global db
    
    # Verificar si se envió un archivo
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se envió ningún archivo"})
    
    file = request.files['file']
    
    # Verificar si el archivo tiene un nombre
    if file.filename == '':
        return jsonify({"status": "error", "message": "No se seleccionó ningún archivo"})
    
    # Verificar si el archivo es JSON
    if not file.filename.lower().endswith('.json'):
        return jsonify({"status": "error", "message": "El archivo debe ser de tipo JSON"})
    
    try:
        # Leer el contenido del archivo
        file_content = file.read().decode('utf-8')
        
        # Parsear el JSON
        json_data = json.loads(file_content)
        
        # Procesar los datos JSON para crear documentos
        documents = process_json_data(json_data)
        
        if not documents:
            return jsonify({"status": "error", "message": "No se pudieron procesar los datos JSON"})
        
        # Crear o actualizar el índice FAISS
        if db is None:
            # Si no hay un índice existente, crear uno nuevo
            db = FAISS.from_documents(documents, embeddings)
        else:
            # Si ya hay un índice, agregar los nuevos documentos
            db.add_documents(documents)
        
        # Guardar el índice actualizado
        save_faiss_index()
        
        return jsonify({
            "status": "success", 
            "message": f"Se cargaron {len(documents)} documentos correctamente",
            "document_count": len(documents)
        })
        
    except json.JSONDecodeError:
        return jsonify({"status": "error", "message": "El archivo no contiene un JSON válido"})
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar el archivo: {str(e)}"})

# Endpoint para cargar documentos JSON desde texto
@app.route("/upload-json-text", methods=["POST"])
def upload_json_text():
    global db
    
    # Obtener los datos JSON del cuerpo de la solicitud
    data = request.get_json()
    
    if not data or 'json_data' not in data:
        return jsonify({"status": "error", "message": "No se proporcionaron datos JSON"})
    
    try:
        # Parsear el JSON
        json_data = data['json_data']
        
        # Procesar los datos JSON para crear documentos
        documents = process_json_data(json_data)
        
        if not documents:
            return jsonify({"status": "error", "message": "No se pudieron procesar los datos JSON"})
        
        # Crear o actualizar el índice FAISS
        if db is None:
            # Si no hay un índice existente, crear uno nuevo
            db = FAISS.from_documents(documents, embeddings)
        else:
            # Si ya hay un índice, agregar los nuevos documentos
            db.add_documents(documents)
        
        # Guardar el índice actualizado
        save_faiss_index()
        
        return jsonify({
            "status": "success", 
            "message": f"Se cargaron {len(documents)} documentos correctamente",
            "document_count": len(documents)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar los datos JSON: {str(e)}"})

# Endpoint para cargar documentos TXT
@app.route("/upload-txt", methods=["POST"])
def upload_txt():
    global db
    
    # Verificar si se envió un archivo
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No se envió ningún archivo"})
    
    file = request.files['file']
    
    # Verificar si el archivo tiene un nombre
    if file.filename == '':
        return jsonify({"status": "error", "message": "No se seleccionó ningún archivo"})
    
    # Verificar si el archivo es TXT
    if not file.filename.lower().endswith('.txt'):
        return jsonify({"status": "error", "message": "El archivo debe ser de tipo TXT"})
    
    try:
        # Leer el contenido del archivo
        file_content = file.read().decode('utf-8')
        
        # Obtener parámetros de la solicitud
        single_document = request.form.get('single_document', 'false').lower() == 'true'
        use_splitter = request.form.get('use_splitter', 'false').lower() == 'true'
        chunk_size = int(request.form.get('chunk_size', 1000))
        chunk_overlap = int(request.form.get('chunk_overlap', 200))
        
        # Procesar el texto para crear documentos
        if use_splitter:
            documents = process_text_with_splitter(file_content, chunk_size, chunk_overlap)
        else:
            documents = process_text_data(file_content, single_document)
        
        if not documents:
            return jsonify({"status": "error", "message": "No se pudieron procesar los datos TXT"})
        
        # Crear o actualizar el índice FAISS
        if db is None:
            # Si no hay un índice existente, crear uno nuevo
            db = FAISS.from_documents(documents, embeddings)
        else:
            # Si ya hay un índice, agregar los nuevos documentos
            db.add_documents(documents)
        
        # Guardar el índice actualizado
        save_faiss_index()
        
        return jsonify({
            "status": "success", 
            "message": f"Se cargaron {len(documents)} documentos correctamente",
            "document_count": len(documents)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar el archivo: {str(e)}"})

# Endpoint para cargar documentos TXT desde texto
@app.route("/upload-txt-text", methods=["POST"])
def upload_txt_text():
    global db
    
    # Obtener los datos del cuerpo de la solicitud
    data = request.get_json()
    
    if not data or 'text' not in data:
        return jsonify({"status": "error", "message": "No se proporcionaron datos de texto"})
    
    try:
        # Obtener el texto y parámetros
        text = data['text']
        single_document = data.get('single_document', False)
        use_splitter = data.get('use_splitter', False)
        chunk_size = data.get('chunk_size', 1000)
        chunk_overlap = data.get('chunk_overlap', 200)
        
        # Procesar el texto para crear documentos
        if use_splitter:
            documents = process_text_with_splitter(text, chunk_size, chunk_overlap)
        else:
            documents = process_text_data(text, single_document)
        
        if not documents:
            return jsonify({"status": "error", "message": "No se pudieron procesar los datos de texto"})
        
        # Crear o actualizar el índice FAISS
        if db is None:
            # Si no hay un índice existente, crear uno nuevo
            db = FAISS.from_documents(documents, embeddings)
        else:
            # Si ya hay un índice, agregar los nuevos documentos
            db.add_documents(documents)
        
        # Guardar el índice actualizado
        save_faiss_index()
        
        return jsonify({
            "status": "success", 
            "message": f"Se cargaron {len(documents)} documentos correctamente",
            "document_count": len(documents)
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Error al procesar los datos de texto: {str(e)}"})

# Endpoint para verificar el estado del índice
@app.route("/check-index", methods=["GET"])
def check_index():
    global db
    
    if db is None:
        return jsonify({
            "status": "error", 
            "message": "No hay índice cargado"
        })
    
    try:
        # Obtener información del índice
        doc_count = db.index.ntotal  # Número de documentos en el índice
        
        return jsonify({
            "status": "success", 
            "message": "Índice cargado correctamente",
            "document_count": doc_count
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

# Endpoint para recargar el índice
@app.route("/reload-index", methods=["POST"])
def reload_index():
    global db
    
    try:
        # Recargar el índice
        success = load_faiss_index()
        
        if success:
            return jsonify({"status": "success", "message": "Índice recargado correctamente"})
        else:
            return jsonify({"status": "error", "message": "No se pudo recargar el índice"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/ask", methods=["POST"])
def ask():
    global db
    
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"answer": "No entendí tu pregunta."})

    if db is None:
        return jsonify({"answer": "No hay índice cargado. Ejecuta el ingest primero."})

    try:
        # Detectar si el usuario quiere crear un caso directamente
        case_keywords = ["crear caso", "generar ticket", "hacer ticket", "abrir caso", "nuevo caso"]
        for keyword in case_keywords:
            if keyword in question.lower():
                return jsonify({
                    "answer": "Entendido. Voy a redirigirte para crear un nuevo caso.",
                    "create_ticket": True
                })

        # Verificar si es un saludo básico
        if is_basic_greeting(question):
            return jsonify({
                "answer": get_greeting_response(question),
                "basic_greeting": True
            })

        # Primero verificar si la pregunta es válida
        if not is_valid_question(question):
            return jsonify({
                "answer": "No entendí tu pregunta. Si gustas, podemos crear un caso.",
                "suggest_ticket": True
            })

        # 🔹 Recuperar documentos más relevantes con puntuación de similitud
        docs_and_scores = db.similarity_search_with_score(question, k=6)
        relevant_docs = [d for d, score in docs_and_scores if score > 0.5]  # filtra por score

        # Si no hay documentos relevantes, sugerir crear un caso
        if not relevant_docs:
            return jsonify({
                "answer": "No tengo información sobre esto. Si gustas, podemos crear un caso.",
                "suggest_ticket": True
            })

        context = "\n\n".join(d.page_content for d in relevant_docs)
        prompt = BASE_PROMPT.format(context=context, question=question)

        # 🔹 Llamar al modelo Ollama
        respuesta = llm.invoke(prompt)
        respuesta_text = respuesta.strip() if isinstance(respuesta, str) else str(respuesta)
        
        # Limpiar la respuesta de frases no deseadas
        respuesta_text = clean_response(respuesta_text)
        
        # Verificar si la respuesta es útil
        if not is_response_useful(respuesta_text):
            return jsonify({
                "answer": "No pude encontrar una respuesta útil a tu pregunta. Si gustas, podemos crear un caso.",
                "suggest_ticket": True
            })

        # Si la respuesta es útil, agregar pregunta de confirmación
        return jsonify({
            "answer": respuesta_text,
            "ask_confirmation": True
        })

    except Exception as e:
        return jsonify({"answer": f"Ocurrió un error: {str(e)}"})

# Cargar el índice al iniciar la aplicación
load_faiss_index()

if __name__ == "__main__":
    # Asegúrate de tener corriendo el servicio de Ollama en tu máquina
    app.run(host="0.0.0.0", port=5000, debug=True)