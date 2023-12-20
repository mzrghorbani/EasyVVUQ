#!/usr/bin/env python3

# These code contains material and example problems in thermodynamics.
# This code was used from https://kyleniemeyer.github.io/computational-thermo/
# under Creative Commons Attribution 4.0 International License.

# Steam equilibrating with liquid water
######################################
# Accident scenario: steam leaks into a rigid, insulated tank that is partially filled with water.
# The steam and liquid water are not initially at thermal equilibrium, though they are at the same pressure.
# The steam is at temperature 600 C and pressure 20 MPa.
# The liquid water is initially at 40 C and pressure 20 MPa.
# The total volume of the tank is 10 m^3
# And the volume of the liquid water initially in the tank is 1 m^3.

# Eventually, the contents of the tank reach a uniform temperature and pressure.
# The tank is well-insulated and rigid.

# Problem: Determine the final temperature and pressure of the water in the tank.

import dataclasses
import json
import sys

import numpy as np
import cantera as ct
from pint import UnitRegistry


@dataclasses.dataclass
class Config:
    steamT: float  # Initial steam temperature (degC)
    steamP: float  # Initial steam pressure (MPa)
    liquidT: float  # Initial liquid temperature (degC)
    liquidP: float  # Initial liquid pressure (MPa)
    liquidV: float  # Liquid volume initially in the tank (m^3)
    tankV: float  # Volume of the tank (m^3)

    @staticmethod
    def decode(cfg):
        return Config(**cfg)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("ERROR: Config file not provided")
        sys.exit(1)
    with open(sys.argv[1]) as fh:
        config = json.load(fh, object_hook=Config.decode)

    # Setup UnitRegistry to handle unit conversion and manipulation
    ureg = UnitRegistry()
    Q_ = ureg.Quantity

    # Setup Cantera environment providing steam and liquid
    steam = ct.Water()
    temp_steam1 = Q_(config.steamT, "degC")
    pres1 = Q_(config.steamP, "MPa")
    steam.TP = temp_steam1.to("K").magnitude, pres1.to("Pa").magnitude
    steam()

    liquid = ct.Water()
    temp_liquid1 = Q_(config.liquidT, "degC")
    pres_liquid1 = Q_(config.liquidP, "MPa")
    liquid.TP = temp_liquid1.to("K").magnitude, pres_liquid1.to("Pa").magnitude
    liquid()

    # "Calculate the mass of liquid water in the tank, and then determine the volume and mass of steam"
    vol_tank = Q_(config.tankV, "meter^3")
    vol_liquid1 = Q_(config.liquidV, "meter^3")
    mass_liquid1 = vol_liquid1 / Q_(liquid.v, "m^3/kg")
    print(f"Mass of liquid at state 1: {mass_liquid1: .2f}")
    vol_steam1 = vol_tank - vol_liquid1
    mass_steam1 = vol_steam1 / Q_(steam.v, "m^3/kg")
    print(f"Mass of steam at state 1: {mass_steam1: .2f}")
    mass_1 = mass_liquid1 + mass_steam1
    print(f"Total mass of system: {mass_1: .2f}")

    mass_2 = mass_1
    spec_vol2 = vol_tank / mass_2
    print(f"Specific volume of state 2: {spec_vol2: .2e}")
    int_energy2 = (Q_(liquid.u, "J/kg") * mass_liquid1 + Q_(steam.u, "J/kg") * mass_steam1) / mass_2
    int_energy2.ito("kilojoule/kg")
    print(f"Internal energy of state 2: {int_energy2: .2f}")
    water_equilibrium = ct.Water()
    water_equilibrium.UV = int_energy2.to("J/kg").magnitude, spec_vol2.to("m^3/kg").magnitude
    water_equilibrium()

    # "At equilibrium, the tank contains a mixture of saturated liquid and vapor, with temperature and pressure"
    final_temperature = Q_(water_equilibrium.T, "K")
    final_pressure = Q_(water_equilibrium.P, "Pa")

    print(f"Final temperature: {final_temperature: .2f}")
    print(f"Final pressure: {final_pressure.to(ureg.MPa): .2f}")

    with open("output.json", "w+") as fh:
        content = json.dumps({"finalT": final_temperature.magnitude, "finalP": final_pressure.to(ureg.MPa).magnitude})
        fh.write(content)