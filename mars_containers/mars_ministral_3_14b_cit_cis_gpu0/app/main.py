# main.py on the mars_ministral_3_14b_cit_cis_gpu0
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from mars_ministral_3_14b_cit_cis_gpu0 import Mars_Ministral # Change here

info = {} # meta_information of agent                        # change bellow
info['agent_category']   = 'LLM'
info['agent_type']       = 'Mistral'
info['agent_model']      = '3'
info['agent_variant']    = '14B'
info['agent_host']       = 'cit_cis_gpu0'
info['agent_developper'] = 'shigeru.fujita@gmail.com' # email address is recommended
info['input_category']   = 'User requirements, resposes'
info['output_category']  = 'LLM results'
info['life_cycle']       = 'continue'
info['related_agents']   = 'mars_wbif'

agent = Mars_Ministral() # Source code: mars__ministral_3_14b_cit_cis_gpu0.py #change here

agent.set_meta_information(info) # meta_information is a Dict

""" ################################################################
Normally, we don't need to edit bellow.
""" ################################################################
@asynccontextmanager
async def lifespan(app: FastAPI):
    await agent.regist()
    await agent.start()
    yield
    
app = FastAPI(lifespan=lifespan)

app.include_router(agent.router)
