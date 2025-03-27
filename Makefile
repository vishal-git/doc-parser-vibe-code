.PHONY: backend frontend

# Start FastAPI backend server
backend:
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Start Streamlit frontend
frontend:
	uv run streamlit run frontend/streamlit_app.py --server.port 8501

# Start both backend and frontend (requires GNU Make)
run: backend frontend
