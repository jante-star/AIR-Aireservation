import os
from dotenv import load_dotenv
load_dotenv()

from app import create_app
from app.config import DevelopmentConfig, ProductionConfig

env = os.getenv('FLASK_ENV', 'development')
config = DevelopmentConfig if env == 'development' else ProductionConfig

app = create_app(config)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=config.DEBUG)
