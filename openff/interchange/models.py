from typing import Optional, Tuple

from openff.units import unit
from pydantic import BaseModel, Field

from openff.interchange.types import custom_quantity_encoder, json_loader


class DefaultModel(BaseModel):
    """A custom Pydantic model used by other components."""

    class Config:
        json_encoders = {
            unit.Quantity: custom_quantity_encoder,
        }
        json_loads = json_loader
        validate_assignment = True
        arbitrary_types_allowed = True


class TopologyKey(DefaultModel):
    """A unique identifier of a segment of a chemical topology.

    These refer to a single portion of a chemical graph, i.e. a single valence term,
    (a bond, angle, or dihedral) or a single atom. These target only the information in
    the chemical graph and do not store physics parameters. For example, a TopologyKey
    corresponding to a bond would store the indices of the two atoms that compose the
    bond, but not the force constant or equilibrium bond length as determined by the
    force field.

    Examples
    --------

    Create a TopologyKey identifying some speicfic angle

    .. code-block:: pycon

        >>> from openff.interchange.models import TopologyKey
        >>> this_angle = TopologyKey(atom_indices=(2, 1, 3))
        >>> this_angle
        TopologyKey(atom_indices=(2, 1, 3), mult=None)

    Create a TopologyKey indentifying just one atom

    .. code-block:: pycon

        >>> this_atom = TopologyKey(atom_indices=(4,))
        >>> this_atom
        TopologyKey(atom_indices=(4,), mult=None)

    Layer multiple TopologyKey objects that point to the same torsion

    .. code-block:: pycon

        >>> key1 = TopologyKey(atom_indices=(1, 2, 5, 6), mult=0)
        >>> key2 = TopologyKey(atom_indices=(1, 2, 5, 6), mult=1)
        >>> assert key1 != key2

    """

    atom_indices: Tuple[int, ...] = Field(
        tuple(), description="The indices of the atoms occupied by this interaction"
    )
    mult: Optional[int] = Field(
        None, description="The index of this duplicate interaction"
    )

    def __hash__(self):
        return hash((self.atom_indices, self.mult))


class PotentialKey(DefaultModel):
    """A unique identifier of an instance of physical parameters as applied to a segment of a chemical topology.

    These refer to a single term in a force field as applied to a single segment of a chemical
    topology, i.e. a single atom or dihedral. For example, a PotentialKey corresponding to a
    bond would store the the force constant and the equilibrium bond length as determined by
    the force field. These keys to not have direct knowledge of where in a topology they have been
    applied.

    Examples
    --------

    Create a PotentialKey corresponding to the parameter with id `b55` in OpenFF "Parsley" 1.0.0

    .. code-block:: pycon

        >>> from openff.interchange.models import PotentialKey
        >>> from openff.toolkit.typing.engines.smirnoff import ForceField
        >>> parsley = ForceField("openff-1.0.0.offxml")
        >>> param = parsley["Bonds"].get_parameter({"id": "b55"})[0]
        >>> bond_55 = PotentialKey(id=param.smirks)
        >>> bond_55
        PotentialKey(id='[#16X4,#16X3:1]-[#8X2:2]', mult=None, associated_handler=None)

    Create a PotentialKey corresponding to the angle parameters in OPLS-AA defined
    between atom types opls_135, opls_135, and opls_140

    .. code-block:: pycon

        >>> oplsaa_angle = PotentialKey(id="opls_135-opls_135-opls_140")
        >>> oplsaa_angle
        PotentialKey(id='opls_135-opls_135-opls_140', mult=None, associated_handler=None)

    """

    id: str = Field(
        ...,
        description="A unique identifier of this potential, i.e. a SMARTS pattern or an atom type",
    )
    mult: Optional[int] = Field(
        None, description="The index of this duplicate interaction"
    )
    associated_handler: Optional[str] = Field(
        None,
        description="The type of handler this potential key is associated with, "
        "i.e. 'Bonds', 'vdW', or 'LibraryCharges",
    )

    def __hash__(self):
        return hash((self.id, self.mult))
