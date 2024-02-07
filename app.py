from arkitekt import register
import time
import numpy as np
from omero_ark.api.schema import ProjectFragment, DatasetFragment, ImageFragment
from arkitekt import register, startup
from mikro.api.schema import (
    RepresentationFragment,
    TableFragment,
    from_xarray,
    PhysicalSizeInput,
    ChannelInput,
    PlaneInput,
    AffineMatrix,
    OmeroRepresentationInput,
)
from omero_ark.api.schema import ImageFragment, get_image, ame
import xarray as xr
from fakts import get_current_fakts
import ezomero
import omero
from omero.gateway import BlitzGateway


@register
def yield_dataset_for_project(project: ProjectFragment) -> DatasetFragment:
    """Yield Dataset for Project

    Yield Dataset for Project


    """
    for dataset in project.datasets:
        yield dataset


@register
def yield_image_for_dataset(dataset: DatasetFragment) -> ImageFragment:
    """Yield Image for Dataset

    Yield Image for Dataset


    """
    for image in dataset.images:
        yield image


@register
def print_metadata(image: ImageFragment) -> None:
    """Print Metadata

    Yield Image for Dataset


    """
    image = conn.getObject("Image", image.id)

    metadata = {}

    physical_size = PhysicalSizeInput(
        x=image.getPixelSizeX(),
        y=image.getPixelSizeY(),
        z=image.getPixelSizeZ(),
    )

    # Acquisition data
    if image.getAcquisitionDate():
        metadata["Acquisition Date"] = str(image.getAcquisitionDate())

    # Channels information
    channels = []
    for c in image.getChannels():
        ch = ChannelInput(
            name=c.getLabel(),
            color=c.getColor().getHtml(),
            emmissionWavelength=c.getEmissionWave(),
            excitationWavelength=c.getExcitationWave(),
        )
        channels.append(ch)

    metadata["Channels"] = channels

    stage_label = image.getStageLabel()
    author = image.getAuthor()

    objective_settings = image.getObjectiveSettings()

    print(stage_label, author, objective_settings)

    print(physical_size)
    print(metadata)

    x = OmeroRepresentationInput(
        channels=channels,
        acquisitionDate=(
            str(image.getAcquisitionDate()) if image.getAcquisitionDate() else None
        ),
        physicalSize=physical_size,
    )

    print(x)


@register
def image_to_rep(image: ImageFragment) -> RepresentationFragment:
    """Convert an image

    Parameters
    ----------
    image : ImageFragment
        The image to convert

    Returns
    -------
    RepresentationFragment
        The representation
    """
    # Pixels and Channels will be loaded automatically as needed
    image, pixels = ezomero.get_image(conn, int(image.id))
    print(image.getName(), image.getDescription())
    physical_size = PhysicalSizeInput(
        x=image.getPixelSizeX(),
        y=image.getPixelSizeY(),
        z=image.getPixelSizeZ(),
    )

    print(physical_size)

    # Channels information
    channels = []
    for c in image.getChannels():
        ch = ChannelInput(
            name=c.getLabel(),
            color=c.getColor().getHtml(),
            emmissionWavelength=c.getEmissionWave(),
            excitationWavelength=c.getExcitationWave(),
        )
        channels.append(ch)

    stage_label = image.getStageLabel()
    author = image.getAuthor()

    objective_settings = image.getObjectiveSettings()

    omero = OmeroRepresentationInput(
        channels=channels,
        acquisitionDate=(
            str(image.getAcquisitionDate()) if image.getAcquisitionDate() else None
        ),
        physicalSize=physical_size,
    )
    print("rendered_image:", pixels)
    f = xr.DataArray(pixels, dims=["t", "z", "y", "x", "c"])

    return from_xarray(f, name=image.getName(), omero=omero)


@register()
def rep_to_image(image: RepresentationFragment) -> ImageFragment:
    """Convert a representation

    Parameters
    ----------
    image : RepresentationFragment
        The representation to convert

    Returns
    -------
    ImageFragment
        The image
    """

    thearray = image.data.transpose("x", "y", "z", "c", "t").compute().data

    x = ezomero.post_image(conn, thearray, image.name)
    print("Done")
    return get_image(x)


@startup
async def initialize_omero():
    global conn

    fakts = get_current_fakts()

    user = await ame()

    host = await fakts.aget("omero.host")
    port = await fakts.aget("omero.port")

    print("Will Act on behalf of this user")
    print(user, host, port)
    conn = BlitzGateway(
        user.omero_user.omero_username,
        user.omero_user.omero_password,
        host=host,
        port=port,
    )
    conn.connect()
