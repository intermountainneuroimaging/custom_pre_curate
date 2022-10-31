"""Flywheel gear context parser."""


def parse_config(gear_context):
    """Parse gear config.

    Args:
        gear_context (flywheel_gear_toolkit.GearToolkitContext): context

    Returns:
        (tuple): tuple containing
            - parent container
            - dictionary of input files
            - optional requirements file
    """
    container_id = gear_context.destination["id"]
    container = gear_context.client.get_container(container_id)

    # if run as analysis gear...
    if "gear_info" in container:
        get_parent_fn = getattr(gear_context.client, f"get_{container.parent.type}")
        parent = get_parent_fn(container.parent.id)
    else:
        # if utility gear, "destination id" from config is working container (e.g. acquisition, session)
        parent = container


    input_file_one = gear_context.get_input_path("additional-input-one")
    input_files = {
        "additional_input_one": input_file_one
    }
    return parent, input_files


def get_parent_id(container):
    parents = container.parents
    for pp in parents.attribute_map:
        if parents[pp] is not None:
            return parents[pp]
