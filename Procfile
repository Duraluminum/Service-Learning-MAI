web: python -c "import os; os.environ['RAILWAY_SERVICE_TYPE']='web'; import uvicorn; uvicorn.run('app.api:app', host='0.0.0.0', port=int(os.getenv('PORT', 8000)))"
worker: python main.py