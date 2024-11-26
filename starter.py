from main import app
from flask_socketio import SocketIO
from main.models import db  # Assuming your models are in a file named `models.py`
from main.admin_routes import seed_categories  # Import your seeding function

if __name__ == '__main__':
    with app.app_context():
        # Seed the database
        seed_categories()
        print("Seeding completed.")

    # Run the app
    socketio = SocketIO(app)
    socketio.run(app, debug=True, port=1750, use_reloader=True)