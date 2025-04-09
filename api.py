import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import resend
from datetime import datetime

load_dotenv()

app = Flask(__name__)


CORS(app, resources={r"/*": {"origins": [
    "https://parquelipangue.cl",
    "http://localhost:3000"]}})

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# print("🔑 RESEND_API_KEY =", os.getenv("RESEND_API_KEY"))


@app.before_request
def log_origin():
    print(f"📡 Origin de la solicitud: {request.headers.get('Origin')}")



# test connection
@app.route("/test-connection", methods=["GET"])
def test_connection():
    print("✅Received request to test connection")
    return jsonify({
        "status": "ok", 
        "message": "Conexión exitosa con la API de Parque Lipangue 🚀"
        }), 200
  
    

@app.route("/send-intern-email", methods=["POST"])
def ordereat_send_intern_email():
    data = request.json

    file_path = os.path.join(os.path.dirname(__file__), "./templates/intern-email", "intern-email.html")

    with open(file_path, "r", encoding="utf-8") as file:
        
        email_template = file.read()
        
        template_vars = {
            "{{from_name}}": data.get("fromName", ""),
            "{{from_email}}": data.get("fromEmail", ""),
            "{{from_phone}}": data.get("fromPhone", ""),
            "{{from_event_type}}": data.get("fromEventType", ""),
            "{{from_event_date}}": data.get("fromEventDate", ""),
            "{{from_people}}": data.get("fromPeople", ""),
            "{{from_message}}": data.get("fromMessage", "(No se proporcionó mensaje)"),
            "{{timestamp}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for var, value in template_vars.items():
            email_template = email_template.replace(var, value)
    
    try:
        resend.api_key = RESEND_API_KEY
        if not resend.api_key:
            raise ValueError("API key not found in environment variables.")
        
        params_for_email = {
            "from": "Parque Lipangue Web <contacto@parquelipangue.cl>",
            "to": ["contacto@parquelipangue.cl", "angelica.apparcel@gmail.com", "claudiaurrutiav@gmail.com"],
            "subject": f"Nuevo mensaje de {data.get('fromName', '** SIN NOMBRE **')}",
            "html": email_template,
        }
        
        params: resend.Emails.SendParams = params_for_email
        
        email = resend.Emails.send(params)
        
        if email:
            print("✅ Correo interno enviado correctamente")
            
        return jsonify({
            "message": "Correo interno enviado a ordereat ✅",
            "status": "ok"
            }), 200
    except Exception as e:
        print("❌ Error al enviar el correo:", str(e))
        return jsonify({"error": "❌ No se pudo enviar el correo interno"}), 500


@app.route("/send-thanks-email", methods=["POST"])
def ordereat_send_email():
    data = request.json

    file_path = os.path.join(os.path.dirname(__file__), "./templates/thanks-email", "thanks-email.html")
    
    with open(file_path, "r", encoding="utf-8") as file:
        
        email_template = file.read()
        
        template_vars = {
            "{{from_name}}": data.get("fromName", "")
        }
        
        for var, value in template_vars.items():
            email_template = email_template.replace(var, value)

    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        params: resend.Emails.SendParams = {
            "from": "Parque Lipangue <contacto@parquelipangue.cl>",
            "to": [data['fromEmail']],
            "subject": "Hemos recibido tu mensaje!",
            "html": email_template,
        }
        
        email = resend.Emails.send(params)
        
        if email:
            print("✅ Correo de agradecimiento enviado correctamente:")
        
        return jsonify({"message": "Correo de agradecimiento enviado correctamente ✅"}), 200
    
    except Exception as e:
        print("❌ Error al enviar el correo de agradecimiento:", str(e))
        return jsonify({"error": r"No se pudo enviar el correo de agradecimiento ❌. Error: {str(e)}"}), 500



if __name__ == "__main__":
    app.run(host='0.0.0.0', port="5001")
    