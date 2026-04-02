import asyncio
import json
import logging
import os
import uuid
import random
import time
import pandas as pd
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional

from fastapi import FastAPI, BackgroundTasks
from sqlalchemy import create_engine, Column, String, Boolean, Integer, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base
from faker import Faker

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
)
logger = logging.getLogger("generator")

Base = declarative_base()
fake = Faker()

@dataclass
class GeneratorState:
    is_running: bool = False
    generated_count: int = 0
    target_count: int = 0
    start_time: Optional[float] = None
    last_batch_duration: float = 0.0

state = GeneratorState()
app = FastAPI(title="Subscription & Payment Generator")

# Подключения
SUB_DB_URL = os.getenv("SUB_DB_URL")
PAY_DB_URL = os.getenv("PAY_DB_URL")

engine_sub = create_engine(SUB_DB_URL, pool_pre_ping=True)
engine_pay = create_engine(PAY_DB_URL, pool_pre_ping=True)

_ERR_CODES = ("insufficient_funds", "card_expired", "do_not_honor", "expired_card")


def _transactions_from_orders(df_orders: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in df_orders.iterrows():
        order_status = row["status"]
        created = row["created_at"]
        if order_status == "paid":
            tx_status = "success"
            err = None
            raw = json.dumps({"captured": True, "gateway": "mock"})
        else:
            tx_status = random.choice(["declined", "error"])
            err = random.choice(_ERR_CODES)
            raw = json.dumps({"status": tx_status, "error_code": err, "gateway": "mock"})
        rows.append(
            {
                "id": uuid.uuid4(),
                "order_id": row["id"],
                "external_reference": f"gw_{uuid.uuid4()}",
                "status": tx_status,
                "error_code": err,
                "raw_response": raw,
                "created_at": created + timedelta(seconds=random.randint(0, 2)),
            }
        )
    return pd.DataFrame(rows)


# --- Задача генерации ---
async def data_generator_task(count: int, batch_size: int = 50):
    state.is_running, state.target_count, state.generated_count = True, count, 0
    state.start_time = time.time()
    
    logger.info(f"Task started: target={count}, batch_size={batch_size}")

    try:
        plans = pd.read_sql("SELECT id, price_amount, duration_days FROM plans", engine_sub)
        
        while state.is_running and state.generated_count < count:
            iter_start = time.time()
            curr_batch = min(batch_size, count - state.generated_count)
            
            user_ids = [uuid.uuid4() for _ in range(curr_batch)]
            now = datetime.now()
            
            df_users = pd.DataFrame({
                'id': user_ids,
                'email': [fake.unique.email() for _ in range(curr_batch)],
                'password_hash': 'hash',
                'created_at': [now - timedelta(minutes=random.randint(10, 5000)) for _ in range(curr_batch)]
            })

            sel_plans = plans.sample(n=curr_batch, replace=True).reset_index(drop=True)
            statuses = random.choices(['paid', 'failed'], weights=[0.8, 0.2], k=curr_batch)
            
            df_orders = pd.DataFrame({
                'id': [uuid.uuid4() for _ in range(curr_batch)],
                'user_id': user_ids,
                'plan_id': sel_plans['id'],
                'amount': sel_plans['price_amount'],
                'status': statuses,
                'created_at': df_users['created_at'] + timedelta(seconds=30)
            })

            paid_mask = df_orders['status'] == 'paid'
            df_subs = pd.DataFrame({
                'id': [uuid.uuid4() for _ in range(paid_mask.sum())],
                'user_id': df_orders.loc[paid_mask, 'user_id'],
                'plan_id': df_orders.loc[paid_mask, 'plan_id'],
                'status': 'active',
                'starts_at': df_orders.loc[paid_mask, 'created_at'],
                'ends_at': df_orders.loc[paid_mask, 'created_at'] + pd.to_timedelta(sel_plans.loc[paid_mask, 'duration_days'], unit='D'),
                'last_order_id': df_orders.loc[paid_mask, 'id']
            })

            df_transactions = _transactions_from_orders(df_orders)

            df_users.to_sql('users', engine_sub, if_exists='append', index=False, method='multi')
            df_orders.to_sql('orders', engine_pay, if_exists='append', index=False, method='multi')
            df_transactions.to_sql('transactions', engine_pay, if_exists='append', index=False, method='multi')
            if not df_subs.empty:
                df_subs.to_sql('subscriptions', engine_sub, if_exists='append', index=False, method='multi')
            
            state.generated_count += curr_batch
            state.last_batch_duration = time.time() - iter_start
            logger.info(f"Batch processed: {state.generated_count}/{count} in {state.last_batch_duration:.2f}s")
            
            await asyncio.sleep(0.05)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
    finally:
        state.is_running = False
        logger.info(f"Task finished: total={state.generated_count}")

# --- API ---
@app.post("/start")
async def start(background_tasks: BackgroundTasks, count: int = 100):
    if not state.is_running: 
        background_tasks.add_task(data_generator_task, count)
    return {"status": "started", "target": count}

@app.post("/stop")
async def stop():
    if state.is_running:
        state.is_running = False
        return {"status": "stopping"}
    return {"status": "not_running"}

@app.get("/status")
async def get_status():
    uptime = time.time() - state.start_time if state.is_running and state.start_time else 0
    return {
        "is_running": state.is_running,
        "progress": f"{state.generated_count}/{state.target_count}",
        "uptime_sec": round(uptime, 2)
    }
