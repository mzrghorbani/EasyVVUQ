import os
import numpy as np
import easyvvuq as uq
import chaospy as cp
from easyvvuq.actions import CreateRunDirectory, Encode, ExecuteLocal, Decode, Actions

WORK_DIR = '/tmp'

params = {
    "steamT": {"type": "integer", "default": 600},
    "steamP": {"type": "integer", "default": 30},
    "liquidT": {"type": "float", "default": 10},
    "liquidP": {"type": "float", "default": 20},
    "liquidV": {"type": "integer", "default": 2},
    "tankV": {"type": "integer", "default": 15},
}

vary = {
    "steamT": cp.DiscreteUniform(100, 600),
    "steamP": cp.DiscreteUniform(5, 30),
    "liquidT": cp.Normal(15, 3),
    "liquidP": cp.Normal(10, 2),
    "liquidV": cp.DiscreteUniform(1, 2),
    # "tankV": cp.Normal(15, 2) # Tank V is const
}

encoder = uq.encoders.GenericEncoder(
    template_fname="./steam-water-equilibrium/config.template", delimiter="$", target_filename="input.json"
)

decoder = uq.decoders.JSONDecoder(
    target_filename="output.json", output_columns=["finalT", "finalP"]
)

execute = ExecuteLocal(f"python3 {os.getcwd()}/steam-water-equilibrium/steam-water-equilibrium.py input.json")

actions = Actions(CreateRunDirectory(WORK_DIR, flatten=True), 
                  Encode(encoder), 
                  execute, 
                  Decode(decoder))

campaign = uq.Campaign(name="steam-water", params=params, actions=actions,
                       work_dir=WORK_DIR, verify_all_runs=True)

### Sampler set
# sampler = uq.sampling.SCSampler(vary=vary, polynomial_order=1)
sampler = uq.sampling.PCESampler(vary=vary, polynomial_order=1)
campaign.set_sampler(sampler)

# with QCGPJPool(
#     template=EasyVVUQParallelTemplate(),
#     template_params={
#         "venv": r"/home/<username>/.pyenv/versions/3.10.7/envs/steam-water"
#     },
# ) as qcgpj:
#     campaign.execute(pool=qcgpj).collate()

campaign.execute().collate()
