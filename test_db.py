from app import create_app, db

app = create_app()

with app.app_context():
    try:
        db.session.execute('SELECT 1')
        print("✅ Conexión a MySQL exitosa")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")

# Para ejecutar este script, ejecutar el siguiente comando:
#✅ Conexión a MySQL exitosa
#python test_db.py