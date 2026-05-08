FROM python:3.9-slim
WORKDIR /app
RUN pip install flask requests
COPY . .
EXPOSE 5000
CMD ["python", "frontend_app.py"]