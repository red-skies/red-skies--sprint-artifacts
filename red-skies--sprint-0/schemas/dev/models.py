from dataclasses import dataclass
from dataclasses import field
from enum import IntEnum


class EntityType(IntEnum):
    """Represents the type of an entity."""

    NONE = 0
    """Unknown type."""
    AIRCRAFT = 1
    """Entity of type `Aircraft`."""
    RADAR = 2
    """Entity of type `Radar`."""


@dataclass
class Position:
    """Represents a WGS84 geodetic coordinate."""

    latitude: float = 0.0
    """Latitude (degrees), in the range [-90, 90]."""
    longitude: float = 0.0
    """Longitude (degrees), in the range [-180, 180]."""
    altitude: float = 0.0
    """Altitude (meters)."""


@dataclass
class Attitude:
    """Represents the orientation of a body in space."""

    roll: float = 0.0
    """Rotation around the longitudinal axis (degrees)."""
    pitch: float = 0.0
    """Rotation around the lateral axis (degrees)."""
    yaw: float = 0.0
    """Rotation around the vertical axis (degrees)."""


@dataclass
class BodyVelocity:
    """Represents a velocity vector, expressed relative to the body frame."""

    forward: float = 0.0
    """Velocity along the forward axis (m/s)."""
    right: float = 0.0
    """Velocity along the right axis (m/s)."""
    down: float = 0.0
    """Velocity along the down axis (m/s)."""


@dataclass
class LocalVelocity:
    """Represents a velocity vector, expressed relative to the local NED frame."""

    north: float = 0.0
    """Velocity along the north axis (m/s)."""
    east: float = 0.0
    """Velocity along the east axis (m/s)."""
    down: float = 0.0
    """Velocity along the down axis (m/s)."""


@dataclass
class Detection:
    """Represents a detection made by an entity."""

    uid: str = str()
    """The UID of the detected entity."""
    distance: float = 0.0
    """The 3D distance from the detector to the detected entity (meters)."""
    azimuth: float = 0.0
    """
    The compass heading from the detector towards the detected entity (degrees).
    Note that this value does not take the detector's heading into account.
    """


@dataclass
class DetectionReport:
    """Stores a collection of detections."""

    detections: dict[str, Detection] = field(default_factory=dict)
    """Detections made by an entity, keyed by the UID of a detected entity."""


@dataclass
class EntityConfig:
    """Initial configuration for an entity."""

    position: Position = field(default_factory=Position)
    """Initial geodetic position (WGS84)."""
    heading: float = 0.0
    """Initial heading (degrees)."""
    speed: float = 0.0
    """Initial speed (m/s)."""
    detection_range: float = 0.0
    """Maximum detection range (meters). Modeled as a sphere around the entity."""


@dataclass
class EntityState:
    """Represents the state of an entity"""

    uid: str = str()
    """The UID of the entity."""
    type: EntityType = EntityType.NONE
    """The type of the entity."""
    position: Position = field(default_factory=Position)
    """Geodetic position (WGS84)."""
    attitude: Attitude = field(default_factory=Attitude)
    """Orientation in space (RPY)."""
    body_velocity: BodyVelocity = field(default_factory=BodyVelocity)
    """Velocity with respect to the body frame (m/s). """
    local_velocity: LocalVelocity = field(default_factory=LocalVelocity)
    """Velocity with respect to the local NED frame (m/s). """
    speed: float = 0.0
    """Speed (m/s)."""
    report: DetectionReport = field(default_factory=DetectionReport)
    """Report on detections made by the entity."""


@dataclass
class SimulationState:
    """Represents the state of the simulation."""

    time: float = 0.0
    """Simulation time (seconds)."""
    frame: int = 0
    """Simulation frame, i.e., the number of times the simulation has been ticked."""
    entities: dict[str, EntityState] = field(default_factory=dict)
    """Mapping of entity UIDs to their respective state."""
