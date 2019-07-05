import easyvvuq as uq
import chaospy as cp
import os
import sys
import pytest
from pprint import pprint

__copyright__ = """

    Copyright 2018 Robin A. Richardson, David W. Wright

    This file is part of EasyVVUQ

    EasyVVUQ is free software: you can redistribute it and/or modify
    it under the terms of the Lesser GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    EasyVVUQ is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Lesser GNU General Public License for more details.

    You should have received a copy of the Lesser GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
__license__ = "LGPL"


# If cannonsim has not been built (to do so, run the Makefile in tests/cannonsim/src/)
# then skip this test
if not os.path.exists("tests/cannonsim/bin/cannonsim"):
    pytest.skip(
        "Skipping cannonsim test (cannonsim is not installed in tests/cannonsim/bin/)",
        allow_module_level=True)


def test_sweep_sampler(tmpdir):

    # Set up a fresh campaign called "cannon"
    my_campaign = uq.Campaign(name='cannon', work_dir=tmpdir)

    # Define parameter space for the cannonsim app
    params = {
        "angle": {
            "type": "float",
            "min": 0.0,
            "max": 6.28,
            "default": 0.79},
        "air_resistance": {
            "type": "float",
            "min": 0.0,
            "max": 1.0,
            "default": 0.2},
        "height": {
            "type": "float",
            "min": 0.0,
            "max": 1000.0,
            "default": 1.0},
        "time_step": {
            "type": "float",
            "min": 0.0001,
            "max": 1.0,
            "default": 0.01},
        "gravity": {
            "type": "float",
            "min": 0.0,
            "max": 1000.0,
            "default": 9.8},
        "mass": {
            "type": "float",
            "min": 0.0001,
            "max": 1000.0,
            "default": 1.0},
        "velocity": {
            "type": "float",
            "min": 0.0,
            "max": 1000.0,
            "default": 10.0}}

    # Create an encoder and decoder for the cannonsim app
    encoder = uq.encoders.GenericEncoder(
        template_fname='tests/cannonsim/test_input/cannonsim.template',
        delimiter='#',
        target_filename='in.cannon')
    decoder = uq.decoders.SimpleCSV(
        target_filename='output.csv', output_columns=[
            'Dist', 'lastvx', 'lastvy'], header=0)

    # Add the cannonsim app
    my_campaign.add_app(name="cannonsim",
                        params=params,
                        encoder=encoder,
                        decoder=decoder)

    # Set the active app to be cannonsim (this is redundant when only one app
    # has been added)
    my_campaign.set_app("cannonsim")

    # Create a collation element for this campaign
    collater = uq.collate.AggregateSamples(average=False)
    my_campaign.set_collater(collater)

    # Make a sweep sampler
    sweep = {
        "angle": [0.1, 0.2, 0.3],
        "height": [2.0, 10.0],
        "velocity": [10.0, 10.1, 10.2]
    }
    sampler1 = uq.sampling.BasicSweep(sweep=sweep)

    print("Serialized sampler:", sampler1.serialize())

    # Set the campaign to use this sampler
    my_campaign.set_sampler(sampler1)

    # Draw first 5 samples
    my_campaign.draw_samples(num_samples=5)

    # Print the list of runs now in the campaign db
    print("List of runs added:")
    pprint(my_campaign.list_runs())
    print("---")

    # Encode all runs into a local directory
    pprint(
        f"Encoding all runs to campaign runs dir {my_campaign.get_campaign_runs_dir()}")
    my_campaign.populate_runs_dir()

    assert(len(my_campaign.get_campaign_runs_dir()) > 0)
    assert(os.path.exists(my_campaign.get_campaign_runs_dir()))
    assert(os.path.isdir(my_campaign.get_campaign_runs_dir()))

    # Local execution
    my_campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(
        "tests/cannonsim/bin/cannonsim in.cannon output.csv"))

    # Collate all data into one pandas data frame
    my_campaign.collate()
    print("data:", my_campaign.get_collation_result())

    # Save the state of the campaign
    state_file = tmpdir + "sweep_state.json"
    my_campaign.save_state(state_file)

    my_campaign = None

    # Load state in new campaign object
    reloaded_campaign = uq.Campaign(state_file=state_file, work_dir=tmpdir)
    reloaded_campaign.set_app("cannonsim")

    # Draw remaining samples, execute and collate
    print("Processing remaining samples...")
    reloaded_campaign.draw_samples()
    print("List of runs added:")
    pprint(reloaded_campaign.list_runs())
    print("---")

    reloaded_campaign.populate_runs_dir()
    reloaded_campaign.apply_for_each_run_dir(uq.actions.ExecuteLocal(
        "tests/cannonsim/bin/cannonsim in.cannon output.csv"))

    print("Completed runs:")
    pprint(reloaded_campaign.scan_completed())

    print("All completed?", reloaded_campaign.all_complete())

    reloaded_campaign.collate()
    print("data:\n", reloaded_campaign.get_collation_result())

    # Print the campaign log
    pprint(reloaded_campaign._log)


if __name__ == "__main__":
    test_sweep_sampler("/tmp/")