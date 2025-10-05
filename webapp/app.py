from threading import Thread
import os
from types import SimpleNamespace
from flask import Flask, render_template, jsonify

app = Flask(__name__)


CONFIG_PATH = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'onioningestor.yml'))


def load_config():
    try:
        import yaml
    except Exception:
        return {}
    try:
        with open(CONFIG_PATH, 'r') as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


@app.route('/')
def index():
    # Placeholder: show a simple dashboard and run control
    return render_template('index.html')


@app.route('/start-ingest', methods=['POST'])
def start_ingest():
    # Start a background thread to run ingestion once.
    def _run():
        try:
            # Import Ingestor class and run a single iteration.
            from onioningestor import Ingestor
            cfg_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'onioningestor.yml'))
            args = SimpleNamespace(configFile=cfg_path, logLevel='INFO')
            ing = Ingestor(args)
            # run a single ingestion iteration
            ing.run_once()
        except Exception:
            # swallow errors to keep the web thread alive; in future log properly
            pass

    Thread(target=_run, daemon=True).start()
    return jsonify({'status': 'started'})


@app.route('/api/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    cfg = load_config()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
