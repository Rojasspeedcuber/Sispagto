# app.py

import typer
from typing_extensions import Annotated
from database import SessionLocal, engine
from models import Base
import logic
import reports

app = typer.Typer()

# Create database tables on startup
Base.metadata.create_all(bind=engine)

@app.command()
def add_credor(
    doc: Annotated[str, typer.Option(help="CPF/CNPJ of the creditor")],
    name: Annotated[str, typer.Option(help="Name of the creditor")]
):
    """
    Registers a new Creditor in the system. 
    """
    db = SessionLocal()
    try:
        credor = logic.create_credor(db, credor_doc=doc, nome=name)
        print(f"Creditor '{credor.credor_nome}' with document '{credor.credor_doc}' created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@app.command()
def add_product(
    description: Annotated[str, typer.Option(help="Description of the product/service")],
    value: Annotated[int, typer.Option(help="Value of one unit of the product/service")]
):
    """
    Registers a new Product/Service. 
    """
    db = SessionLocal()
    try:
        product = logic.create_produto_servico(db, descricao=description, valor=value)
        print(f"Product '{product.prod_serv_descricao}' created with ID {product.prod_serv_n}.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@app.command()
def add_contract(
    number: Annotated[str, typer.Option(help="Contract number")],
    creditor_doc: Annotated[str, typer.Option(help="Creditor's document (CPF/CNPJ)")],
    start_date: Annotated[str, typer.Option(help="Contract start date (YYYY-MM-DD)")],
    end_date: Annotated[str, typer.Option(help="Contract end date (YYYY-MM-DD)")],
    value: Annotated[int, typer.Option(help="Total value of the contract")]
):
    """
    Registers a new Contract. 
    """
    db = SessionLocal()
    try:
        contract = logic.create_contrato(db, contrato_n=number, credor_doc=creditor_doc,
                                       data_ini=start_date, data_fim=end_date, valor=value)
        print(f"Contract '{contract.contrato_n}' created successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

@app.command()
def add_payment(
    date: Annotated[str, typer.Option(help="Payment date (YYYY-MM-DD)")],
    period: Annotated[str, typer.Option(help="Budget period for the payment")],
    value: Annotated[int, typer.Option(help="Payment amount")],
    product_id: Annotated[int, typer.Option(help="ID of the product/service")],
    quantity: Annotated[int, typer.Option(help="Quantity of the product/service")],
    creditor_doc: Annotated[str, typer.Option(help="Creditor's document (CPF/CNPJ)")],
    contract_number: Annotated[str, typer.Option(help="Associated contract number")] = None,
    payment_type: Annotated[str, typer.Option(help="Payment type (nf, recibo, fatura, boleto)")] = None,
    doc_number: Annotated[str, typer.Option(help="Document number (e.g., NF number)")] = None,
    doc_date: Annotated[str, typer.Option(help="Document date (YYYY-MM-DD)")] = None
):
    """
    Registers a new Payment. 
    """
    db = SessionLocal()
    try:
        payment = logic.create_payment(
            db=db,
            data=date,
            periodo=period,
            valor=value,
            prod_serv_n=product_id,
            prod_serv_qtd=quantity,
            credor_doc=creditor_doc,
            contrato_n=contract_number,
            tipo_pagamento=payment_type,
            doc_n=doc_number,
            doc_data=doc_date
        )
        print(f"Payment with ID {payment.pagto_id} created successfully.")
    except Exception as e:
        print(f"Error creating payment: {e}")
    finally:
        db.close()

@app.command()
def generate_report(
    start_date: Annotated[str, typer.Option(help="Filter by start date (YYYY-MM-DD)")] = None,
    end_date: Annotated[str, typer.Option(help="Filter by end date (YYYY-MM-DD)")] = None,
    period: Annotated[str, typer.Option(help="Filter by payment period")] = None,
    creditor_doc: Annotated[str, typer.Option(help="Filter by creditor document")] = None,
    contract_number: Annotated[str, typer.Option(help="Filter by contract number")] = None,
):
    """
    Generates a financial report in Excel format. 
    """
    db = SessionLocal()
    try:
        file_path = reports.generate_report(
            db,
            data_inicio=start_date,
            data_fim=end_date,
            periodo=period,
            credor_doc=creditor_doc,
            contrato_n=contract_number
        )
        print(f"Report successfully generated at: {file_path}")
    except Exception as e:
        print(f"Error generating report: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    app()