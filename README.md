# Monorepo

A monorepo containing a Next.js frontend and FastAPI backend.

## Project Structure

```
monorepo/
├── frontend/          # Next.js + TypeScript frontend
│   ├── src/
│   │   ├── app/       # Next.js App Router
│   │   └── components/
│   ├── package.json
│   ├── tsconfig.json
│   └── tailwind.config.js
├── backend/           # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
└── README.md
```

## Getting Started

### Frontend (Next.js)

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Backend (FastAPI)

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the development server:
```bash
python main.py
```

The backend API will be available at `http://localhost:8000`

## Features

- **Frontend**: Next.js 14 with TypeScript, Tailwind CSS, and App Router
- **Backend**: FastAPI with automatic API documentation, CORS support, and Pydantic models
- **CORS**: Configured to allow frontend-backend communication
- **Type Safety**: Full TypeScript support in frontend, Pydantic models in backend

## API Documentation

Once the backend is running, you can access:
- Interactive API docs: `http://localhost:8000/docs`
- ReDoc documentation: `http://localhost:8000/redoc`
