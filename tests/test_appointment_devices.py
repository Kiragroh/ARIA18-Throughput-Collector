"""Execute the portable device CTE itself, not a Python copy of the mapping."""
import sqlite3


def query(rows):
    from tools.build_collector_v2 import appointment_device_ctes
    with sqlite3.connect(':memory:') as db:
        db.executescript('''
          CREATE TABLE Appointment (DimActivityTransactionID,DimPatientID,DimActivityID,
            AppointmentDateTime,ctrResourceSer,DimResourceID,AppointmentResourceStatus);
          CREATE TABLE Resource (ctrResourceSer,ResourceId);
          CREATE TABLE ResourceMachine (DimResourceID,MachineId);
          CREATE TABLE Machine (MachineId);
          INSERT INTO Machine VALUES ('M1'),('M2');
          INSERT INTO Resource VALUES (1,'M1'),(2,'M2');
        ''')
        db.executemany('INSERT INTO Appointment VALUES (?,?,?,?,?,?,?)',rows)
        sql=appointment_device_ctes().replace('#','').replace("N'", "'")
        return db.execute('WITH '+sql+' SELECT DimPatientID,standalone_id,machine FROM appointment_devices ORDER BY standalone_id').fetchall()


def test_parallel_patientless_slots_keep_separate_machines():
    rows=[(1,None,10,'2025-01-02 12:00',1,None,'Open'),
          (2,None,10,'2025-01-02 12:00',2,None,'Open')]
    assert query(rows)==[(None,1,'M1'),(None,2,'M2')]


def test_patient_resource_fanout_keeps_one_clinical_appointment():
    rows=[(1,100,10,'2025-01-02 12:00',1,None,'Open'),
          (2,100,10,'2025-01-02 12:00',1,None,'Open')]
    assert query(rows)==[(100,None,'M1')]


def test_deleted_or_cancelled_resource_does_not_create_ambiguous_machine():
    rows=[(1,100,10,'2025-01-02 12:00',1,None,'Open'),
          (2,100,10,'2025-01-02 12:00',2,None,'Deleted'),
          (3,100,10,'2025-01-02 12:00',2,None,'Cancelled')]
    assert query(rows)==[(100,None,'M1')]


def test_two_current_devices_are_not_arbitrarily_resolved():
    rows=[(1,100,10,'2025-01-02 12:00',1,None,'Open'),
          (2,100,10,'2025-01-02 12:00',2,None,'Open')]
    assert query(rows)==[(100,None,'AMBIGUOUS_DEVICE')]


def test_main_export_and_inventory_share_cte_and_patientless_join_guard():
    from tools.build_collector_v2 import appointment_device_ctes, event_sql
    from tools.build_preflight_v2 import queries
    for sql in (event_sql(),queries()['AppointmentInventory'][0]):
        assert appointment_device_ctes() in sql
        assert 'standalone_id=a.DimActivityTransactionID' in sql
        assert 'COALESCE(a.DimPatientID,0)<=0' in sql


def test_cancelled_resource_fanout_cannot_hide_an_active_resource():
    import re
    from tools.build_collector_v2 import event_sql
    expression=re.search(r"COALESCE\(MIN\(CASE WHEN resource_status.*? AS resource_status",
                         event_sql(),re.S).group().replace("N'", "'")
    with sqlite3.connect(':memory:') as db:
        db.execute('CREATE TABLE states (resource_status)')
        db.executemany('INSERT INTO states VALUES (?)',[('Cancelled',),('Open',)])
        assert db.execute('SELECT '+expression+' FROM states').fetchone()[0]=='Open'
        db.execute("DELETE FROM states WHERE resource_status='Open'")
        assert db.execute('SELECT '+expression+' FROM states').fetchone()[0]=='Cancelled'
