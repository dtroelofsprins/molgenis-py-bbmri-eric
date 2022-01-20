from unittest import mock
from unittest.mock import MagicMock

import pytest

from molgenis.bbmri_eric.model import Table, TableType
from molgenis.bbmri_eric.pid_manager import (
    NoOpPidManager,
    PidManager,
    PidManagerFactory,
)
from molgenis.bbmri_eric.pid_service import DummyPidService, NoOpPidService, Status
from molgenis.bbmri_eric.printer import Printer


@pytest.fixture
def pid_manager(pid_service, printer):
    return PidManager(pid_service, printer)


def test_assign_biobank_pids(pid_manager, pid_service):
    biobanks = Table.of(
        table_type=TableType.BIOBANKS,
        meta=MagicMock(),
        rows=[
            {"id": "b1", "name": "biobank1", "pid": "pid1"},
            {"id": "b2", "name": "biobank2"},
            {"id": "b3", "name": "biobank3"},
        ],
    )

    pid_service.reverse_lookup.side_effect = [[], ["pid3"]]

    warnings = pid_manager.assign_biobank_pids(biobanks)

    pid_service.register_pid.assert_called_with(url="url/#/biobank/b2", name="biobank2")
    assert len(warnings) == 1
    assert (
        warnings[0].message
        == "PID(s) already exist for new biobank \"biobank3\": ['pid3']. Please check "
        "the PID's contents!"
    )


def test_update_biobank_pids(pid_manager, pid_service):
    biobanks = Table.of(
        table_type=TableType.BIOBANKS,
        meta=MagicMock(),
        rows=[
            {"id": "b1", "name": "biobank1", "pid": "pid1"},
            {"id": "b2", "name": "biobank2_renamed", "pid": "pid2"},
        ],
    )

    existing_biobanks = Table.of(
        table_type=TableType.BIOBANKS,
        meta=MagicMock(),
        rows=[
            {"id": "b1", "name": "biobank1", "pid": "pid1"},
            {"id": "b2", "name": "biobank2", "pid": "pid2"},
        ],
    )

    pid_manager.update_biobank_pids(biobanks, existing_biobanks)

    pid_service.set_name.assert_called_with("pid2", "biobank2_renamed")


def test_terminate_biobanks(pid_manager, pid_service):
    pid_manager.terminate_biobanks(["pid1", "pid2"])
    assert pid_service.set_status.mock_calls == [
        mock.call("pid1", Status.TERMINATED),
        mock.call("pid2", Status.TERMINATED),
    ]


def test_noop_pid_manager():
    noop = NoOpPidManager()

    assert noop.assign_biobank_pids(MagicMock()) == []
    assert noop.update_biobank_pids(MagicMock(), MagicMock()) is None
    assert noop.terminate_biobanks(MagicMock()) is None


def test_pid_manager_factory():
    noop_pid_service = NoOpPidService()
    dummy_pid_service = DummyPidService()
    printer = Printer()

    manager1 = PidManagerFactory.create(noop_pid_service, printer)
    manager2 = PidManagerFactory.create(dummy_pid_service, printer)

    assert type(manager1) == NoOpPidManager
    assert type(manager2) == PidManager
