import os
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from app import create_app, db

# Set up the app and the manager
app = create_app(os.getenv('FLASK_ENV') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)

# Add commands to the manager
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', Server(host='0.0.0.0', port=os.getenv('PORT', 5000)))

if __name__ == '__main__':
    manager.run()