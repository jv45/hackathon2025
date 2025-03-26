FROM python:3.11

WORKDIR /app

#COPY prometheus_polling_agent.py /app/
COPY executeScript.py /app/

RUN pip install requests scikit-learn numpy autogen

#CMD ["python", "prometheus_polling_agent.py"]
CMD ["python", "executeScript.py"]
