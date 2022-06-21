#!/usr/bin/env python3
"""Custom pre curate entrypoint."""
import logging
import flywheel
import pandas as pd
import sys
from io import StringIO
from flywheel_gear_toolkit.utils.curator import HierarchyCurator
from flywheel_gear_toolkit.utils import walker
from utils import parser
from flywheel_gear_toolkit import GearToolkitContext
import json

log = logging.getLogger(__name__)

class Curator(HierarchyCurator):

    def curate_project(self, project: flywheel.Project):
        pass

    def curate_subject(self, subject: flywheel.Subject):
        pass

    def curate_session(self, session: flywheel.Session):
        pass

    def curate_acquisition(self, acquisition: flywheel.Acquisition):
        parents = acquisition.parents
        # client = flywheel.Client('flywheel.rc.colorado.edu:brWEShFriXpt1yZs7y')
        # current_project = client.get(parents.project)

        current_project = gtk_context.client.get(parents.project)
        contents_of_csv = current_project.read_file('acquisition_label_remapping.csv')
        # decode the UTF-8 file string
        decode = contents_of_csv.decode('utf-8')
        csv = StringIO(decode)

        if csv:
            df = pd.read_csv(csv, sep=",")
            # convert to dictionary for easy get calls
            list_of_mappings = dict(df.values)
            #Get the current acquisition label
            acq_label = acquisition.label
            #If needed, strip the beginning sequence numbering
            split_label = acq_label.split(' - ')
            #The last entry in the list will always be the character set (what we want)
            acq_label = split_label[len(split_label) - 1]

            # now map to new label
            new_label = list_of_mappings.get(acq_label)
            if new_label:
                # update acquisition label
                acquisition.update({"label": new_label})
                log.info("Curating acquisition label: %s ---> %s", acquisition.label, new_label)
            else:
                log.info("No change in acquisition label: " + acquisition.label)
        else:
            raise ValueError("no csv file found")


if __name__ == "__main__":
    # TODO add Singularity capability

    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gtk_context:
    # with GearToolkitContext(config_path='custom-pre-curate-0.1.3-62695de675975922d1f28bd4/config.json'\
    #                         , manifest_path='custom-pre-curate-0.1.3-62695de675975922d1f28bd4/manifest.json') as gtk_context:
        gtk_context.init_logging()
        config_dictionary = gtk_context.config_json['inputs']
        config_dictionary['api-key']['key'] = 'XXX'

        parent, input_files = parser.parse_config(gtk_context)

        #create custom curator
        my_curator = Curator()

        #create walker to walk the parent level
        root_walker = walker.Walker(
            parent,
            depth_first=my_curator.config.depth_first,
            reload=my_curator.config.reload,
            stop_level=my_curator.config.stop_level,
        )

        for container in root_walker.walk():
            my_curator.curate_container(container)


