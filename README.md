# ISL SignSpeak

Real-time Indian Sign Language recognition using a React frontend, a FastAPI backend, MediaPipe-style landmark features, and trained scikit-learn models.

## Problem Statement

Communication between Indian Sign Language users and non-signers is often limited by the lack of accessible, real-time translation tools. ISL SignSpeak addresses this gap by recognizing hand and body landmark patterns from a camera feed and converting them into predicted sign labels with confidence scores.

## What Is This Project?

ISL SignSpeak is a full-stack sign recognition application. The browser captures webcam input, extracts pose/hand landmark features, sends them to a Python backend over WebSocket, and displays the predicted sign from pre-trained machine learning models.

The repository also includes structured CSV landmark datasets and a training script for building new RandomForestClassifier `.pkl` models.

## Why Does It Exist?

This project exists to make sign language recognition easier to experiment with, demonstrate, and extend. It combines dataset organization, model training, model serving, and a usable frontend into one project so new signs and categories can be added without rebuilding the entire system.

## Key Features

- Real-time webcam-based ISL recognition workflow.
- FastAPI backend with REST and WebSocket endpoints.
- Multiple `.pkl` model support with automatic model discovery.
- Model upload, rename, delete, and reload endpoints.
- React + Vite frontend for camera feed, model selection, predictions, and sentence building.
- Structured CSV database organized by sign categories.
- Training script for generating new scikit-learn model files from landmark CSVs.
- Clean `.gitignore` for dependencies, caches, local environments, and build output.

## Screenshots

Add screenshots here after running the app locally.

Suggested files:

- `docs/screenshots/home.png`
- `docs/screenshots/prediction.png`
- `docs/screenshots/model-selector.png`

Example:

```md
![Home screen](docs/screenshots/home.png)
![Live prediction](docs/screenshots/prediction.png)
```

## Tech Stack

**Frontend**

- React
- Vite
- JavaScript
- CSS

**Backend**

- Python
- FastAPI
- Uvicorn
- WebSockets
- NumPy
- scikit-learn
- joblib
- pandas
- OpenCV
- MediaPipe

**Machine Learning**

- RandomForestClassifier
- Landmark CSV datasets
- Serialized `.pkl` models

## Project Structure

```text
ISL SignSpeak/
├── backend/
│   ├── main.py
│   ├── landmark_processor.py
│   ├── model_manager.py
│   ├── requirements.txt
│   └── models/
│       ├── 3fruit10.pkl
│       ├── Fruit2102.pkl
│       ├── Fruit2402.pkl
│       ├── Veg2102.pkl
│       ├── Veg2402.pkl
│       ├── VVKT.pkl
│       └── colors.pkl
├── database/
│   ├── README.md
│   ├── dataset_manifest.csv
│   └── Structured/
│       └── category-wise CSV datasets
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── public/
│   └── src/
│       ├── components/
│       ├── hooks/
│       ├── utils/
│       └── assets/
├── ml/
│   └── train_model.py
├── .gitignore
└── README.md
```

## How To Run

### Prerequisites

Install these before running the project:

- Git
- Python 3.11 or newer
- Node.js and npm
- A webcam-enabled browser
- Docker, optional

For dataset collection, also install:

- OpenCV Python
- MediaPipe

### 1. Clone The Repository

```bash
git clone https://github.com/Yog964/SignSpeak.git
cd SignSpeak
```

### 2. Run The Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

On macOS/Linux, activate the virtual environment with:

```bash
source .venv/bin/activate
```

Backend runs at:

```text
http://localhost:8000
```

### 3. Run The Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```text
http://localhost:5173
```

### 4. Run With Docker

Docker files are not included yet. After adding `Dockerfile` files for `backend` and `frontend`, and a root `docker-compose.yml`, the project can be run with:

```bash
docker compose up --build
```

Suggested service layout:

```text
backend  -> FastAPI on port 8000
frontend -> Vite app on port 5173
```

## Main Workflow

1. Start the FastAPI backend.
2. Backend loads all `.pkl` models from `backend/models`.
3. Start the React frontend.
4. Select an available model/category in the UI.
5. Allow webcam access in the browser.
6. Frontend extracts landmark features from the camera feed.
7. Landmarks are sent to `/ws/predict`.
8. Backend returns the predicted sign and confidence score.
9. The frontend displays the result and can build a sentence from predictions.

## API Endpoints

### REST

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/api/health` | Check backend health. |
| `GET` | `/api/models` | List loaded models. |
| `POST` | `/api/models/upload` | Upload a new `.pkl` model and reload models. |
| `PUT` | `/api/models/{model_id}` | Rename an existing model file. |
| `DELETE` | `/api/models/{model_id}` | Delete a model file and reload models. |

### WebSocket

```text
ws://localhost:8000/ws/predict
```

Client message:

```json
{
  "type": "predict",
  "model": "fruit2102",
  "landmarks": [0.43, 0.09, -0.14]
}
```

Server response:

```json
{
  "type": "prediction",
  "sign": "apple",
  "confidence": 85.2,
  "category": "Fruit2102"
}
```

## Useful Scripts

### Frontend

```bash
npm run dev
npm run build
npm run preview
npm run lint
```

### Backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Train A Model

```bash
cd ml
python train_model.py --data-dir ../database/Structured/Vedant_Fruits --output ../backend/models/fruits.pkl --category Fruits
```

### Collect A Dataset

The dataset collection script used for this project is:

```text
ml/collect_dataset.py
```

It records webcam frames, extracts MediaPipe Pose landmarks, and saves them as a labeled CSV file.

```bash
cd ml
python collect_dataset.py --action hello --output ../database/Structured/GeneralAction/hello.csv --duration 8
```

Preview camera without saving:

```bash
python collect_dataset.py --action hello --output ../database/Structured/GeneralAction/hello.csv --preview-only
```

## Testing

No dedicated automated test suite is currently included.

Recommended checks:

```bash
cd frontend
npm run lint
npm run build
```

```bash
cd backend
python -m py_compile main.py landmark_processor.py model_manager.py
```

Manual test:

1. Start backend and frontend.
2. Open `http://localhost:5173`.
3. Allow webcam access.
4. Select a model.
5. Verify predictions appear without backend errors.

## Notes

- Model files must be stored in `backend/models` and use the `.pkl` extension.
- The backend derives model IDs from lowercase filenames without `.pkl`.
- Dataset CSV files should include landmark feature columns and an `action` label column.
- Use `ml/collect_dataset.py` to collect new landmark CSV files.
- The structured database is stored in `database/Structured`.
- `node_modules`, Python caches, virtual environments, and build outputs are intentionally ignored.
- Large future datasets or model files may require Git LFS if they exceed GitHub file limits.

## License

No license file is currently included. Add a `LICENSE` file before using or distributing this project publicly.
