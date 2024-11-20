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
        current_project = gtk_context.client.get(parents.project)
        contents_of_csv = current_project.read_file('acquisition_label_remapping.csv')
        # decode the UTF-8 file string
        decode = contents_of_csv.decode('utf-8')
        csv = StringIO(decode)
        # set return code
        return_code = 0

        if csv:
            df = pd.read_csv(csv, sep=",")
            # convert to dictionary for easy get calls
            list_of_mappings = dict(df.values)
            # 1. CHECK IF CURRENT LABEL IS ALREADY REPROIN COMPLIANT
            acq_label = acquisition.label
            val_list = list(list_of_mappings.values())
            try:
                reverse_exists = val_list.index(acq_label)
                log.info("Acquisition looks to be already pre-curated")
                log.info("No change in acquisition label: " + acquisition.label)
                return return_code
            except:
                # 2. Get the current acquisition label: IF FROM PL, MUST BE DICOM NAME, IF FROM SCANNER MUST BE ACQ LABEL
                for ff in acquisition.files:
                    if ff.type == 'dicom':
                        dcm_file_name = (ff.name).split('.')[0]
                temp_label = dcm_file_name

                # If needed, strip the beginning sequence numbering. Doesn't do anything if coming from scanner
                split_label = temp_label.split(' - ')

                # If this is acquisition is coming from PETA LIBRARY, make it looks as if it's coming from the scanner
                if len(split_label) > 1:
                    # this is coming from PL
                    acq_label = split_label[len(split_label) - 1]
                    # start an array with all other acq file names that came before
                    file_names = []
                    new_label = acq_label
                    session_of_interest = gtk_context.client.get(acquisition.session)
                    # loop through all dicom names and add to list
                    acquisitions = session_of_interest.acquisitions.find(sort='timestamp:asc')
                    # loop through all acquisitions except for current one, which should be at the very end of the list
                    # Change: now looping through all acquisitions including the current one to make this work when curated at a session level, not only acquisition level
                    for acq in acquisitions:
                        for ff in acq.files:
                            if ff.type == 'dicom':
                                num_name = ((ff.name).split('.')[0]).split(' - ')[1]
                                file_names.append(num_name)

                    # sum the number of times this file name already exists. This gives you the relabelling index
                    already_exists = sum(1 for i in file_names if i == new_label)
                    # set the new label based on the already exists count
                    if already_exists > 1:
                        new_label = acq_label + "_" + str(already_exists - 1)
                    # Now set the new_label to acq_label
                    acq_label = new_label

                # 3. MAP to new ReproIn label. This is the only part that should run when ingesting from scanner
                new_label = list_of_mappings.get(acq_label)
                # see if the mapping exists
                if new_label:
                    # Does acquisition name already exist?
                    session_of_interest = gtk_context.client.get(acquisition.session)
                    already_exists = session_of_interest.acquisitions.find(f'label={new_label}')
                    # set the repetition count of the file
                    rep = 0
                    # if the acquistion name already exists, append an _1, if still exists then an _2, etc, until name is unique
                    while len(already_exists) > 0:
                        # if you landed in this while loop, then there's an unexpected acquisition to address. While the code below will rename the acquisition to the correct convention, we need to check this manually, so we return an error code
                        rep += 1
                        old_label = list_of_mappings.get(acq_label)
                        new_label = old_label + "_" + str(rep)
                        already_exists = session_of_interest.acquisitions.find(f'label={new_label}')
                    # update acquisition label
                    acquisition.update({"label": new_label})
                    log.info("Curating acquisition label: %s ---> %s", acquisition.label, new_label)
                    if rep > 0:
                        # The only exception for allowing a repeated acquisition name is if we're dealing with magnitude phase field maps. For all other cases, we should return an error and user should correct duplicate scan manually
                        if 'fmap-gre_acq-siemens' in new_label:
                            log.warning("The following scan is a duplicate: %s", old_label)
                            log.warning("But it looks like this is a mag/phase fieldmap, so it's okay")
                        else:
                            log.error("The following scan is a duplicate: %s", old_label)
                            log.error("Correct scan manually before running bids-curate")
                            return_code = 1
                            sys.exit(1)
                else:
                    # see if the reverse mapping exists. This would mean session has already been curated
                    val_list = list(list_of_mappings.values())
                    try:
                        val_list.index(new_label)
                        log.info("Acquisition looks to be already pre-curated")
                        log.info("No change in acquisition label: " + acquisition.label)
                    except:
                        log.error("The following acquisition has no corresponding reproIn mapping: %s",
                                  acquisition.label)
                        log.error(
                            "Check for duplicates or incorrect naming. Correct scan manually before running bids-curate")
                        sys.exit(1)
        else:
            raise ValueError("no csv file found")
        log.info("Gear is done.  Returning %s", return_code)
        return return_code


if __name__ == "__main__":
    # TODO add Singularity capability

    # Get access to gear config, inputs, and sdk client if enabled.
    with GearToolkitContext() as gtk_context:
        # with GearToolkitContext(config_path='bids-pre-curate-0.1.5_inc2.0-65ea1cf3a6535b425969b95a/config.json'\
        #                         , manifest_path='bids-pre-curate-0.1.5_inc2.0-65ea1cf3a6535b425969b95a/manifest.json') as gtk_context:
        gtk_context.init_logging()
        config_dictionary = gtk_context.config_json['inputs']
        config_dictionary['api-key'][
            'key'] = 'XXX'

        parent, input_files = parser.parse_config(gtk_context)

        # create custom curator
        my_curator = Curator()

        # create walker to walk the parent level
        root_walker = walker.Walker(
            parent,
            depth_first=my_curator.config.depth_first,
            reload=my_curator.config.reload,
            stop_level=my_curator.config.stop_level,
        )

        for container in root_walker.walk():
            return_code = my_curator.curate_container(container)
        sys.exit(return_code)


