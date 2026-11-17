# main.py on the mars_wbif
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_wbif import MarsWbIF

info = {} # meta_information of agent
info['agent_category']   = 'User interface'
info['agent_type']       = 'Web browser'
info['agent_developper'] = 'shigeru.fujita@gmail.com' # email address is recommended
info['input_category']   = 'User requirements, resposes'
info['output_category']  = 'LLM results'
info['life_cycle']       = 'continue'
info['related_agents']   = 'mars_Ministral_3_14B_cit_cis_gpu0'

wb = MarsWbIF() # Source code: mars_wbif.py
wb.set_meta_information(info) # meta_information is a Dict

@asynccontextmanager
async def lifespan(app: FastAPI):
    await wb.regist()
    await wb.start()
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(wb.router)
