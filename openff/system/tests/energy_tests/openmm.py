from typing import Dict

import numpy as np
from simtk import openmm, unit

from openff.system.components.system import System


def get_openmm_energies(
    off_sys: System,
    round_positions=None,
) -> Dict:

    omm_sys: openmm.System = off_sys.to_openmm()

    force_names = {force.__class__.__name__ for force in omm_sys.getForces()}
    group_to_force = {i: force_name for i, force_name in enumerate(force_names)}
    force_to_group = {force_name: i for i, force_name in group_to_force.items()}

    for force in omm_sys.getForces():
        force_name = force.__class__.__name__
        force.setForceGroup(force_to_group[force_name])

    integrator = openmm.VerletIntegrator(1.0 * unit.femtoseconds)
    context = openmm.Context(omm_sys, integrator)

    box_vectors = off_sys.box.magnitude * unit.nanometer
    context.setPeriodicBoxVectors(*box_vectors)

    positions = off_sys.positions.magnitude * unit.nanometer
    if round_positions is not None:
        rounded = np.round(positions, round_positions)
        context.setPositions(rounded)
    else:
        context.setPositions(positions)

    force_groups = {force.getForceGroup() for force in context.getSystem().getForces()}

    omm_energies = dict()

    for force_group in force_groups:
        state = context.getState(getEnergy=True, groups={force_group})
        omm_energies[group_to_force[force_group]] = state.getPotentialEnergy()
        del state

    del context
    del integrator

    return omm_energies
