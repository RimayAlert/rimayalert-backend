import firebase_admin
from firebase_admin import credentials, messaging

# Ruta dentro de WSL
cred = credentials.Certificate(
    "/home/developer/FAZQ/RimayAlert/secrets/rimayalertback-firebase-admin-sdk-key.json"
)

# Inicializar Firebase Admin
firebase_admin.initialize_app(cred)

# Token real del móvil
MOBILE_TOKEN = "fI-X2J1hTvOZc5jTXqTFEs:APA91bGAsmUi_r5txhy1_nLreyxaZpIekIBMSoGPJ7qSoK4To8H493baHNaQtATYp3EZCcWMaPXh4uZAggGLR-sk_J7ymisGTwrs0Q6Blbb9bOUgZ_zsA7M"

# Crear y enviar notificación
msg = messaging.Message(
    notification=messaging.Notification(
        title="TEST RIMAY",
        body="Prueba directa desde script.py"
    ),
    token=MOBILE_TOKEN
)

response = messaging.send(msg)
print("Notificación enviada:", response)
