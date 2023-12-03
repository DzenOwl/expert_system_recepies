from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from pydantic import BaseModel
from typing import TypedDict, Tuple, Set

import uvicorn

from recipes import Recipes


class MachineInput(BaseModel):
    facts: dict[int, str]
    rules: dict[int, tuple[int, set[int]]]
    selected: set[int]


app = FastAPI()

origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')


@app.get('/')
async def index():
    return RedirectResponse('/base')


@app.get('/base')
async def db_page(request: Request):
    return templates.TemplateResponse('database.html', {'request': request})


@app.get('/machine')
async def machine_page(request: Request):
    return templates.TemplateResponse('machine.html', {'request': request})


@app.post('/machine')
async def process_facts(machine_input: MachineInput):
    machine = Recipes(machine_input.facts, machine_input.rules)
    machine.set_background_facts(machine_input.selected)
    machine.find_all_avail_facts()
    return {
        'new_facts': machine.get_new_facts(),
        'new_facts_explained': machine.get_records_how_new_facts_was_received(),
    }


if __name__ == '__main__':
    uvicorn.run('server:app', host="127.0.0.1", port=8000, reload=True)
