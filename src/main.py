from fastapi import FastAPI

app = FastAPI()

@app.post("/clientes/{client_id}/transacoes")
def create_transaction(client_id):
    pass


@app.get("/clientes/{client_id}/extrato")
def get_user_statement(client_id):
    pass
