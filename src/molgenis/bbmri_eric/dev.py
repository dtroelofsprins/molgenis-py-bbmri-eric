"""
Development only module
"""

# TODO dev code in src: remove or move to /tests

from dotenv import dotenv_values

from molgenis.bbmri_eric import nodes
from molgenis.bbmri_eric.bbmri_client import BbmriSession
from molgenis.bbmri_eric.eric import Eric

config = dotenv_values(".env.local")

target = config["TARGET"]
username = config["USERNAME"]
password = config["PASSWORD"]

bbmri_session = BbmriSession(url=target)
bbmri_session.login(username, password)

eric = Eric(bbmri_session)
# eric.stage_external_nodes([nodes.get_external_node("BE")])
eric.publish_nodes([nodes.get_node("BE")])
