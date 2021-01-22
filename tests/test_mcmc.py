import os
import easyvvuq as uq
import numpy as np
import chaospy as cp

HOME = os.path.abspath(os.path.dirname(__file__))

def test_mcmc(tmp_path):
    campaign = uq.Campaign(name="mcmc", work_dir=tmp_path)
    params = {
        "x1": {"type": "float", "min": -5.0, "max": 5.0, "default": 0.0},
        "x2": {"type": "float", "min": -5.0, "max": 5.0, "default": 0.0},
        "out_file": {"type": "string", "default": "output.json"}
    }
    encoder = uq.encoders.GenericEncoder(
        template_fname=os.path.abspath("tutorials/rosenbrock.template"), delimiter="$", target_filename="input.json")
    decoder = uq.decoders.JSONDecoder("output.json", ["value"])
    campaign.add_app(name="mcmc", params=params, encoder=encoder, decoder=decoder)
    vary_init = {
        "x1": -3.0,
        "x2": 2.0
    }
    def q(x, b=0.5):
        return cp.J(cp.Normal(x['x1'], b), cp.Normal(x['x2'], b))
    sampler = uq.sampling.MCMCSampler(vary_init, q, 'value')
    campaign.set_sampler(sampler)
    action = uq.actions.ExecuteLocal("tutorials/rosenbrock.py input.json")
    ignored = sampler.mcmc_sampling(campaign, action, 200)
    import pdb; pdb.set_trace()
